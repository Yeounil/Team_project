# visualizer/gantt_chart.py

import matplotlib.pyplot as plt
from collections import defaultdict

def draw_gantt_chart(ax, timeline):
    if not timeline:
        print("❗ No timeline data to draw.")
        return

    yticks = []
    ylabels = []
    pid_set = set()
    y_positions = {}
    current_y = 0

    for start, pid, duration in timeline:
        if pid not in pid_set:
            pid_set.add(pid)
            y_positions[pid] = current_y
            yticks.append(current_y)
            ylabels.append(f"P{pid}")
            current_y += 1

        y = y_positions[pid]
        ax.broken_barh([(start, duration)], (y - 0.4, 0.8), facecolors=f"C{pid % 10}")
        ax.text(start + duration / 2, y, f"P{pid}", va='center', ha='center', color='white', fontsize=8)

    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels)
    ax.set_xlabel("Time")
    ax.set_title("Gantt Chart - Scheduling Result")
    ax.grid(True, axis='x', linestyle='--', alpha=0.5)
    ax.set_ylim(-1, current_y)

