from setuptools import  setup,find_packages
import os
here = os.path.abspath(os.path.dirname(__file__))  
setup(
    name='siem_hkm_ai_smartcore',
    packages=find_packages(),
    install_requires=[
        "pandas" , "BAC0","opcua"
    ],
    version='0.1.3',
    description="A Python library for intelligent building management with BACnet/OPC UA communication and HVAC optimization",
    long_description = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md") , "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="lanzco's team",
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # 替换为你的许可证
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Home Automation",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)


