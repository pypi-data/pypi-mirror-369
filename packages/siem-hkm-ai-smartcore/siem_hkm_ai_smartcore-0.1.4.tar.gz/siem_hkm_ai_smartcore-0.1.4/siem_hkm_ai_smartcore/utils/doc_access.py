import os
import platform
import subprocess
from pathlib import Path

class DocAccessor:
    """文档访问工具，用于打开本地docs文件夹中的文档"""
    
    def __init__(self):
        # 定位项目根目录下的docs文件夹（根据实际结构调整相对路径）
        # 原理：从当前文件（doc_access.py）向上查找，直到找到docs文件夹
        self.utils_dir = Path(__file__).parent  # utils/ 目录
        self.package_root = self.utils_dir.parent  # siem_hkm_ai_smartcore/ 目录
        self.project_root = self.package_root.parent  # 项目根目录
        self.docs_root = self.project_root / "docs"  # 本地docs文件夹路径
        
        # 检查docs文件夹是否存在
        if not self.docs_root.exists():
            print(2222)
            raise FileNotFoundError(
                f"未找到本地文档文件夹！预期路径：{self.docs_root}\n"
                "请确认项目根目录下存在docs文件夹，或修改DocAccessor中的路径配置。"
            )
        else:
            print(f"文档文件夹已定位：{self.docs_root}")

    def open(self, module_name: str = None, filename: str = None):
        """
        打开指定模块或文件的文档（二选一，优先用filename）
        
        参数:
            module_name: 模块名（如"bacnet"、"ahu_optimizer"），自动匹配docs/[module_name].md
            filename: 文档文件名（如"custom_doc.md"），直接打开docs/[filename]
        示例:
            open(module_name="bacnet") → 打开docs/bacnet.md
            open(filename="opcua.md") → 打开docs/opcua.md
        """
        # 确定文档路径
        if filename:
            doc_path = self.docs_root / filename
        elif module_name:
            # 自动拼接模块名+md后缀
            doc_path = self.docs_root / f"{module_name}.md"
        else:
            raise ValueError("请指定module_name或filename（如open(module_name='bacnet')）")
        
        # 检查文档是否存在
        if not doc_path.exists():
            existing_docs = [f.name for f in self.docs_root.glob("*.md")]
            raise FileNotFoundError(
                f"文档不存在：{doc_path}\n"
                f"当前docs文件夹中的文档：{existing_docs}"
            )
        
        # 用系统默认程序打开
        try:
            path_str = str(doc_path.resolve())
            if platform.system() == "Windows":
                os.startfile(path_str)
            elif platform.system() == "Darwin":
                subprocess.run(["open", path_str], check=True)
            else:
                subprocess.run(["xdg-open", path_str], check=True)
            print(f"已打开文档：{path_str}")
        except Exception as e:
            raise RuntimeError(f"打开失败：{e}")
        

# 全局实例，方便直接导入
doc_accessor = DocAccessor()
