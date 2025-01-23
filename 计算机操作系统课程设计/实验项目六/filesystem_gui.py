import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import simpledialog
from typing import Optional

class FileNode:
    def __init__(self, name: str, is_directory: bool = False):
        self.name = name
        self.is_directory = is_directory
        self.content = ""
        self.children = {}
        self.parent = None

class FileSystem:
    def __init__(self):
        self.root = FileNode("/", True)
        self.current_dir = self.root

    def create_node(self, name: str, is_directory: bool, parent: FileNode) -> Optional[FileNode]:
        # 检查是否存在同名节点（不管是文件还是目录）
        if name in parent.children:
            messagebox.showerror("错误", f"错误：目录 {parent.name} 下已存在名为 {name} 的文件或目录")
            return None
        
        # 创建新节点
        node = FileNode(name, is_directory)
        node.parent = parent
        parent.children[name] = node
        return node

    def write_file(self, file_node: FileNode, content: str) -> bool:
        if file_node.is_directory:
            messagebox.showerror("错误", "错误：目标不是文件")
            return False
        file_node.content = content
        return True

    def read_file(self, file_node: FileNode) -> Optional[str]:
        if file_node.is_directory:
            messagebox.showerror("错误", "错误：目标不是文件")
            return None
        return file_node.content

    def delete_node(self, node: FileNode) -> bool:
        if node == self.root:
            messagebox.showerror("错误", "不能删除根目录")
            return False
            
        if node.is_directory and node.children:
            if not messagebox.askyesno("确认", "该目录不为空，确定要删除吗？"):
                return False
                
        if node.parent:
            del node.parent.children[node.name]
        return True

