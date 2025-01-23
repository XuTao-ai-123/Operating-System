from scheduler import Scheduler
from process import ProcessState

class PriorityScheduler(Scheduler):
    def get_name(self):
        return "优先级调度(Priority)"
    
    def schedule(self, processes):
        self.processes = processes
        self.current_time = 0
        self.completed_processes = []
        remaining_processes = self.processes.copy()
        
        while remaining_processes:
            # 获取当前时间点可执行的进程
            available_processes = [
                p for p in remaining_processes 
                if p.arrival_time <= self.current_time
            ]
            
            if not available_processes:
                # 如果没有可用进程，时间推进到下一个进程的到达时间
                self.current_time = min(p.arrival_time for p in remaining_processes)
                continue
            
            # 选择优先级最高的进程（优先级数值越小优先级越高）
            process = min(available_processes, key=lambda p: p.priority)
            process.state = ProcessState.RUNNING
            
            # 计算等待时间
            process.waiting_time = self.current_time - process.arrival_time
            
            # 执行进程
            self.current_time += process.burst_time
            
            # 计算完成时间和周转时间
            process.completion_time = self.current_time
            process.turnaround_time = process.completion_time - process.arrival_time
            
            process.state = ProcessState.READY
            self.completed_processes.append(process)
            remaining_processes.remove(process) 