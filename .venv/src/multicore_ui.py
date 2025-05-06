import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QSpinBox, QTableWidget, QTableWidgetItem, QLabel, QComboBox,
    QSplitter, QSizePolicy, QHeaderView, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scheduler.factory import create_scheduler
from scheduler.multicore.scheduler import MultiCoreScheduler
from visualizer.gantt_chart import draw_gantt_chart
from scheduler.process import Process

class SchedulerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multicore Process Scheduler") #window 제목 설정
        self.setMinimumSize(1600, 800)

        main_layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # 입력 영역 구성
        input_panel = QWidget()
        input_layout = QVBoxLayout(input_panel)

        self.pcore_input = self._create_labeled_spinbox("P-코어 수:", input_layout, 0, 4)
        self.pcore_input.valueChanged.connect(self.update_ecore_limit)
        self.ecore_input = self._create_labeled_spinbox("E-코어 수:", input_layout, 0, 4)
        self.core_label = QLabel("총 코어 수 제한: 최대 4")
        input_layout.addWidget(self.core_label)

        self.algo_choice = self._create_labeled_combobox("스케줄링 알고리즘:", input_layout,
                                                        ["FCFS", "HRRN", "Priority", "RR", "SPN", "SRTN"])
        self.quantum_input = self._create_labeled_spinbox("Round Robin Quantum (RR 선택 시):", input_layout, 1, 100)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["PID", "Arrival Time", "Burst Time"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        input_layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        self.add_row_button = QPushButton("프로세스 추가")
        self.run_button = QPushButton("시뮬레이션 실행")
        button_layout.addWidget(self.add_row_button)
        button_layout.addWidget(self.run_button)
        input_layout.addLayout(button_layout)

        input_layout.addWidget(QLabel("스케줄링 결과"))
        self.result_table = QTableWidget(0, 5)
        self.result_table.setHorizontalHeaderLabels(["PID", "WT", "TT", "NTT", "Finish Time"])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        input_layout.addWidget(self.result_table)

        self.power_label = QLabel("전력 소비: P-core = 0, E-core = 0, Total = 0")
        self.power_label.setAlignment(Qt.AlignCenter)
        self.power_label.setFont(QFont("HY헤드라인", 12, QFont.Bold))
        self.power_label.setStyleSheet(
            "color: #004488; margin-top: 10px; padding: 6px; border: 1px solid #004488; border-radius: 4px; background-color: #e0f0ff;")
        input_layout.addWidget(self.power_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(input_panel)
        splitter.addWidget(scroll_area)

        # Gantt 차트 영역
        chart_panel = QWidget()
        chart_layout = QVBoxLayout(chart_panel)
        self.figure = Figure(figsize=(10, 6))
        self.figure.subplots_adjust(left=0.01, right=0.99, top=0.95, bottom=0.1)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        chart_layout.addWidget(self.canvas)
        splitter.addWidget(chart_panel)

        # 이벤트 연결
        self.add_row_button.clicked.connect(self.add_row)
        self.run_button.clicked.connect(self.run_simulation)
        self.apply_stylesheet()

    def apply_stylesheet(self):
        self.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }

            QTableWidget {
                border: 1px solid #ccc;
                font-size: 13px;
            }

            QLabel {
                font-weight: bold;
            }

            QComboBox, QSpinBox, QTableWidget {
                padding: 4px;
                border: 1px solid #aaa;
                border-radius: 4px;
            }

            QWidget {
                font-family: 'HY헤드라인';
                font-size: 12px;
            }
        """)

    def _create_labeled_spinbox(self, label_text, layout, min_val, max_val):
        layout.addWidget(QLabel(label_text))
        spinbox = QSpinBox()
        spinbox.setRange(min_val, max_val)
        layout.addWidget(spinbox)
        return spinbox

    def _create_labeled_combobox(self, label_text, layout, items):
        layout.addWidget(QLabel(label_text))
        combo = QComboBox()
        combo.addItems(items)
        layout.addWidget(combo)
        return combo

    def update_ecore_limit(self):
        max_ecore = 4 - self.pcore_input.value()
        self.ecore_input.setMaximum(max_ecore)

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)

    def run_simulation(self):
        pcore_count = self.pcore_input.value()
        ecore_count = self.ecore_input.value()
        if pcore_count + ecore_count == 0:
            return

        algorithm = self.algo_choice.currentText()
        quantum = self.quantum_input.value() if algorithm == "RR" else None

        processes = []
        for row in range(self.table.rowCount()):
            try:
                pid = int(self.table.item(row, 0).text())
                arrival = int(self.table.item(row, 1).text())
                burst = int(self.table.item(row, 2).text())
                processes.append(Process(pid, arrival, burst))
            except:
                continue

        self.result_table.setRowCount(len(processes))
        scheduler_algo = create_scheduler(algorithm, quantum)
        multicore_scheduler = MultiCoreScheduler(pcore_count, ecore_count, scheduler_algo)
        multicore_scheduler.load_processes(processes)
        multicore_scheduler.run()

        for i, p in enumerate(processes):
            self.result_table.setItem(i, 0, QTableWidgetItem(str(p.pid)))
            self.result_table.setItem(i, 1, QTableWidgetItem(str(p.waiting_time)))
            self.result_table.setItem(i, 2, QTableWidgetItem(str(p.turn_around_time)))
            self.result_table.setItem(i, 3, QTableWidgetItem(str(p.normalized_TT)))
            self.result_table.setItem(i, 4, QTableWidgetItem(str(p.finish_time)))

        p_power = sum(c.total_power for c in multicore_scheduler.pcores)
        e_power = sum(c.total_power for c in multicore_scheduler.ecores)
        self.power_label.setText(
            f"<b><span style='color:red;'>P-core</span> = {p_power:.2f}W</b>  |  "
            f"<b><span style='color:blue;'>E-core</span> = {e_power:.2f}W</b>  |  "
            f"<b><span style='color:green;'>Total</span> = {p_power + e_power:.2f}W</b>"
        )

        self.plot_gantt_chart(multicore_scheduler.get_timelines(), multicore_scheduler.get_core_types())

    def plot_gantt_chart(self, timelines, core_types):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        draw_gantt_chart(ax, list(zip(core_types, timelines)))
        self.canvas.draw()

def run():
    app = QApplication(sys.argv)
    window = SchedulerUI()
    window.show()
    sys.exit(app.exec_())
