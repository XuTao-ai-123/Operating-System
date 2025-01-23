import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from banker import is_safe_state

class BankerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("银行家算法模拟器")
        
        # 设置窗口大小和位置
        window_width = 480  # 减小窗口宽度
        window_height = 400  # 减小窗口高度
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 设置默认进程数和资源类型数
        self.n_processes = 5
        self.n_resources = 3
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure('Title.TLabel', font=('Microsoft YaHei UI', 16, 'bold'))
        self.style.configure('Matrix.TLabel', font=('Microsoft YaHei UI', 10))
        self.style.configure('Matrix.TEntry', font=('Consolas', 10))
        
        self.create_widgets()
        self.load_from_file("banker_data.txt")

    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 标题
        title_label = ttk.Label(main_frame, text="银行家算法模拟系统", style='Title.TLabel')
        title_label.pack(pady=(5,10))
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", padx=5)
        
        # 左侧按钮
        ttk.Button(button_frame, text="添加进程", command=self.add_process, width=10).pack(side="left", padx=2)
        ttk.Button(button_frame, text="删除进程", command=self.delete_process, width=10).pack(side="left", padx=2)
        
        # 右侧按钮
        ttk.Button(button_frame, text="加载数据", command=lambda: self.load_from_file(), width=10).pack(side="right", padx=2)
        ttk.Button(button_frame, text="保存数据", command=self.save_to_file, width=10).pack(side="right", padx=2)
        
        # 矩阵区域
        matrices_frame = ttk.Frame(main_frame)
        matrices_frame.pack(fill="both", expand=True, pady=10)
        
        # 最大需求矩阵
        max_frame = ttk.LabelFrame(matrices_frame, text="最大需求矩阵", padding=(5,5,5,5))
        max_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        # 分配矩阵
        alloc_frame = ttk.LabelFrame(matrices_frame, text="分配矩阵", padding=(5,5,5,5))
        alloc_frame.pack(side="right", fill="both", expand=True, padx=5)
        
        # 创建矩阵输入框
        self.max_entries = self.create_matrix(max_frame)
        self.allocation_entries = self.create_matrix(alloc_frame)
        
        # 可用资源区域
        available_frame = ttk.LabelFrame(main_frame, text="可用资源", padding=(5,5,5,5))
        available_frame.pack(fill="x", padx=5, pady=5)
        
        self.available_entries = []
        for j in range(self.n_resources):
            ttk.Label(available_frame, text=chr(65+j), style='Matrix.TLabel').grid(row=0, column=j*2, padx=5)
            entry = ttk.Entry(available_frame, width=5, justify='center', style='Matrix.TEntry')
            entry.grid(row=0, column=j*2+1, padx=5, pady=5)
            self.available_entries.append(entry)
        
        # 检查按钮
        ttk.Button(main_frame, text="检查安全状态", command=self.check_safety, width=15).pack(pady=5)
        
        # 结果显示
        self.result_text = tk.Text(main_frame, height=3, width=40, font=('Microsoft YaHei UI', 10))
        self.result_text.pack(pady=5)

    def create_matrix(self, parent):
        entries = []
        # 添加资源标签 (A, B, C)
        for j in range(self.n_resources):
            ttk.Label(parent, text=chr(65+j), style='Matrix.TLabel').grid(row=0, column=j+1, padx=5)
        
        # 添加进程标签和输入框
        for i in range(self.n_processes):
            ttk.Label(parent, text=f"P{i}", style='Matrix.TLabel').grid(row=i+1, column=0, padx=5)
            row_entries = []
            for j in range(self.n_resources):
                entry = ttk.Entry(parent, width=5, justify='center', style='Matrix.TEntry')
                entry.grid(row=i+1, column=j+1, padx=5, pady=2)
                row_entries.append(entry)
            entries.append(row_entries)
        return entries

    def add_process(self):
        """添加一个新进程"""
        self.n_processes += 1
        # 保存当前数据
        max_data = self.get_matrix_data(self.max_entries)
        alloc_data = self.get_matrix_data(self.allocation_entries)
        avail_data = self.get_available_data()
        
        # 重新创建整个界面
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_widgets()
        
        # 恢复原有数据
        if max_data and alloc_data and avail_data:
            # 填充原有进程的数据
            for i in range(len(max_data)):
                for j in range(self.n_resources):
                    self.max_entries[i][j].insert(0, str(max_data[i][j]))
                    self.allocation_entries[i][j].insert(0, str(alloc_data[i][j]))
            
            # 新进程的数据初始化为0
            for j in range(self.n_resources):
                self.max_entries[-1][j].insert(0, "0")
                self.allocation_entries[-1][j].insert(0, "0")
            
            # 恢复可用资源数据
            for j in range(self.n_resources):
                self.available_entries[j].insert(0, str(avail_data[j]))

    def delete_process(self):
        """删除最后一个进程"""
        if self.n_processes > 1:
            # 保存当前数据（除了最后一个进程）
            max_data = self.get_matrix_data(self.max_entries[:-1])
            alloc_data = self.get_matrix_data(self.allocation_entries[:-1])
            avail_data = self.get_available_data()
            
            self.n_processes -= 1
            # 重新创建整个界面
            for widget in self.root.winfo_children():
                widget.destroy()
            self.create_widgets()
            
            # 恢复数据
            if max_data and alloc_data and avail_data:
                for i in range(self.n_processes):
                    for j in range(self.n_resources):
                        self.max_entries[i][j].insert(0, str(max_data[i][j]))
                        self.allocation_entries[i][j].insert(0, str(alloc_data[i][j]))
                
                for j in range(self.n_resources):
                    self.available_entries[j].insert(0, str(avail_data[j]))
        else:
            messagebox.showwarning("警告", "至少需要保留一个进程！")

    def clear_all_entries(self):
        """清空所有输入框"""
        for matrix in [self.max_entries, self.allocation_entries]:
            for row in matrix:
                for entry in row:
                    entry.delete(0, tk.END)
        
        for entry in self.available_entries:
            entry.delete(0, tk.END)

    def load_from_file(self, filename=None):
        """从文件加载数据"""
        if filename is None:
            filename = filedialog.askopenfilename(
                title="选择数据文件",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
        if not filename:
            return
            
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                lines = [line.strip() for line in file if line.strip() and not line.startswith('#')]
                
                # 读取进程数和资源数
                n_proc, n_res = map(int, lines[0].split())
                if n_proc != self.n_processes or n_res != self.n_resources:
                    self.n_processes = n_proc
                    self.n_resources = n_res
                    # 重新创建整个界面
                    for widget in self.root.winfo_children():
                        widget.destroy()
                    self.create_widgets()
                
                # 清空现有数据
                self.clear_all_entries()
                
                # 读取最大需求矩阵
                current_line = 1
                for i in range(self.n_processes):
                    if current_line + i >= len(lines):
                        break
                    values = lines[current_line + i].split()
                    for j in range(min(self.n_resources, len(values))):
                        self.max_entries[i][j].insert(0, values[j])
                
                # 读取分配矩阵
                current_line += self.n_processes
                for i in range(self.n_processes):
                    if current_line + i >= len(lines):
                        break
                    values = lines[current_line + i].split()
                    for j in range(min(self.n_resources, len(values))):
                        self.allocation_entries[i][j].insert(0, values[j])
                
                # 读取可用资源
                current_line += self.n_processes
                if current_line < len(lines):
                    values = lines[current_line].split()
                    for j in range(min(self.n_resources, len(values))):
                        self.available_entries[j].insert(0, values[j])
                
        except Exception as e:
            messagebox.showerror("错误", f"加载文件时出错：{str(e)}")

    def save_to_file(self):
        """保存数据到文件"""
        filename = filedialog.asksaveasfilename(
            title="保存数据文件",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not filename:
            return
            
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                # 写入进程数和资源数
                file.write(f"# 进程数 资源类型数\n{self.n_processes} {self.n_resources}\n\n")
                
                # 写入最大需求矩阵
                file.write("# 最大需求矩阵 (Max)\n")
                for row in self.max_entries:
                    values = [entry.get() for entry in row]
                    file.write(" ".join(values) + "\n")
                file.write("\n")
                
                # 写入分配矩阵
                file.write("# 当前分配矩阵 (Allocation)\n")
                for row in self.allocation_entries:
                    values = [entry.get() for entry in row]
                    file.write(" ".join(values) + "\n")
                file.write("\n")
                
                # 写入可用资源
                file.write("# 可用资源 (Available)\n")
                values = [entry.get() for entry in self.available_entries]
                file.write(" ".join(values) + "\n")
                
                messagebox.showinfo("成功", "数据保存成功！")
                
        except Exception as e:
            messagebox.showerror("错误", f"保存文件时出错：{str(e)}")

    def get_matrix_data(self, entries):
        matrix = []
        for row in entries:
            matrix_row = []
            for entry in row:
                try:
                    value = int(entry.get())
                    matrix_row.append(value)
                except ValueError:
                    messagebox.showerror("错误", "请输入有效的数字！")
                    return None
            matrix.append(matrix_row)
        return matrix

    def get_available_data(self):
        available = []
        for entry in self.available_entries:
            try:
                value = int(entry.get())
                available.append(value)
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字！")
                return None
        return available

    def check_safety(self):
        max_matrix = self.get_matrix_data(self.max_entries)
        allocation_matrix = self.get_matrix_data(self.allocation_entries)
        available = self.get_available_data()
        
        if None in (max_matrix, allocation_matrix, available):
            return
            
        processes = list(range(self.n_processes))
        is_safe, sequence = is_safe_state(processes, available, max_matrix, allocation_matrix)
        
        self.result_text.delete(1.0, tk.END)
        if is_safe:
            sequence_str = ' -> '.join(f'P{i}' for i in sequence)
            self.result_text.insert(tk.END, f"系统处于安全状态\n安全序列为：\n{sequence_str}")
        else:
            self.result_text.insert(tk.END, "系统处于不安全状态\n没有安全序列！")

if __name__ == "__main__":
    root = tk.Tk()
    app = BankerGUI(root)
    root.mainloop() 