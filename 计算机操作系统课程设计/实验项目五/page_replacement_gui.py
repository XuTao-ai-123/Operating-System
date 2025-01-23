import random
import tkinter as tk
from tkinter import ttk, messagebox

class PageReplacementGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("页面置换算法模拟")
        self.root.geometry("1000x700")
        
        # 创建页面置换算法实例
        self.pr = PageReplacement(3)
        
        self.create_widgets()
        
    def create_widgets(self):
        # 框架设置
        control_frame = ttk.LabelFrame(self.root, text="控制面板", padding="10")
        control_frame.pack(fill="x", padx=10, pady=5)
        
        button_frame = ttk.LabelFrame(self.root, text="算法选择", padding="10")
        button_frame.pack(fill="x", padx=10, pady=5)
        
        result_frame = ttk.LabelFrame(self.root, text="结果显示", padding="10")
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 控制面板组件
        ttk.Label(control_frame, text="物理内存框数:").grid(row=0, column=0, padx=5, pady=5)
        self.frames_var = tk.StringVar(value="3")
        frames_entry = ttk.Entry(control_frame, textvariable=self.frames_var, width=10)
        frames_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(control_frame, text="页面序列:").grid(row=1, column=0, padx=5, pady=5)
        self.pages_var = tk.StringVar(value="7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1")
        pages_entry = ttk.Entry(control_frame, textvariable=self.pages_var, width=70)
        pages_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5)
        
        ttk.Button(control_frame, text="生成随机序列", command=self.generate_random).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(control_frame, text="清空结果", command=self.clear_results).grid(row=0, column=3, padx=5, pady=5)
        
        # 在控制面板添加页面序列生成控制
        ttk.Label(control_frame, text="页面个数:").grid(row=2, column=0, padx=5, pady=5)
        self.page_count_var = tk.StringVar(value="20")
        page_count_entry = ttk.Entry(control_frame, textvariable=self.page_count_var, width=10)
        page_count_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(control_frame, text="最大页面号:").grid(row=2, column=2, padx=5, pady=5)
        self.max_page_var = tk.StringVar(value="7")
        max_page_entry = ttk.Entry(control_frame, textvariable=self.max_page_var, width=10)
        max_page_entry.grid(row=2, column=3, padx=5, pady=5)
        
        # 算法按钮
        algorithms = [
            ("FIFO算法", self.run_fifo),
            ("LRU算法", self.run_lru),
            ("OPT算法", self.run_opt),
            ("运行所有算法", self.run_all)
        ]
        
        for i, (text, command) in enumerate(algorithms):
            btn = ttk.Button(button_frame, text=text, command=command, width=20)
            btn.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 结果显示区域
        self.result_text = tk.Text(result_frame, height=30, width=80, font=("Courier New", 10))
        self.result_text.pack(fill="both", expand=True, padx=5, pady=5)
        
    def generate_random(self):
        try:
            page_count = int(self.page_count_var.get())
            max_page = int(self.max_page_var.get())
            
            if page_count <= 0:
                raise ValueError("页面个数必须大于0")
            if max_page < 0:
                raise ValueError("最大页面号必须大于等于0")
                
            pages = [random.randint(0, max_page) for _ in range(page_count)]
            self.pages_var.set(",".join(map(str, pages)))
            
        except ValueError as e:
            if str(e).startswith("页面") or str(e).startswith("最大"):
                messagebox.showerror("错误", str(e))
            else:
                messagebox.showerror("错误", "请输入有效的数字")
        
    def clear_results(self):
        self.result_text.delete(1.0, tk.END)
        
    def run_algorithm(self, algo_name, algo_func):
        try:
            frames = int(self.frames_var.get())
            if frames <= 0:
                raise ValueError("物理内存框数必须大于0")
                
            pages_str = self.pages_var.get()
            pages = [int(x.strip()) for x in pages_str.split(",")]
            
            self.pr.frames = frames
            
            # 运行算法
            faults = algo_func(pages)
            total = len(pages)
            fault_rate = (faults / total) * 100
            hit_rate = 100 - fault_rate
            
            # 如果是第一个算法运行，显示条件信息
            if self.result_text.get(1.0, tk.END).strip() == "":
                header = (
                    f"实验条件:\n"
                    f"{'=' * 50}\n"
                    f"页面引用序列: {pages}\n"
                    f"物理内存框数: {frames}\n\n"
                    f"{'算法':<10}{'缺页次数':<8}{'总请求次数':<8}{'缺页率':<8}{'命中率'}\n"
                    f"{'-' * 50}\n"
                )
                self.result_text.insert(tk.END, header)
            
            # 只显示算法结果
            result = f"{algo_name:<10}{faults:<12}{total:<12}{fault_rate:<10.0f}{hit_rate:.0f}\n"
            self.result_text.insert(tk.END, result)
            
        except ValueError as e:
            messagebox.showerror("错误", str(e))
        except Exception as e:
            messagebox.showerror("错误", f"发生错误: {str(e)}")
            
    def run_fifo(self):
        self.run_algorithm("FIFO", self.pr.fifo)
        
    def run_lru(self):
        self.run_algorithm("LRU", self.pr.lru)
        
    def run_opt(self):
        self.run_algorithm("OPT", self.pr.opt)
        
    def run_all(self):
        self.clear_results()
        self.run_fifo()
        self.run_lru()
        self.run_opt()

class PageReplacement:
    def __init__(self, frames):
        self.frames = frames
        
    def fifo(self, pages):
        memory = []
        page_faults = 0
        
        for page in pages:
            if page not in memory:
                page_faults += 1
                if len(memory) >= self.frames:
                    memory.pop(0)  # 移除最先进入的页面
                memory.append(page)
            
        return page_faults
    
    def lru(self, pages):
        memory = []
        page_faults = 0
        
        for page in pages:
            if page not in memory:
                page_faults += 1
                if len(memory) >= self.frames:
                    memory.pop(0)  # 移除最久未使用的页面
                memory.append(page)
            else:
                # 将最近使用的页面移到最后
                memory.remove(page)
                memory.append(page)
                
        return page_faults
    
    def opt(self, pages):
        memory = []
        page_faults = 0
        
        for i, page in enumerate(pages):
            if page not in memory:
                page_faults += 1
                if len(memory) >= self.frames:
                    # 出未来最晚使用的页面
                    future_pages = pages[i+1:]
                    to_remove = None
                    furthest_use = -1
                    
                    for frame in memory:
                        if frame not in future_pages:
                            to_remove = frame
                            break
                        else:
                            next_use = future_pages.index(frame)
                            if next_use > furthest_use:
                                furthest_use = next_use
                                to_remove = frame
                                
                    memory.remove(to_remove)
                memory.append(page)
                
        return page_faults

def generate_random_pages(length=20, max_page=7):
    return [random.randint(0, max_page) for _ in range(length)]

def main():
    root = tk.Tk()
    app = PageReplacementGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 