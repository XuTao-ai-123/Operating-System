def calculate_need(max_matrix, allocation_matrix):
    need = []
    for i in range(len(max_matrix)):
        need.append([max_matrix[i][j] - allocation_matrix[i][j] 
                    for j in range(len(max_matrix[0]))])
    return need

def is_safe_state(processes, available, max_matrix, allocation_matrix):
    n = len(processes)
    m = len(available)
    
    # 计算Need矩阵
    need = calculate_need(max_matrix, allocation_matrix)
    
    # 复制可用资源数组
    work = available.copy()
    
    # 初始化完成数组
    finish = [False] * n
    safe_sequence = []
    
    # 按Need数排序的进程顺序
    process_order = sorted(range(n), 
                         key=lambda x: (sum(need[x]), x))
    
    count = 0
    while count < n:
        found = False
        for p_idx in process_order:
            if not finish[p_idx]:
                # 检查是否可以分配资源
                can_allocate = True
                for j in range(m):
                    if need[p_idx][j] > work[j]:
                        can_allocate = False
                        break
                
                if can_allocate:
                    # 分配资源
                    for j in range(m):
                        work[j] += allocation_matrix[p_idx][j]
                    finish[p_idx] = True
                    safe_sequence.append(p_idx)
                    count += 1
                    found = True
                    
        if not found:
            return False, []
            
    return True, safe_sequence

# 测试数据
processes = [0, 1, 2, 3, 4]
available = [3, 3, 2]
max_matrix = [
    [7, 5, 3],
    [3, 2, 2],
    [9, 0, 2],
    [2, 2, 2],
    [4, 3, 3]
]
allocation_matrix = [
    [0, 1, 0],
    [2, 0, 0],
    [3, 0, 2],
    [2, 1, 1],
    [0, 0, 2]
] 