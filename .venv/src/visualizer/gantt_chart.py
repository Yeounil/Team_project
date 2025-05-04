# visualizer/gantt_chart.py
import matplotlib.pyplot as plt
from collections import defaultdict

def draw_gantt_chart(ax, timelines):
    if not timelines:
        print("❗ No timeline data to draw.")
        return

    yticks = []
    ylabels = []
    max_time = 100
    for core_idx, core_timeline in enumerate(timelines):
        for start, pid, duration in core_timeline:
            if duration <= 0:
                continue
            ax.broken_barh([(start, duration)], (core_idx - 0.4, 0.8),
                           facecolors=f"C{pid % 10}")
            ax.text(start + duration / 2, core_idx, f"P{pid}",
                    ha='center', va='center', color='white', fontsize=8)
        yticks.append(core_idx)
        ylabels.append(f"Core {core_idx}")

    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels)
    ax.set_xlabel("Time")
    ax.set_title("Gantt Chart - Core Usage")
    ax.grid(True, axis='x', linestyle='--', alpha=0.5)
    ax.set_ylim(-1, len(timelines))

