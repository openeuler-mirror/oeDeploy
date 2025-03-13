import subprocess

bound_cpus = {0:1,1:1}


def execute_command(command):
    print(command)
    result = subprocess.run(command.split(), capture_output=True, text=True).stdout.split()
    print(result)


def isolate_tids(tids, cpu_range):
    command = f"taskset -cp {cpu_range[0]}-{cpu_range[-1]} {tids[0]}"
    execute_command(command)
    i = 0
    cpuSkippedCount = 0
    while i < len(tids):
        cpu = cpu_range[i + cpuSkippedCount]+24
        if cpu in bound_cpus:
            cpuSkippedCount += 1
            continue
        bound_cpus[cpu] = 1
        command = f"taskset -cp {cpu} {tids[i]}"
        execute_command(command)
        i += 1


def check_is_valid(info):
    #return "release_thread" in info or "acl_thread" in infoi
    #return "rayMsRayWorke" in info or "python3" in info or "Hccl_Notify" in info
    return "batch_launch" in info or "frontend" in info or "backend" in info or "Actor" in info or "bprop" in info or "python3" in info or "MsRayWorke" in info

def enforce_isolation():
    npu_len = 8
    command = "npu-smi info -t topo"
    result = subprocess.run(command.split(), capture_output=True, text=True).stdout.split()
    cpu_lists = [val for i, val in enumerate(result) if i > npu_len + 1 and i % (npu_len + 2) == 9][:8]
    cpu_lists = [range(int(cpu_st.split('-')[0]), int(cpu_st.split('-')[1])) for cpu_st in cpu_lists]

    command = "npu-smi info"
    result = subprocess.run(command.split(), capture_output=True, text=True).stdout
    arr = " ".join(result.split('\n')[-npu_len * 2 - 2:]).split('|')

    pids = [pid.strip() for i, pid in enumerate(arr) if i % 5 == 2]
    tids = []

    for pid in pids:
        command = f"ps -T -p {pid}"
        results = subprocess.run(command.split(), capture_output=True, text=True).stdout
        results = results.split('\n')
        key_sort = lambda l1: "0" if len(l1) < 4 else l1.split()[3]
        result = [info for info in results if check_is_valid(info)]
        result = sorted(result, key=key_sort)
        len_top_results = 9
        top_results = result[-len_top_results-1:-1]
        new_tids = [info.split()[1] for info in top_results]
        tids += [[pid] + new_tids]

    print("cpu-sets: ", cpu_lists)
    print("*" * 10)
    print("pids on npu: ", pids)
    print("*" * 10)
    print("tids: ", tids)

    for i in range(len(pids)):
        isolate_tids(tids[i], cpu_lists[i])

enforce_isolation()

