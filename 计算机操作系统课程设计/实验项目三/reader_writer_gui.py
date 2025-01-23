import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from multiprocessing import Process, Array, Value, Semaphore, Lock, Queue
import time
import random
import os
import threading
from datetime import datetime

class Buffer:
    def __init__(self, size):
        self.size = size
        self.data = Array('c', b' ' * size)
        self.in_ptr = Value('i', 0)
        self.out_ptr = Value('i', 0)
        self.count = Value('i', 0)
        self.mutex = Lock()
        self.empty = Semaphore(size)
        self.full = Semaphore(0)
        self.running = Value('i', 1)
        self.start_time = Value('d', 0.0)

def writer_process(buffer, writer_id, message_queue):
    while buffer.running.value:
        try:
            # 获取当前缓冲区中的所有数据
            buffer.mutex.acquire()
            current_data = set()
            for i in range(buffer.size):
                char = buffer.data[i].decode()
                if char != ' ':
                    current_data.add(char)
            buffer.mutex.release()
            
            # 生成不重复的随机数据
            while True:
                data = chr(random.randint(65, 90))  # A-Z
                if data not in current_data:
                    break
            
            buffer.empty.acquire(timeout=1)
            buffer.mutex.acquire()
            
            if not buffer.running.value:
                buffer.mutex.release()
                break

            write_pos = buffer.in_ptr.value
            buffer.data[write_pos] = data.encode()[0]
            buffer.in_ptr.value = (buffer.in_ptr.value + 1) % buffer.size
            buffer.count.value += 1
            
            # 构建缓冲区状态字符串
            buffer_status = ""
            for i in range(buffer.size):
                char = buffer.data[i].decode()
                if char == ' ':
                    buffer_status += "[ ]"
                else:
                    buffer_status += f"[{char}]"
            
            # 使用共享的开始时间计算相对时间
            current_time = time.time() - buffer.start_time.value
            
            # 修改消息格式
            message = f"时间 {current_time:.1f}s: 写者{writer_id} 写入了数据 '{data}'。 缓冲区状态: {buffer_status}\n"
            message_queue.put(message)
            
            # 检查缓冲区是否已满
            if buffer.count.value >= buffer.size:  # 只有当真正满了才提示
                waiting_msg = f"时间 {current_time:.1f}s: 缓冲区已满，写者1、写者2、写者3 正在等待。\n"
                message_queue.put(waiting_msg)
            
            buffer.mutex.release()
            buffer.full.release()
            
            time.sleep(random.uniform(0.1, 0.5))
        except:
            break

def reader_process(buffer, message_queue):
    while buffer.running.value:
        try:
            buffer.full.acquire(timeout=1)
            buffer.mutex.acquire()
            
            if not buffer.running.value:
                buffer.mutex.release()
                break

            read_pos = buffer.out_ptr.value
            data = buffer.data[read_pos].decode()
            buffer.data[read_pos] = b' '[0]
            buffer.out_ptr.value = (buffer.out_ptr.value + 1) % buffer.size
            buffer.count.value -= 1
            
            # 构建缓冲区状态字符串
            buffer_status = ""
            for i in range(buffer.size):
                char = buffer.data[i].decode()
                if char == ' ':
                    buffer_status += "[ ]"
                else:
                    buffer_status += f"[{char}]"
            
            # 使用共享的开始时间计算相对时间
            current_time = time.time() - buffer.start_time.value
            
            # 修改消息格式
            message = f"时间 {current_time:.1f}s: 读者读取了数据 '{data}'。 缓冲区状态: {buffer_status}\n"
            message_queue.put(message)
            
            buffer.mutex.release()
            buffer.empty.release()
            
            time.sleep(random.uniform(0.1, 0.5))
        except:
            break

class ReaderWriterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("读者-写者问题可视化系统")
        self.root.geometry("800x600")
        
        self.style = ttk.Style()
        self.style.configure('TButton', padding=5)
        self.style.configure('TLabelframe', padding=10)
        
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        
        self.processes = []
        self.buffer = None
        self.message_queue = Queue()
        
        self.create_widgets()
        self.setup_layout()
        
        # 启动更新显示的线程
        self.update_thread = threading.Thread(target=self.update_display)
        self.update_thread.daemon = True
        self.update_thread.start()

    def create_widgets(self):
        # 创建控制面板
        self.control_frame = ttk.LabelFrame(self.main_frame, text="系统控制", padding="10")
        
        # 参数设置区域
        self.params_frame = ttk.Frame(self.control_frame)
        
        # 缓冲区大小设置
        ttk.Label(self.params_frame, text="缓冲区大小:").grid(row=0, column=0, padx=5)
        self.buffer_size_var = tk.StringVar(value="16")
        self.buffer_size_spinbox = ttk.Spinbox(
            self.params_frame,
            from_=1,
            to=32,
            textvariable=self.buffer_size_var,
            width=10,
            state='readonly'
        )
        self.buffer_size_spinbox.grid(row=0, column=1, padx=5)
        
        # 写者数量设置
        ttk.Label(self.params_frame, text="写者数量:").grid(row=0, column=2, padx=5)
        self.writer_count_var = tk.StringVar(value="3")
        self.writer_count_spinbox = ttk.Spinbox(
            self.params_frame,
            from_=1,
            to=10,
            textvariable=self.writer_count_var,
            width=10,
            state='readonly'
        )
        self.writer_count_spinbox.grid(row=0, column=3, padx=5)
        
        # 按钮区域
        self.button_frame = ttk.Frame(self.control_frame)
        
        self.start_button = ttk.Button(self.button_frame, text="开始", command=self.start)
        self.stop_button = ttk.Button(self.button_frame, text="停止", command=self.stop)
        self.reset_button = ttk.Button(self.button_frame, text="重置", command=self.reset)
        
        self.stop_button['state'] = 'disabled'
        self.reset_button['state'] = 'disabled'
        
        # 状态显示区域
        self.status_frame = ttk.LabelFrame(self.main_frame, text="运行状态", padding="10")
        
        # 文本显示区域
        self.text_area = scrolledtext.ScrolledText(self.status_frame, width=70, height=20)
        
        # 缓冲区可视化
        self.buffer_frame = ttk.LabelFrame(self.status_frame, text="缓冲区状态", padding="10")
        self.buffer_canvas = tk.Canvas(self.buffer_frame, height=80, bg='white')
        
        # 状态栏
        self.statusbar = ttk.Label(self.main_frame, text="就绪", relief=tk.SUNKEN, anchor=tk.W)

    def setup_layout(self):
        # 控制面板布局
        self.control_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.params_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.button_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # 按钮布局 - 调整按钮间距和大小
        for i, button in enumerate([self.start_button, self.stop_button, self.reset_button]):
            button.grid(row=0, column=i, padx=10, pady=5)
            button['width'] = 10  # 设置按钮宽度
        
        # 状态显示区域布局
        self.status_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.text_area.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # 缓冲区可视化布局
        self.buffer_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.buffer_canvas.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # 状态栏布局
        self.statusbar.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        
        # 配置权重
        self.main_frame.rowconfigure(1, weight=1)
        self.status_frame.rowconfigure(0, weight=1)
        self.status_frame.columnconfigure(0, weight=1)

    def update_display(self):
        try:
            while True:
                try:
                    message = self.message_queue.get_nowait()
                    self.text_area.insert(tk.END, message)
                    self.text_area.see(tk.END)
                    self.update_buffer_visualization()
                except:
                    self.root.after(100, self.update_display)
                    break
        except:
            pass

    def update_buffer_visualization(self):
        if self.buffer:
            self.buffer_canvas.delete("all")
            width = self.buffer_canvas.winfo_width()
            height = self.buffer_canvas.winfo_height()
            cell_width = width // self.buffer.size
            
            for i in range(self.buffer.size):
                x1 = i * cell_width
                x2 = x1 + cell_width
                y1 = 10
                y2 = height - 10
                
                # 绘制边框
                self.buffer_canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill='white',
                    outline='#666'
                )
                
                # 显示数据
                char = self.buffer.data[i].decode()
                if char != ' ':
                    self.buffer_canvas.create_text(
                        (x1 + x2) // 2,
                        (y1 + y2) // 2,
                        text=char,
                        font=('Arial', 12, 'bold')
                    )

    def start(self):
        try:
            buffer_size = int(self.buffer_size_var.get())
            writer_count = int(self.writer_count_var.get())
            
            if buffer_size < 1 or writer_count < 1:
                messagebox.showerror("错误", "缓冲区大小和写者数量必须大于0")
                return
                
            self.buffer = Buffer(buffer_size)
            self.buffer.start_time.value = time.time()
            self.buffer.running.value = 1
            
            self.message_queue.put("[系统] 系统启动\n")
            
            # 创建进程
            self.processes = []
            
            # 创建写者进程
            for i in range(writer_count):
                p = Process(target=writer_process, args=(self.buffer, i+1, self.message_queue))
                self.processes.append(p)
            
            # 创建读者进程
            reader_proc = Process(target=reader_process, args=(self.buffer, self.message_queue))
            self.processes.append(reader_proc)
            
            # 启动所有进程
            for p in self.processes:
                p.start()
            
            self.start_button['state'] = 'disabled'
            self.stop_button['state'] = 'normal'
            self.reset_button['state'] = 'normal'
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字！")

    def stop(self):
        if self.buffer:
            self.buffer.running.value = 0
            for p in self.processes:
                p.terminate()
            self.stop_button['state'] = 'disabled'
            self.reset_button['state'] = 'normal'
            self.message_queue.put("[系统] 系统已停止\n")

    def reset(self):
        self.text_area.delete(1.0, tk.END)
        self.buffer_canvas.delete("all")
        self.start_button['state'] = 'normal'
        self.stop_button['state'] = 'disabled'
        self.reset_button['state'] = 'disabled'
        self.message_queue.put("[系统] 系统已重置\n")

def main():
    root = tk.Tk()
    root.title("读者-写者问题可视化系统")
    
    # 设置窗口大小和位置
    window_width = 800
    window_height = 600
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    app = ReaderWriterGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main() 