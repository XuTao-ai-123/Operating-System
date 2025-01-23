from scheduler import Scheduler
from process import ProcessState
from collections import deque

class RRScheduler(Scheduler):
    def __init__(self, time_quantum=2):
        super().__init__()
        self.time_quantum = time_quantum
    
    def get_name(self):
        return f"时间片轮转(RR, 时间片={self.time_quantum})"
    
    def schedule(self, processes):
        self.processes = processes
        self.current_time = 0
        self.completed_processes = []
        execution_sequence = []
        
        # 初始化进程的剩余时间
        for p in processes:
            p.remaining_time = p.burst_time
        
        # 就绪队列
        ready_queue = deque()
        remaining_processes = processes.copy()
        
        while remaining_processes or ready_queue:
            # 将已到达的进程加入就绪队列
            arrived_processes = [p for p in remaining_processes if p.arrival_time <= self.current_time]
            for p in arrived_processes:
                ready_queue.append(p)
                remaining_processes.remove(p)
            
            if not ready_queue:
                # 如果就绪队列为空，时间推进到下一个进程到达
                if remaining_processes:
                    next_arrival = min(p.arrival_time for p in remaining_processes)
                    self.current_time = next_arrival
                continue
            
            # 取出队首进程执行
            current_process = ready_queue.popleft()
            current_process.state = ProcessState.RUNNING
            
            # 确定本次执行时间
            execute_time = min(self.time_quantum, current_process.remaining_time)
            
            # 记录执行序列
            execution_sequence.append(
                (current_process.id, self.current_time, self.current_time + execute_time)
            )
            
            # 更新时间和进程状态
            self.current_time += execute_time
            current_process.remaining_time -= execute_time
            
            # 检查进程是否完成
            if current_process.remaining_time == 0:
                current_process.completion_time = self.current_time
                current_process.turnaround_time = current_process.completion_time - current_process.arrival_time
                current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
                current_process.state = ProcessState.READY
                self.completed_processes.append(current_process)
            else:
                # 如果进程未完成，重新加入队列
                # 但要先检查是否有新到达的进程
                newly_arrived = [
                    p for p in remaining_processes 
                    if p.arrival_time <= self.current_time
                ]
                for p in newly_arrived:
                    ready_queue.append(p)
                    remaining_processes.remove(p)
                # 然后将当前进程加入队列尾部
                current_process.state = ProcessState.READY
                ready_queue.append(current_process)
        
        return execution_sequence