# visualizer/gantt_chart.py

import matplotlib.pyplot as plt
from collections import defaultdict

def draw_gantt_chart(timeline):
    fig, ax = plt.subplots(figsize=(10, 3))
    process_bars = defaultdict(list)

    # 각 프로세스별로 시작과 연속 길이를 묶어서 막대 위치 구성
    if not timeline:
        print("❗ No timeline data to draw.")
        return

    prev_pid = timeline[0][1]
    start_time = timeline[0][0]

    for i in range(1, len(timeline)):
        time, pid = timeline[i]
        if pid != prev_pid:
            process_bars[prev_pid].append((start_time, time - start_time))
            start_time = time
            prev_pid = pid

    # 마지막 조각 저장
    process_bars[prev_pid].append((start_time, timeline[-1][0] + 1 - start_time))

    yticks = []
    ylabels = []

    for i, (pid, intervals) in enumerate(process_bars.items()):
        for start, duration in intervals:
            ax.broken_barh([(start, duration)], (i - 0.4, 0.8), facecolors=f"C{pid % 10}")
            ax.text(start + duration / 2, i, f"P{pid}", va='center', ha='center', color='white', fontsize=8)
        yticks.append(i)
        ylabels.append(f"P{pid}")

    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels)
    ax.set_xlabel("Time")
    ax.set_title("Gantt Chart - Round Robin")
    ax.grid(True, axis='x', linestyle='--', alpha=0.5)
    ax.set_ylim(-1, len(process_bars))
    plt.tight_layout()
    plt.show()
