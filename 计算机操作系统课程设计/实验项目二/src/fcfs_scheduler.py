from scheduler import Scheduler
from process import ProcessState

class FCFSScheduler(Scheduler):
    def get_name(self):
        return "先来先服务(FCFS)"
    
    def schedule(self, processes):
        self.processes = sorted(processes, key=lambda p: p.arrival_time)
        self.current_time = 0
        self.completed_processes = []
        execution_sequence = []
        
        for process in self.processes:
            if self.current_time < process.arrival_time:
                self.current_time = process.arrival_time
                
            process.state = ProcessState.RUNNING
            process.waiting_time = self.current_time - process.arrival_time
            
            execution_sequence.append((process.id, self.current_time, self.current_time + process.burst_time))
            
            self.current_time += process.burst_time
            process.completion_time = self.current_time
            process.turnaround_time = process.completion_time - process.arrival_time
            
            process.state = ProcessState.READY
            self.completed_processes.append(process)
        
        return execution_sequence