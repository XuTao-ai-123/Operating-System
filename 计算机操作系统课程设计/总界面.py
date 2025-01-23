import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import subprocess

class MainGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("操作系统课程设计")
        
        # 设置窗口大小和位置
        window_width = 1200
        window_height = 800
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 设置背景图片
        try:
            # 加载原始图片
            bg_image = Image.open("R-C (1).jpg")
            
            # 计算缩放比例，保持原始比例
            img_ratio = bg_image.width / bg_image.height
            window_ratio = window_width / window_height
            
            if window_ratio > img_ratio:
                # 如果窗口比图片更宽，以宽度为准
                new_width = window_width
                new_height = int(window_width / img_ratio)
            else:
                # 如果窗口比图片更高，以高度为准
                new_height = window_height
                new_width = int(window_height * img_ratio)
            
            # 调整图片大小
            bg_image = bg_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            
            # 创建背景标签并居中放置
            self.bg_label = tk.Label(root, image=self.bg_photo)
            self.bg_label.place(x=(window_width-new_width)//2, y=(window_height-new_height)//2)
            
        except Exception as e:
            print(f"加载背景图片出错: {str(e)}")
            self.root.configure(bg='lightblue')
            
        self.setup_ui()
        
    def setup_ui(self):
        # 顶部标题
        title_label = tk.Label(
            self.root,
            text="操作系统课程设计",
            font=("Microsoft YaHei", 24, "bold")
        )
        title_label['bg'] = self.root['bg']
        title_label.place(relx=0.5, rely=0.05, anchor='center')
        
        # 项目按钮
        projects = [
            ("项目一：银行家算法", "实验项目一"),
            ("项目二：通用处理机调度", "实验项目二"),
            ("项目三：进程同步", "实验项目三"),
            ("项目四：存储管理", "实验项目四"),
            ("项目五：虚拟存储器模拟", "实验项目五"),
            ("项目六：文件系统", "实验项目六"),
            ("项目七：磁盘调度", "实验项目七"),
            ("项目八：多进程同步模拟", "实验项目八")
        ]
        
        # 统一的按钮样式
        button_style = {
            'width': 30,
            'height': 1,
            'font': ('Microsoft YaHei', 11, 'bold'),
            'bg': '#4a90e2',  # 明亮的蓝色
            'fg': 'white',    # 白色文字
            'relief': 'raised',  # 凸起的3D效果
            'borderwidth': 3,
            'cursor': 'hand2',
            'padx': 10,
            'pady': 5,
            'activebackground': '#357abd',  # 点击时的颜色
            'activeforeground': 'white'     # 点击时的文字颜色
        }
        
        # 创建按钮并直接放置在root上
        button_start_y = 0.2  # 开始位置
        button_spacing = 0.07  # 按钮间距
        
        for i, (name, folder) in enumerate(projects):
            btn = tk.Button(
                self.root,
                text=name,
                command=lambda f=folder: self.run_project(f),
                **button_style
            )
            btn.place(relx=0.5, rely=button_start_y + i * button_spacing, anchor='center')
            
            # 添加鼠标悬停效果
            def on_enter(e, button=btn):
                button.config(bg='#357abd')  # 深蓝色
            def on_leave(e, button=btn):
                button.config(bg='#4a90e2')  # 恢复原来的蓝色
                
            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)
        
        # 退出按钮 - 底部居中
        exit_btn = tk.Button(
            self.root,
            text="退出",
            command=self.root.quit,
            width=10,
            height=1,
            font=('Microsoft YaHei', 11, 'bold'),
            bg='#e74c3c',  # 红色
            fg='white',
            relief='raised',
            borderwidth=3,
            cursor='hand2',
            padx=10,
            pady=5,
            activebackground='#c0392b',  # 深红色
            activeforeground='white'
        )
        exit_btn.place(relx=0.5, rely=0.85, anchor='center')
        
        # 退出按钮悬停效果
        def on_exit_enter(e):
            exit_btn.config(bg='#c0392b')  # 深红色
        def on_exit_leave(e):
            exit_btn.config(bg='#e74c3c')  # 恢复原来的红色
            
        exit_btn.bind('<Enter>', on_exit_enter)
        exit_btn.bind('<Leave>', on_exit_leave)
    
    def run_project(self, project_folder):
        try:
            if not os.path.exists(project_folder):
                messagebox.showerror("错误", f"找不到项目文件夹: {project_folder}")
                return
                
            # 保存当前工作目录
            original_dir = os.getcwd()
            
            # 切换到项目目录
            os.chdir(project_folder)
            
            # 根据不同项目选择不同的运行文件
            if project_folder == "实验项目一":
                main_file = "main.py"
            elif project_folder == "实验项目二":
                main_file = os.path.join("src", "main.py")
            elif project_folder == "实验项目三":
                main_file = "reader_writer_gui.py"
            elif project_folder == "实验项目四":
                main_file = "main.py"
            elif project_folder == "实验项目五":
                main_file = "page_replacement_gui.py"
            elif project_folder == "实验项目六":
                main_file = "filesystem_gui.py"
            elif project_folder == "实验项目七":
                main_file = "disk_scheduler.py"
            elif project_folder == "实验项目八":
                main_file = "producer_consumer.py"
                
            if os.path.exists(main_file):
                subprocess.Popen([sys.executable, main_file])
            else:
                messagebox.showerror("错误", f"找不到主程序文件: {main_file}")
            
            # 恢复原来的工作目录
            os.chdir(original_dir)
                
        except Exception as e:
            messagebox.showerror("错误", f"运行项目时出错: {str(e)}")
            # 确保恢复原来的工作目录
            if 'original_dir' in locals():
                os.chdir(original_dir)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainGUI(root)
    root.mainloop()
