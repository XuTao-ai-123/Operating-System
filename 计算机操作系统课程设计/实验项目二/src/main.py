import tkinter as tk
from tkinter import ttk
from process import Process, ProcessState
from fcfs_scheduler import FCFSScheduler
from sjf_scheduler import SJFScheduler
from rr_scheduler import RRScheduler
from priority_scheduler import PriorityScheduler
from hrrn_scheduler import HRRNScheduler
from tkinter import filedialog
import os

class ProcessSchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("进程调度模拟器")
        
        # 创建进程列表
        self.processes = []
        
        # 默认时间片大小
        self.time_quantum = tk.IntVar(value=2)
        
        # 创建调度器（RR调度器会在选择时动态创建）
        self.schedulers = [
            FCFSScheduler(),
            SJFScheduler(),
            PriorityScheduler(),
            HRRNScheduler()
        ]
        
        self.setup_ui()
        
    def setup_ui(self):
        # 创建主框架，使用网格布局
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部控制面板
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="5")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 左侧：文件操作
        file_frame = ttk.Frame(control_frame)
        file_frame.pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="加载文件", command=self.load_processes).pack(pady=2)
        ttk.Button(file_frame, text="增加进程", command=self.add_process_dialog).pack(pady=2)
        ttk.Button(file_frame, text="删除进程", command=self.delete_selected_process).pack(pady=2)
        
        # 中间：时间片设置
        quantum_frame = ttk.Frame(control_frame)
        quantum_frame.pack(side=tk.LEFT, padx=20)
        ttk.Label(quantum_frame, text="时间片大小:").pack(side=tk.LEFT)
        quantum_spinbox = ttk.Spinbox(
            quantum_frame,
            from_=1,
            to=10,
            width=5,
            textvariable=self.time_quantum
        )
        quantum_spinbox.pack(side=tk.LEFT, padx=5)
        
        # 右侧：算法选择和控制按钮
        algo_frame = ttk.Frame(control_frame)
        algo_frame.pack(side=tk.LEFT, padx=5)
        
        # 算法选择下拉框
        self.algorithm_var = tk.StringVar()
        algorithm_combo = ttk.Combobox(
            algo_frame, 
            textvariable=self.algorithm_var,
            values=[
                "先来先服务(FCFS)",
                "最短作业优先(SJF)",
                "优先级调度(Priority)",
                "时间片轮转(RR)",
                "高响应比(HRRN)"
            ],
            width=20
        )
        algorithm_combo.set("选择调度算法")
        algorithm_combo.pack(side=tk.LEFT, padx=5)
        
        # 控制按钮组
        btn_frame = ttk.Frame(algo_frame)
        btn_frame.pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="开始调度", command=self.start_scheduling).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="暂停", command=self.pause_scheduling).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="重置", command=self.reset_scheduling).pack(side=tk.LEFT, padx=2)
        
        # 进程信息表格区域
        table_frame = ttk.LabelFrame(main_frame, text="进程信息", padding="5")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建进程表格
        columns = ('ID', '到达时间', '运行时间', '优先级', '状态')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 设置列
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.CENTER)
        
        # 放置表格和滚动条
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(main_frame, text="调度结果", padding="5")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 添加文本框和滚动条
        self.result_text = tk.Text(result_frame, height=10, wrap=tk.WORD)
        result_scroll = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=result_scroll.set)
        
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        result_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加示例数据
        self.add_sample_processes()
        
    def add_sample_processes(self):
        sample_processes = [
            Process("P1", 0, 5, 3),
            Process("P2", 1, 3, 2),
            Process("P3", 2, 8, 1),
            Process("P4", 3, 6, 4),
        ]
        
        for p in sample_processes:
            self.processes.append(p)
            self.tree.insert('', tk.END, values=(
                p.id, p.arrival_time, p.burst_time, p.priority, p.state
            ))
            
    def start_scheduling(self):
        selected_algorithm = self.algorithm_var.get()
        
        # 根据选择的算法获取对应的调度器
        if selected_algorithm == "时间片轮转(RR)":
            scheduler = RRScheduler(time_quantum=self.time_quantum.get())
        else:
            scheduler = next(
                (s for s in self.schedulers if s.get_name() == selected_algorithm), 
                None
            )
        
        if scheduler:
            scheduler.schedule(self.processes.copy())
            self.show_results(scheduler)
            
    def show_results(self, scheduler):
        # 在结果开始前添加分隔线
        self.result_text.insert(tk.END, "\n" + "="*50 + "\n\n")
        
        result = f"{scheduler.get_name()}：\n"
        
        # 获取执行结果
        execution_info = scheduler.schedule(self.processes.copy())
        
        # 显示执行顺序
        if isinstance(scheduler, RRScheduler):
            result += "执行顺序：\n时间段 进程\n"
            for proc_id, start, end in execution_info:
                result += f"{start:2d} - {end:2d} {proc_id}\n"
        else:
            result += "执行顺序："
            execution_sequence = " → ".join([p.id for p in scheduler.completed_processes])
            result += f"{execution_sequence}\n"
        
        # 显示完成时间
        result += "完成时间："
        completion_times = [f"{p.id} = {p.completion_time}" for p in scheduler.completed_processes]
        result += ", ".join(completion_times) + "\n"
        
        # 显示周转时间
        result += "周转时间："
        turnaround_times = [f"{p.id} = {p.turnaround_time}" for p in scheduler.completed_processes]
        result += ", ".join(turnaround_times) + "\n"
        
        # 显示等待时间
        result += "等待时间："
        waiting_times = [f"{p.id} = {p.waiting_time}" for p in scheduler.completed_processes]
        result += ", ".join(waiting_times) + "\n"
        
        # 显示平均时间
        result += f"平均周转时间：{scheduler.get_average_turnaround_time():.2f}\n"
        result += f"平均等待时间：{scheduler.get_average_waiting_time():.2f}\n"
        
        # 将结果添加到文本框末尾
        self.result_text.insert(tk.END, result)
        # 自动滚动到最新结果
        self.result_text.see(tk.END)
        
    def pause_scheduling(self):
        pass
        
    def reset_scheduling(self):
        for p in self.processes:
            p.state = ProcessState.READY
            p.remaining_time = p.burst_time
            p.waiting_time = 0
            p.turnaround_time = 0
            
        self.update_process_table()
        self.result_text.delete(1.0, tk.END)
        
    def update_process_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for p in self.processes:
            self.tree.insert('', tk.END, values=(
                p.id, p.arrival_time, p.burst_time, p.priority, p.state
            ))
    
    def load_processes(self):
        filename = filedialog.askopenfilename(
            title="选择进程数据文件",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if filename:
            # 清空现有进程
            self.processes.clear()
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 从文件读取进程数据
            with open(filename, 'r', encoding='utf-8') as file:
                for line in file:
                    if line.strip():
                        # 解析每行数据：进程ID 到达时间 运行时间 优先级
                        pid, arrival_time, burst_time, priority = line.strip().split()
                        process = Process(
                            pid,
                            int(arrival_time),
                            int(burst_time),
                            int(priority)
                        )
                        self.processes.append(process)
                        self.tree.insert('', tk.END, values=(
                            process.id,
                            process.arrival_time,
                            process.burst_time,
                            process.priority,
                            process.state
                        ))

    def add_process_dialog(self):
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("添加进程")
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        
        # 创建输入框架
        input_frame = ttk.Frame(dialog, padding="10")
        input_frame.pack(fill=tk.BOTH, expand=True)
        
        # 进程信息输入
        ttk.Label(input_frame, text="进程ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        id_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=id_var).grid(row=0, column=1, pady=2)
        
        ttk.Label(input_frame, text="到达时间:").grid(row=1, column=0, sticky=tk.W, pady=2)
        arrival_var = tk.IntVar()
        ttk.Entry(input_frame, textvariable=arrival_var).grid(row=1, column=1, pady=2)
        
        ttk.Label(input_frame, text="运行时间:").grid(row=2, column=0, sticky=tk.W, pady=2)
        burst_var = tk.IntVar()
        ttk.Entry(input_frame, textvariable=burst_var).grid(row=2, column=1, pady=2)
        
        ttk.Label(input_frame, text="优先级:").grid(row=3, column=0, sticky=tk.W, pady=2)
        priority_var = tk.IntVar()
        ttk.Entry(input_frame, textvariable=priority_var).grid(row=3, column=1, pady=2)
        
        def confirm_add():
            try:
                # 创建新进程
                process = Process(
                    id_var.get(),
                    arrival_var.get(),
                    burst_var.get(),
                    priority_var.get()
                )
                # 添加到进程列表和表格
                self.processes.append(process)
                self.tree.insert('', tk.END, values=(
                    process.id,
                    process.arrival_time,
                    process.burst_time,
                    process.priority,
                    process.state
                ))
                dialog.destroy()
            except ValueError:
                tk.messagebox.showerror("错误", "请输入有效的数值")
        
        # 确认按钮
        ttk.Button(input_frame, text="确认", command=confirm_add).grid(row=4, column=0, columnspan=2, pady=10)

    def delete_selected_process(self):
        # 获取选中的项
        selected_item = self.tree.selection()
        if not selected_item:
            tk.messagebox.showwarning("警告", "请先选择要删除的进程")
            return
        
        # 确认删除
        if tk.messagebox.askyesno("确认", "确定要删除选中的进程吗？"):
            for item in selected_item:
                # 获取进程ID
                process_id = self.tree.item(item)['values'][0]
                # 从进程列表中删除
                self.processes = [p for p in self.processes if p.id != process_id]
                # 从表格中删除
                self.tree.delete(item)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProcessSchedulerGUI(root)
    root.mainloop() 