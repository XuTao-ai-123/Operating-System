from abc import ABC, abstractmethod

class Scheduler(ABC):
    def __init__(self):
        self.processes = []
        self.current_time = 0
        self.completed_processes = []
    
    @abstractmethod
    def schedule(self, processes):
        pass
    
    @abstractmethod
    def get_name(self):
        pass
    
    def get_average_turnaround_time(self):
        if not self.completed_processes:
            return 0
        total = sum(p.turnaround_time for p in self.completed_processes)
        return total / len(self.completed_processes)
    
    def get_average_waiting_time(self):
        if not self.completed_processes:
            return 0
        total = sum(p.waiting_time for p in self.completed_processes)
        return total / len(self.completed_processes) 