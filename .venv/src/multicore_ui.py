import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QSpinBox, QTableWidget, QTableWidgetItem, QTextEdit, QLabel, QComboBox
from scheduler.factory import create_scheduler
from scheduler.multicore.scheduler import MultiCoreScheduler

class SchedulerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multicore Process Scheduler")
        self.layout = QVBoxLayout()

        self.core_label = QLabel("사용할 코어 수:")
        self.core_input = QSpinBox()
        self.core_input.setRange(1, 4)

        self.algo_label = QLabel("스케줄링 알고리즘:")
        self.algo_choice = QComboBox()
        self.algo_choice.addItems(["FCFS", "SJF", "Priority", "RR"])

        self.quantum_label = QLabel("Round Robin Quantum (RR 선택 시):")
        self.quantum_input = QSpinBox()
        self.quantum_input.setRange(1, 100)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["PID", "Arrival Time", "Burst Time"])

        self.add_row_button = QPushButton("프로세스 추가")
        self.run_button = QPushButton("시뮬레이션 실행")
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)

        self.layout.addWidget(self.core_label)
        self.layout.addWidget(self.core_input)
        self.layout.addWidget(self.algo_label)
        self.layout.addWidget(self.algo_choice)
        self.layout.addWidget(self.quantum_label)
        self.layout.addWidget(self.quantum_input)
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.add_row_button)
        self.layout.addWidget(self.run_button)
        self.layout.addWidget(self.result_box)

        self.setLayout(self.layout)

        self.add_row_button.clicked.connect(self.add_row)
        self.run_button.clicked.connect(self.run_simulation)

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)

    def run_simulation(self):
        core_count = self.core_input.value()
        algorithm_name = self.algo_choice.currentText()
        quantum = self.quantum_input.value() if algorithm_name == "RR" else None

        processes = []
        for row in range(self.table.rowCount()):
            pid = int(self.table.item(row, 0).text())
            arrival = int(self.table.item(row, 1).text())
            burst = int(self.table.item(row, 2).text())
            processes.append({"pid": pid, "arrival_time": arrival, "burst_time": burst})

        scheduler_algo = create_scheduler(algorithm_name, quantum)
        multicore_scheduler = MultiCoreScheduler(core_count, scheduler_algo)

        multicore_scheduler.load_processes(processes)
        multicore_scheduler.run()

        results = multicore_scheduler.get_results()
        self.result_box.setText(results)


def run():
    app = QApplication(sys.argv)
    window = SchedulerUI()
    window.show()
    sys.exit(app.exec_())