from scheduler.process import Process

class RoundRobinScheduler:
    def __init__(self, quantum):
        self.quantum = quantum

    def schedule(self, ready_queue, pcores, ecores):
        current_time = 0
        process_queue = [Process(p['pid'], p['arrival_time'], p['burst_time']) for p in ready_queue]
        process_queue.sort(key=lambda p: p.arrival_time)

        all_cores = pcores + ecores
        process_queue_buffer = []

        while process_queue or process_queue_buffer or any(p.remaining_time > 0 for p in sum([c.timeline for c in all_cores], [])):
            # 도착한 프로세스 큐에 넣기
            arrived = [p for p in process_queue if p.arrival_time <= current_time]
            for p in arrived:
                process_queue_buffer.append(p)
                process_queue.remove(p)

            if not process_queue_buffer:
                current_time += 1
                continue

            for core in all_cores:
                if not process_queue_buffer:
                    break
                if current_time < core.next_free_time:
                    continue

                process = process_queue_buffer.pop(0)

                if core.is_idle:
                    core.startup_count += 1
                    core.total_power += core.startup_power
                    core.is_idle = False

                actual_burst = min(self.quantum * core.performance, process.remaining_time)
                duration = actual_burst // core.performance

                if process.start_time is None:
                    process.start_time = current_time

                core.timeline.append((current_time, process.pid, duration))
                core.total_power += duration * core.power_rate
                current_time += duration

                process.remaining_time -= actual_burst
                core.next_free_time = current_time

                if process.remaining_time > 0:
                    process_queue_buffer.append(process)
                else:
                    process.finish_time = current_time
                    process.turn_around_time = process.finish_time - process.arrival_time
                    process.waiting_time = process.turn_around_time - process.burst_time
                    process.normalized_TT = round(process.turn_around_time / process.burst_time, 2)
