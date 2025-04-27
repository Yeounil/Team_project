# scheduler/utils.py

from scheduler.process import Process

def load_processes_from_config(process_data):
    processes = []
    for pdata in process_data:
        processes.append(Process(
            pid=pdata["pid"],
            arrival_time=pdata["arrival_time"],
            burst_time=pdata["burst_time"],
            priority=pdata.get("priority", 0)
        ))
    return processes
