import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def draw_gantt_chart(ax, core_info):
    if not core_info:
        print("❗ No timeline data to draw.")
        return

    max_time = 0

    ax.set_xlim(-6, 50)
    ax.set_ylim(-1, len(core_info))

    for core_idx, (core_type, core_timeline) in enumerate(core_info):
        color = 'red' if core_type == 'P' else 'blue'

        for start, pid, duration in core_timeline:
            if duration <= 0:
                continue
            ax.broken_barh([(start, duration)], (core_idx - 0.4, 0.8),
                           facecolors=f"C{pid % 10}")
            ax.text(start + duration / 2, core_idx, f"P{pid}",
                    ha='center', va='center', color='white', fontsize=9, fontweight='bold')

            max_time = max(max_time, start + duration)

        # y축 왼쪽 코어 레이블 박스
        label_rect_x = -5.5
        rect = Rectangle((label_rect_x, core_idx - 0.4), 4.5, 0.8,
                         edgecolor='black', facecolor=color)
        ax.add_patch(rect)
        ax.text(label_rect_x + 2.25, core_idx, f"{core_type}-Core {core_idx}",
                ha='center', va='center', color='white', fontsize=9, fontweight='bold')

    ax.set_yticks([])
    ax.set_xlabel("Time")
    ax.set_title("Gantt Chart - Core Usage")
    ax.grid(True, axis='x', linestyle='--', alpha=0.5)
    ax.set_xlim(-6, max_time + 5)
    ax.set_xticks(np.arange(0, max_time + 6, 1))
