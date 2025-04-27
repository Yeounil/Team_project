class Core:
    def __init__(self, core_id):
        self.core_id = core_id
        self.current_process = None
        self.timeline = []  # (start_time, pid)


class MultiCoreScheduler:
    def __init__(self, core_count, scheduler):
        self.cores = [Core(i) for i in range(core_count)]
        self.scheduler = scheduler
        self.processes = []

    def load_processes(self, process_list):
        self.processes = process_list

    def run(self):
        ready_queue = self.processes.copy()
        self.scheduler.schedule(ready_queue, self.cores)

    def get_results(self):
        output = ""
        for core in self.cores:
            output += f"Core {core.core_id}: {core.timeline}\n"
        return output
