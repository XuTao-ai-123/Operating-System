import tkinter as tk
from tkinter import ttk, messagebox
from memory_manager import MemoryPartition

class MemoryManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("内存分配管理系统")
        
        self.total_memory = tk.IntVar(value=10000)
        self.partitions = {}
        self.partition_var = tk.StringVar()
        
        self.create_widgets()
        
    def create_widgets(self):
        # 创建左右分栏
        left_frame = ttk.Frame(self.root)
        left_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=10, pady=10)
        
        right_frame = ttk.Frame(self.root)
        right_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=10, pady=10)
        
        # 左侧控制面板
        # 总内存设置
        memory_frame = ttk.LabelFrame(left_frame, text="总内存设置")
        memory_frame.pack(pady=5, fill="x")
        
        ttk.Label(memory_frame, text="总内存大小(KB):").pack(side=tk.LEFT, padx=5)
        ttk.Entry(memory_frame, textvariable=self.total_memory, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(memory_frame, text="设置总内存", 
                  command=self.set_total_memory).pack(side=tk.LEFT, padx=5)
        
        # 分区管理
        partition_frame = ttk.LabelFrame(left_frame, text="分区管理")
        partition_frame.pack(pady=5, fill="x")
        
        # 分区添加控件
        add_frame = ttk.Frame(partition_frame)
        add_frame.pack(fill="x", padx=5, pady=5)
        
        self.partition_name = tk.StringVar()
        self.partition_size = tk.IntVar()
        
        ttk.Label(add_frame, text="分区名称:").pack(side=tk.LEFT)
        ttk.Entry(add_frame, textvariable=self.partition_name, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Label(add_frame, text="大小(KB):").pack(side=tk.LEFT)
        ttk.Entry(add_frame, textvariable=self.partition_size, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(add_frame, text="添加分区", 
                  command=self.add_partition).pack(side=tk.LEFT, padx=5)
        ttk.Button(add_frame, text="删除选中分区", 
                  command=self.remove_partition).pack(side=tk.LEFT, padx=5)
        
        # 分区列表
        self.partition_list = ttk.Frame(partition_frame)
        self.partition_list.pack(fill="x", padx=5, pady=5)
        
        # 算法选择
        algorithm_frame = ttk.LabelFrame(left_frame, text="算法选择")
        algorithm_frame.pack(pady=5, fill="x")
        
        self.algorithm_var = tk.StringVar(value='first_fit')
        algorithms = [
            ('首次适应算法', 'first_fit'),
            ('循环首次适应算法', 'next_fit'),
            ('最佳适应算法', 'best_fit')
        ]
        
        for text, value in algorithms:
            ttk.Radiobutton(algorithm_frame, text=text, 
                           variable=self.algorithm_var, value=value).pack(side=tk.LEFT, padx=10)
        
        # 作业管理
        job_frame = ttk.LabelFrame(left_frame, text="作业管理")
        job_frame.pack(pady=5, fill="x")
        
        self.job_id = tk.IntVar()
        self.job_size = tk.IntVar()
        
        ttk.Label(job_frame, text="作业ID:").pack(side=tk.LEFT)
        ttk.Entry(job_frame, textvariable=self.job_id, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Label(job_frame, text="大小(KB):").pack(side=tk.LEFT)
        ttk.Entry(job_frame, textvariable=self.job_size, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(job_frame, text="分配作业", 
                  command=self.allocate_single_job).pack(side=tk.LEFT, padx=5)
        ttk.Button(job_frame, text="释放作业", 
                  command=self.free_single_job).pack(side=tk.LEFT, padx=5)
        
        # 示例操作
        example_frame = ttk.LabelFrame(left_frame, text="示例操作")
        example_frame.pack(pady=5, fill="x")
        
        ttk.Button(example_frame, text="分配示例作业(50,100,150,200)", 
                  command=self.allocate_example_jobs).pack(side=tk.LEFT, padx=5)
        ttk.Button(example_frame, text="释放作业4(200KB)", 
                  command=lambda: self.free_job(4)).pack(side=tk.LEFT, padx=5)
        ttk.Button(example_frame, text="释放作业1(50KB)", 
                  command=lambda: self.free_job(1)).pack(side=tk.LEFT, padx=5)
        ttk.Button(example_frame, text="释放作业2(100KB)", 
                  command=lambda: self.free_job(2)).pack(side=tk.LEFT, padx=5)
        
        # 右侧显示面板
        # 状态显示
        status_frame = ttk.LabelFrame(right_frame, text="内存状态")
        status_frame.pack(pady=5, fill="both", expand=True)
        
        self.canvas = tk.Canvas(status_frame, width=800, height=200, bg='white')
        self.canvas.pack(pady=5, padx=5)
        
        # 操作日志
        text_frame = ttk.LabelFrame(right_frame, text="操作日志")
        text_frame.pack(pady=5, fill="both", expand=True)
        
        self.text_area = tk.Text(text_frame, height=15, width=50)
        self.text_area.pack(pady=5, padx=5, fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_area.yview)
        scrollbar.pack(side="right", fill="y")
        self.text_area.configure(yscrollcommand=scrollbar.set)
        
    def add_partition(self):
        name = self.partition_name.get().strip()
        size = self.partition_size.get()
        
        if not name:
            messagebox.showerror("错误", "请输入分区名称")
            return
            
        if size <= 0:
            messagebox.showerror("错误", "分区大小必须大于0")
            return
            
        total_allocated = sum(p.size for p in self.partitions.values())
        if total_allocated + size > self.total_memory.get():
            messagebox.showerror("错误", "分区总大小超过总内存")
            return
            
        if name in self.partitions:
            messagebox.showerror("错误", "分区名称已存在")
            return
            
        self.partitions[name] = MemoryPartition(size, name)
        self.update_partition_list()
        self.partition_name.set("")
        self.partition_size.set(0)
        
    def remove_partition(self):
        selected = self.partition_var.get()
        if selected in self.partitions:
            del self.partitions[selected]
            self.update_partition_list()
            if self.partitions:
                self.partition_var.set(list(self.partitions.keys())[0])
            self.draw_memory_state()
            
    def update_partition_list(self):
        # 清除现有的分区列表
        for widget in self.partition_list.winfo_children():
            widget.destroy()
            
        # 重新创建分区列表
        for name, partition in self.partitions.items():
            ttk.Radiobutton(self.partition_list, 
                           text=f"分区 {name} ({partition.size}KB)", 
                           variable=self.partition_var,
                           value=name,
                           command=self.draw_memory_state).pack(side=tk.LEFT, padx=5)
                           
        self.draw_memory_state()
        
    def draw_memory_state(self):
        self.canvas.delete("all")
        
        if not self.partitions:
            self.canvas.create_text(400, 200, text="请先添加分区", font=('Arial', 14))
            return
        
        # 绘制标题
        self.canvas.create_text(400, 20, 
                              text=f"总内存大小: {self.total_memory.get()}KB", 
                              font=('Arial', 12, 'bold'))
        
        # 绘制内���使用情况
        x = 50
        y = 50
        block_height = 60
        total_width = 700
        
        # 计算每个分区的起始位置
        current_addr = 0
        for name, partition in self.partitions.items():
            # 绘制分区标题
            partition_width = (partition.size / self.total_memory.get()) * total_width
            self.canvas.create_text(x + partition_width/2, y - 15, 
                                  text=f"分区 {name} ({partition.size}KB)")
            
            # 绘制分区边界
            self.canvas.create_rectangle(x, y, x + partition_width, y + block_height, 
                                      outline='blue', width=2)
            
            # 绘制分区内的内存块
            block_x = x
            for block in partition.blocks:
                width = (block.size / self.total_memory.get()) * total_width
                
                color = '#90EE90' if block.is_free else '#FFB6C1'
                self.canvas.create_rectangle(block_x, y, block_x + width, y + block_height, 
                                          fill=color, outline='black')
                
                text = f"空闲\n{block.size}KB" if block.is_free else f"作业{block.job_id}\n{block.size}KB"
                self.canvas.create_text(block_x + width/2, y + block_height/2, text=text)
                
                # 显示地址范围
                self.canvas.create_text(block_x + width/2, y + block_height + 15, 
                                      text=f"地址: {current_addr}-{current_addr + block.size - 1}")
                
                block_x += width
                current_addr += block.size
            
            x += partition_width
        
        # 绘制剩余未分配空间
        remaining_size = self.total_memory.get() - sum(p.size for p in self.partitions.values())
        if remaining_size > 0:
            width = (remaining_size / self.total_memory.get()) * total_width
            self.canvas.create_rectangle(x, y, x + width, y + block_height, 
                                      fill='#D3D3D3', outline='black')
            self.canvas.create_text(x + width/2, y + block_height/2, 
                                  text=f"未分配空间\n{remaining_size}KB")
            self.canvas.create_text(x + width/2, y + block_height + 15, 
                                  text=f"地址: {current_addr}-{self.total_memory.get()-1}")
        
    def allocate_single_job(self):
        if not self.partitions:
            messagebox.showerror("错误", "请先创建分区")
            return
            
        job_id = self.job_id.get()
        job_size = self.job_size.get()
        
        if job_id <= 0 or job_size <= 0:
            messagebox.showerror("错误", "请输入有效的作业ID和大小")
            return
            
        partition = self.partitions[self.partition_var.get()]
        algorithm = self.algorithm_var.get()
        
        success = False
        if algorithm == 'first_fit':
            success = partition.first_fit(job_size, job_id)
        elif algorithm == 'next_fit':
            success = partition.next_fit(job_size, job_id)
        elif algorithm == 'best_fit':
            success = partition.best_fit(job_size, job_id)
            
        if not success:
            messagebox.showerror("错误", "无法分配作业")
            
        self.draw_memory_state()
        
    def free_single_job(self):
        if not self.partitions:
            return
            
        job_id = self.job_id.get()
        partition = self.partitions[self.partition_var.get()]
        partition.free_memory(job_id)
        self.draw_memory_state()
        
    def set_total_memory(self):
        new_size = self.total_memory.get()
        if new_size <= 0:
            messagebox.showerror("错误", "总内存大小必须大于0")
            return
        
        # 检查新的内存大小是否小于已分配的内存总和
        total_allocated = sum(p.size for p in self.partitions.values())
        if total_allocated > new_size:
            messagebox.showerror("错误", "新的内存大小小于已分配���内存总和")
            return
        
        # 更新总内存大小
        self.total_memory.set(new_size)
        self.draw_memory_state()
        messagebox.showinfo("成功", f"总内存大小已设置为 {new_size}KB")
        
    def allocate_example_jobs(self):
        if not self.partitions:
            messagebox.showerror("错误", "请先创建分区")
            return
        
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, "1.第一次分配：分配4个作业，大小分别为 50、100、150、200。\n")
        
        jobs = [(1, 50), (2, 100), (3, 150), (4, 200)]
        partition = self.partitions[self.partition_var.get()]
        algorithm = self.algorithm_var.get()
        
        for job_id, size in jobs:
            success = False
            if algorithm == 'first_fit':
                success = partition.first_fit(size, job_id)
            elif algorithm == 'next_fit':
                success = partition.next_fit(size, job_id)
            elif algorithm == 'best_fit':
                success = partition.best_fit(size, job_id)
            
            if not success:
                messagebox.showerror("错误", f"无法分配作业{job_id}({size}KB)")
                return
        
        self.draw_memory_state()
        self.update_text_display()
        
    def free_job(self, job_id):
        if not self.partitions:
            return
        
        partition = self.partitions[self.partition_var.get()]
        if partition.free_memory(job_id):
            self.text_area.insert(tk.END, f"\n释放作业{job_id}后的状态：\n")
            self.draw_memory_state()
            self.update_text_display()
        else:
            messagebox.showerror("错误", f"未找到作业{job_id}")
        
    def update_text_display(self):
        if not self.partitions:
            return
        
        partition = self.partitions[self.partition_var.get()]
        text = f"当前内存状态（{partition.name}区）：\n"
        text += "内存状态：\n"
        
        # 显示内存块状态
        block_str = ""
        for block in partition.blocks:
            if block.is_free:
                block_str += f"[空闲 {block.size}KB]"
            else:
                block_str += f"[作业{block.job_id} {block.size}KB]"
        text += block_str + "\n\n"
        
        # 显示空闲块表
        text += "空闲块表示意图：\n"
        text += "+------------+--------------+-----------+\n"
        text += "| 空闲块编号 | 起始地址 (KB)| 大小 (KB) |\n"
        text += "+------------+--------------+-----------+\n"
        
        free_block_num = 1
        for block in partition.blocks:
            if block.is_free:
                text += f"|     {free_block_num:<5} |     {block.start_addr:<7} |   {block.size:<7} |\n"
                free_block_num += 1
        text += "+------------+--------------+-----------+\n"
        
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, text)
        

if __name__ == "__main__":
    root = tk.Tk()
    app = MemoryManagerGUI(root)
    root.mainloop() 