# 从子模块导入核心类/函数，对外暴露简洁的 API
from .core.ahu_optimizer.ahu_optimizer import Ahu_Optimizor
from .interfaces.bacnet_comm.bacnet_device import BAC0DeviceManager
from .interfaces.opcua_device.opcua_uses import OPCUADeviceManager

# 定义包的版本号（与 setup.py 一致）
__version__ = "0.1.3"

# 包的简短描述
__description__ = "bacnet/opcua communication and hvac optimization"

# 可选：限制 from siem_hkm_ai_smartcore import * 时导入的内容
__all__ = [
    "Ahu_Optimizor",
    "BAC0DeviceManager",
    "OPCUADeviceManager",
    "__version__"
]