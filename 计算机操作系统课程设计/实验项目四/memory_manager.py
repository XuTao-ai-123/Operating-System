class MemoryBlock:
    def __init__(self, start_addr, size, is_free=True, job_id=None):
        self.start_addr = start_addr  # 起始地址
        self.size = size             # 大小
        self.is_free = is_free       # 是否为空闲
        self.job_id = job_id         # 作业ID

class MemoryPartition:
    def __init__(self, size, name):
        self.size = size            # 分区大小
        self.name = name            # 分区名称 (A, B, C)
        self.blocks = [MemoryBlock(0, size)]  # 初始化为一个完整的空闲块
        self.last_allocated_index = 0  # 用于循环首次适应算法
        
    def first_fit(self, job_size, job_id):
        for block in self.blocks:
            if block.is_free and block.size >= job_size:
                return self._allocate_memory(block, job_size, job_id)
        return False
    
    def best_fit(self, job_size, job_id):
        best_block = None
        min_fragment = float('inf')
        
        for block in self.blocks:
            if block.is_free and block.size >= job_size:
                fragment = block.size - job_size
                if fragment < min_fragment:
                    min_fragment = fragment
                    best_block = block
                    
        if best_block:
            return self._allocate_memory(best_block, job_size, job_id)
        return False
    
    def next_fit(self, job_size, job_id):
        start_index = self.last_allocated_index
        block_count = len(self.blocks)
        
        # 从上次分配位置开始搜索
        for i in range(block_count):
            current_index = (start_index + i) % block_count
            block = self.blocks[current_index]
            
            if block.is_free and block.size >= job_size:
                self.last_allocated_index = current_index
                return self._allocate_memory(block, job_size, job_id)
                
        return False
    
    def _allocate_memory(self, block, job_size, job_id):
        if block.size > job_size:
            # 分割块
            new_block = MemoryBlock(
                block.start_addr + job_size,
                block.size - job_size,
                True
            )
            block.size = job_size
            idx = self.blocks.index(block)
            self.blocks.insert(idx + 1, new_block)
            
        block.is_free = False
        block.job_id = job_id
        return True
        
    def free_memory(self, job_id):
        for i, block in enumerate(self.blocks):
            if block.job_id == job_id:
                block.is_free = True
                block.job_id = None
                self._merge_free_blocks()
                return True
        return False
    
    def _merge_free_blocks(self):
        i = 0
        while i < len(self.blocks) - 1:
            if self.blocks[i].is_free and self.blocks[i+1].is_free:
                self.blocks[i].size += self.blocks[i+1].size
                self.blocks.pop(i+1)
            else:
                i += 1 