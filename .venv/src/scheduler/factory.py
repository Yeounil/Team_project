from scheduler.algorithms.fcfs import FCFS
from scheduler.algorithms.sjf import SJF
from scheduler.algorithms.priority import Priority
from scheduler.algorithms.rr import RoundRobin
from scheduler.algorithms.spn import SPN
from scheduler.algorithms.srtn import SRTN

def create_scheduler(name, quantum=None):
    if name.lower() == "fcfs":
        return FCFS()
    elif name.lower() == "sjf":
        return SJF()
    elif name.lower() == "priority":
        return Priority()
    elif name.lower() == "spn":
        return SPN()
    elif name.lower() == "rr":
        if quantum is None:
            raise ValueError("RR 알고리즘은 quantum이 필요합니다.")
        return RoundRobin(quantum)
    elif name.lower() == "srtn":
        return SRTN()
    else:
        raise ValueError(f"알 수 없는 알고리즘 이름: {name}")
