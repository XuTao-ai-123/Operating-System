import tkinter as tk
from tkinter import ttk
import threading
import time
import random
from queue import Queue
import logging

class FruitBuffer:
    def __init__(self, size=20):
        self.size = size
        self.buffer = ["空"] * size
        self.lock = threading.Lock()
        self.not_full = threading.Condition(self.lock)
        self.not_empty = threading.Condition(self.lock)
        
    def put(self, item, position):
        with self.not_full:
            while self.buffer[position] != "空":
                self.not_full.wait()
            self.buffer[position] = item
            self.not_empty.notify()
            
    def get(self, position):
        with self.not_empty:
            while self.buffer[position] == "空":
                self.not_empty.wait()
            item = self.buffer[position]
            self.buffer[position] = "空"
            self.not_full.notify()
            return item

class ProducerConsumerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("桔子苹果生产者消费者问题")
        
        self.buffer = None
        self.running = False
        self.paused = False
        
        self.setup_gui()
        
    def setup_gui(self):
        # 参数设置区域
        self.param_frame = tk.LabelFrame(self.root, text="参数设置")
        self.param_frame.pack(pady=10, padx=10, fill="x")
        
        # 缓冲区大小
        tk.Label(self.param_frame, text="缓冲区大小:").grid(row=0, column=0, padx=5, pady=5)
        self.buffer_size = tk.Entry(self.param_frame, width=10)
        self.buffer_size.insert(0, "20")
        self.buffer_size.grid(row=0, column=1)
        
        # 生产者数量
        tk.Label(self.param_frame, text="生产者数量:").grid(row=1, column=0, padx=5, pady=5)
        self.producer_count = tk.Entry(self.param_frame, width=10)
        self.producer_count.insert(0, "20")
        self.producer_count.grid(row=1, column=1)
        
        # 消费者数量
        tk.Label(self.param_frame, text="消费者数量:").grid(row=2, column=0, padx=5, pady=5)
        self.consumer_count = tk.Entry(self.param_frame, width=10)
        self.consumer_count.insert(0, "20")
        self.consumer_count.grid(row=2, column=1)
        
        # 速率设置
        tk.Label(self.param_frame, text="桔子生产速率(个/秒):").grid(row=0, column=2, padx=5, pady=5)
        self.orange_prod_rate = tk.Entry(self.param_frame, width=10)
        self.orange_prod_rate.insert(0, "2")
        self.orange_prod_rate.grid(row=0, column=3)
        
        tk.Label(self.param_frame, text="苹果生产速率(个/秒):").grid(row=1, column=2, padx=5, pady=5)
        self.apple_prod_rate = tk.Entry(self.param_frame, width=10)
        self.apple_prod_rate.insert(0, "1")
        self.apple_prod_rate.grid(row=1, column=3)
        
        tk.Label(self.param_frame, text="消费速率(个/秒):").grid(row=2, column=2, padx=5, pady=5)
        self.consume_rate = tk.Entry(self.param_frame, width=10)
        self.consume_rate.insert(0, "1")
        self.consume_rate.grid(row=2, column=3)
        
        # 缓冲区显示区域
        self.buffer_frame = tk.LabelFrame(self.root, text="缓冲区状态")
        self.buffer_frame.pack(pady=10, padx=10)
        
        self.buffer_labels = []
        for i in range(20):
            label = tk.Label(self.buffer_frame, 
                           text="空",
                           width=4, height=2,
                           relief="raised",
                           bg="green")
            label.grid(row=i//10, column=i%10, padx=2, pady=2)
            self.buffer_labels.append(label)
        
        # 控制按钮
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)
        
        self.start_button = tk.Button(self.button_frame,
                                    text="开始",
                                    command=self.start_simulation)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = tk.Button(self.button_frame,
                                    text="暂停",
                                    command=self.toggle_pause,
                                    state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        self.quit_button = tk.Button(self.button_frame,
                                   text="退出",
                                   command=self.quit_program)
        self.quit_button.pack(side=tk.LEFT, padx=5)
        
    def start_simulation(self):
        if not self.running:
            try:
                buffer_size = int(self.buffer_size.get())
                self.buffer = FruitBuffer(buffer_size)
                self.running = True
                self.paused = False
                
                self.start_button.config(state=tk.DISABLED)
                self.pause_button.config(state=tk.NORMAL)
                
                self.create_threads()
            except ValueError:
                tk.messagebox.showerror("错误", "请输入有效的数值")
                
    def create_threads(self):
        self.threads = []
        producer_count = int(self.producer_count.get())
        consumer_count = int(self.consumer_count.get())
        
        # 创建生产者线程
        for _ in range(producer_count):
            t = threading.Thread(target=self.producer, args=("桔子",))
            self.threads.append(t)
            t.start()
            
            t = threading.Thread(target=self.producer, args=("苹果",))
            self.threads.append(t)
            t.start()
            
        # 创建消费者线程
        for _ in range(consumer_count):
            t = threading.Thread(target=self.consumer, args=("桔子",))
            self.threads.append(t)
            t.start()
            
            t = threading.Thread(target=self.consumer, args=("苹果",))
            self.threads.append(t)
            t.start()
    
    def producer(self, fruit_type):
        while self.running:
            if not self.paused:
                try:
                    rate = (int(self.orange_prod_rate.get()) if fruit_type == "桔子"
                           else int(self.apple_prod_rate.get()))
                    if rate > 0:
                        time.sleep(1/rate)
                    
                    position = random.randint(0, int(self.buffer_size.get())-1)
                    self.buffer.put(fruit_type, position)
                    self.update_buffer_display()
                except ValueError:
                    continue
                
    def consumer(self, fruit_type):
        while self.running:
            if not self.paused:
                try:
                    rate = int(self.consume_rate.get())
                    if rate > 0:
                        time.sleep(1/rate)
                    
                    position = random.randint(0, int(self.buffer_size.get())-1)
                    if self.buffer.buffer[position] == fruit_type:
                        self.buffer.get(position)
                        self.update_buffer_display()
                except ValueError:
                    continue

    def update_buffer_display(self):
        for i, item in enumerate(self.buffer.buffer):
            color = "green" if item == "空" else "red"
            self.buffer_labels[i].config(text=item, bg=color)
        self.root.update()
        
    def toggle_pause(self):
        if self.running:
            self.paused = not self.paused
            self.pause_button.config(text="继续" if self.paused else "暂停")
        
    def quit_program(self):
        self.running = False
        if hasattr(self, 'threads'):
            for thread in self.threads:
                thread.join()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProducerConsumerGUI(root)
    root.mainloop() 