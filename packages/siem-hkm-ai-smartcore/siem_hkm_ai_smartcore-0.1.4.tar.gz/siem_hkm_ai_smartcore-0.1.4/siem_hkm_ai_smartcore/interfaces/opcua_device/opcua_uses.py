from dataclasses import dataclass, field
from typing import Dict, List
from opcua import Client
from opcua.ua import Variant, VariantType

class OPCUADeviceManager:
    def __init__(self):
        """Initialize OPC UA device manager"""
        self.clients = {}  # Store client connections, key is server URL
        self.connected_servers = {}  # Record server connection status
        
    def connect(self, server_url: str) -> bool:
        """
        Connect to OPC UA server
        
        Args:
            server_url: OPC UA server address in format like "opc.tcp://server_A:4840"
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Disconnect first if connection to this server already exists
            if server_url in self.clients:
                self.disconnect(server_url)
                
            # Create new client and connect
            client = Client(server_url)
            client.connect()
            self.clients[server_url] = client
            self.connected_servers[server_url] = True
            print(f"Successfully connected to OPC UA server: {server_url}")
            return True
        except Exception as e:
            print(f"Failed to connect to OPC UA server {server_url}: {str(e)}")
            self.connected_servers[server_url] = False
            return False
    
    def disconnect(self, server_url: str) -> None:
        """
        Disconnect from specified OPC UA server
        
        Args:
            server_url: Address of the server to disconnect from
        """
        if server_url in self.clients:
            try:
                self.clients[server_url].disconnect()
                print(f"Disconnected from OPC UA server: {server_url}")
            except Exception as e:
                print(f"Error occurred while disconnecting {server_url}: {str(e)}")
            finally:
                self.connected_servers[server_url] = False
                del self.clients[server_url]
                
    def disconnect_all(self) -> None:
        """Disconnect all connected OPC UA servers"""
        for server_url in list(self.clients.keys()):
            self.disconnect(server_url)
        print("Disconnected from all OPC UA servers")
    
    def get_node_value(self, server_url: str, node_ns: int, node_name: str):
        """
        Read value of specified node on specified server
        
        Args:
            server_url: OPC UA server address
            node_ns: Node namespace
            node_name: Node name
            node is actually:  "ns={node_ns};s={node_id}"
            
        Returns:
            Node value, None if error occurs
        """
        node_id = f"ns={node_ns};s={node_id}"
        if server_url not in self.clients or not self.connected_servers[server_url]:
            print(f"Not connected to server {server_url}, please connect first")
            return None
            
        try:
            client = self.clients[server_url]
            node = client.get_node(node_id)
            value = node.get_value()
            print(f"Read value from server {server_url} node {node_id}: {value}")
            return value
        except Exception as e:
            print(f"Failed to read node value {server_url} {node_id}: {str(e)}")
            return None
    
    def set_node_value(self, server_url: str, node_ns: int ,node_name: str, value, variant_type: VariantType = None) -> bool:
        """
        Set value of specified node on specified server
        
        Args:
            server_url: OPC UA server address
            node_ns: Node namespace
            node_id: Node name
            node is actually:  "ns={node_ns};s={node_id}"
            value: Value to set
            variant_type: Variable type, automatically inferred if None
            
        Returns:
            True if setting successful, False otherwise
        """
        node_id = f"ns={node_ns};s={node_id}"
        if server_url not in self.clients or not self.connected_servers[server_url]:
            print(f"Not connected to server {server_url}, please connect first")
            return False
            
        try:
            client = self.clients[server_url]
            node = client.get_node(node_id)
            
            # Create Variant automatically if type not specified
            if variant_type:
                variant = Variant(value, variant_type)
                node.set_value(variant)
            else:
                node.set_value(value)
                
            print(f"Set value of server {server_url} node {node_id} to: {value}")
            return True
        except Exception as e:
            print(f"Failed to set node value {server_url} {node_id}: {str(e)}")
            return False
    
    def set_multiple_nodes(self, server_url: str, node_values: Dict[str, tuple]) -> Dict[str, bool]:
        """
        Batch set values for multiple nodes
        
        Args:
            server_url: OPC UA server address
            node_values: Dictionary with node IDs as keys and tuples of (value, type) as values
            
        Returns:
            Dictionary of setting results for each node
        """
        results = {}
        for (node_ns,node_name), (value, variant_type) in node_values.items():
            node_id = f"ns={node_ns};s={node_id}"
            result = self.set_node_value(server_url, node_id, value, variant_type)
            results[node_id] = result
        return results
    
    def get_server_info(self, server_url: str):
        """Get server information"""
        if server_url not in self.clients or not self.connected_servers[server_url]:
            print(f"Not connected to server {server_url}, please connect first")
            return None
            
        try:
            client = self.clients[server_url]
            server = client.get_server_node()
            
            return {
                "server_name": server.read_display_name(),
                "server_uri": server.read_node_id(),
                "product_uri": server.get_child(["0:ProductUri"]).read_value(),
                "application_name": server.get_child(["0:ApplicationName"]).read_value(),
                "application_uri": server.get_child(["0:ApplicationUri"]).read_value(),
            }
        except Exception as e:
            print(f"Failed to get server information {server_url}: {str(e)}")
            return None