class FileSystemGUI:
    def __init__(self):
        self.fs = FileSystem()
        
        self.window = tk.Tk()
        self.window.title("文件系统模拟器")
        self.window.geometry("800x600")

        # 创建左右分栏
        self.paned = ttk.PanedWindow(self.window, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # 左侧文件树
        self.tree_frame = ttk.Frame(self.paned)
        self.tree = ttk.Treeview(self.tree_frame)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.paned.add(self.tree_frame)

        # 右侧操作区
        self.operation_frame = ttk.Frame(self.paned)
        self.paned.add(self.operation_frame)

        # 操作按钮
        ttk.Button(self.operation_frame, text="创建目录", 
                  command=self.create_directory).pack(pady=5)
        ttk.Button(self.operation_frame, text="创建文件", 
                  command=self.create_file).pack(pady=5)
        ttk.Button(self.operation_frame, text="删除", 
                  command=self.delete_node).pack(pady=5)
        ttk.Button(self.operation_frame, text="写入文件", 
                  command=self.write_to_file).pack(pady=5)
        ttk.Button(self.operation_frame, text="读取文件", 
                  command=self.read_file).pack(pady=5)

        # 添加状态栏
        self.status_bar = ttk.Label(self.window, text="当前位置: /", anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 绑定选择事件
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        # 初始化文件树
        self.refresh_tree()
        
    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        self._add_node_to_tree("", self.fs.root)

    def _add_node_to_tree(self, parent_id, node: FileNode):
        node_type = "📁" if node.is_directory else "📄"
        node_id = self.tree.insert(parent_id, "end", text=f"{node_type} {node.name}")
        
        for child in node.children.values():
            self._add_node_to_tree(node_id, child)

    def get_selected_node(self) -> Optional[FileNode]:
        selection = self.tree.selection()
        if not selection:
            return None  # 如果没有选中节点，返回None
        
        # 获取从根到当前节点的路径
        path = []
        current_item = selection[0]
        while current_item:
            item_text = self.tree.item(current_item)["text"]
            name = item_text.split(" ")[1]  # 去掉图标，只保留名称
            path.insert(0, name)
            current_item = self.tree.parent(current_item)
        
        # 从根节点开始查找目标节点
        current = self.fs.root
        for name in path[1:]:  # 跳过根目录名称
            if name in current.children:
                current = current.children[name]
            else:
                return None
        
        return current

    def _find_tree_item(self, target_node, parent_item=""):
        """查找节点对应的树形项目ID"""
        # 检查当前项目
        item_text = self.tree.item(parent_item)["text"] if parent_item else ""
        if item_text:
            name = item_text.split(" ")[1]
            if name == target_node.name:
                return parent_item
        
        # 递归检查子项目
        for child in self.tree.get_children(parent_item):
            item_text = self.tree.item(child)["text"]
            name = item_text.split(" ")[1]
            if name == target_node.name:
                return child
            result = self._find_tree_item(target_node, child)
            if result:
                return result
        return None

    def create_directory(self):
        parent = self.get_selected_node()
        if not parent or not parent.is_directory:
            messagebox.showerror("错误", "请选择一个目录")
            return
        
        name = simpledialog.askstring("创建目录", "请输入目录名：")
        if name:
            new_node = self.fs.create_node(name, True, parent)
            if new_node:
                self.refresh_tree()
                # 展开到父节点
                parent_item = self._find_tree_item(parent)
                if parent_item:
                    self.tree.item(parent_item, open=True)
                    # 查找并选中新创建的节点
                    for child in self.tree.get_children(parent_item):
                        item_text = self.tree.item(child)["text"]
                        if item_text.split(" ")[1] == name:
                            self.tree.selection_set(child)
                            self.tree.see(child)
                            break

    def create_file(self):
        parent = self.get_selected_node()
        if not parent or not parent.is_directory:
            messagebox.showerror("错误", "请选择一个目录")
            return
        
        name = simpledialog.askstring("创建文件", "请输入文件名：")
        if name:
            new_node = self.fs.create_node(name, False, parent)
            if new_node:
                self.refresh_tree()
                # 展开到父节点
                parent_item = self._find_tree_item(parent)
                if parent_item:
                    self.tree.item(parent_item, open=True)
                    # 查找并选中新创建的节点
                    for child in self.tree.get_children(parent_item):
                        item_text = self.tree.item(child)["text"]
                        if item_text.split(" ")[1] == name:
                            self.tree.selection_set(child)
                            self.tree.see(child)
                            break

    def write_to_file(self):
        node = self.get_selected_node()
        if not node or node.is_directory:
            messagebox.showerror("错误", "请选择一个文件")
            return
        
        # 创建写入文件的对话框
        dialog = tk.Toplevel(self.window)
        dialog.title(f"写入文件 - {node.name}")
        dialog.geometry("400x300")
        
        # 创建文本框
        text_area = tk.Text(dialog, height=10)
        text_area.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
        
        # 如果文件已有内容，显示在文本框中
        if node.content:
            text_area.insert("1.0", node.content)
        
        # 创建按钮框架
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=5, padx=5)
        
        def save_content():
            content = text_area.get("1.0", tk.END).strip()
            if self.fs.write_file(node, content):
                messagebox.showinfo("成功", "文件写入成功")
                dialog.destroy()
        
        # 添加保存和取消按钮
        ttk.Button(button_frame, text="保存", command=save_content).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT)
        
        # 使对话框成为模态窗口
        dialog.transient(self.window)
        dialog.grab_set()
        self.window.wait_window(dialog)

    def read_file(self):
        node = self.get_selected_node()
        if not node or node.is_directory:
            messagebox.showerror("错误", "请选择一个文件")
            return
        
        content = self.fs.read_file(node)
        if content is not None:
            # 创建读取文件的对话框
            dialog = tk.Toplevel(self.window)
            dialog.title(f"读取文件 - {node.name}")
            dialog.geometry("400x300")
            
            # 创建只读文本框
            text_area = tk.Text(dialog, height=10)
            text_area.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
            text_area.insert("1.0", content)
            text_area.config(state='disabled')  # 设置为只读
            
            # 添加关闭按钮
            ttk.Button(dialog, text="关闭", command=dialog.destroy).pack(pady=5)
            
            # 使对话框成为模态窗口
            dialog.transient(self.window)
            dialog.grab_set()
            self.window.wait_window(dialog)

    def on_select(self, event):
        """当选择节点改变时更新状态栏"""
        node = self.get_selected_node()
        if node:
            path = []
            current = node
            while current:
                path.append(current.name)
                current = current.parent
            full_path = '/'.join(reversed(path)) or '/'
            self.status_bar.config(text=f"当前位置: {full_path}")

    def delete_node(self):
        """删除选中的文件或目录"""
        node = self.get_selected_node()
        if not node:
            messagebox.showerror("错误", "请选择要删除的文件或目录")
            return
            
        if node == self.fs.root:
            messagebox.showerror("错误", "不能删除根目录")
            return
            
        # 确认删除
        type_str = "目录" if node.is_directory else "文件"
        if not messagebox.askyesno("确认", f"确定要删除{type_str} {node.name} 吗？"):
            return
            
        if self.fs.delete_node(node):
            self.refresh_tree()
            messagebox.showinfo("成功", f"{type_str}已删除")

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = FileSystemGUI()
    app.run() 