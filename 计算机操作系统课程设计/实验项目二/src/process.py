class ProcessState:
    READY = "就绪"
    RUNNING = "运行"

class Process:
    def __init__(self, id, arrival_time, burst_time, priority):
        self.id = id
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.remaining_time = burst_time
        self.state = ProcessState.READY
        
        # 用于统计
        self.waiting_time = 0
        self.turnaround_time = 0
        self.completion_time = 0 