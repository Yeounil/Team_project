import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QSpinBox, QTableWidget, QTableWidgetItem, QLabel, QComboBox, QGridLayout
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scheduler.factory import create_scheduler
from scheduler.multicore.scheduler import MultiCoreScheduler
from visualizer.gantt_chart import draw_gantt_chart
from scheduler.process import Process

class SchedulerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multicore Process Scheduler")

        # 전체 수평 레이아웃
        main_layout = QHBoxLayout()

        # 왼쪽 입력 패널
        input_layout = QVBoxLayout()

        self.pcore_label = QLabel("P-코어 수:")
        self.pcore_input = QSpinBox()
        self.pcore_input.setRange(0, 4)
        self.pcore_input.valueChanged.connect(self.update_ecore_limit)

        self.ecore_label = QLabel("E-코어 수:")
        self.ecore_input = QSpinBox()
        self.ecore_input.setRange(0, 4)

        self.core_label = QLabel("총 코어 수 제한: 최대 4")

        self.algo_label = QLabel("스케줄링 알고리즘:")
        self.algo_choice = QComboBox()
        self.algo_choice.addItems(["FCFS", "HRRN", "Priority", "RR", "SPN", "SRTN"])

        self.quantum_label = QLabel("Round Robin Quantum (RR 선택 시):")
        self.quantum_input = QSpinBox()
        self.quantum_input.setRange(1, 100)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["PID", "Arrival Time", "Burst Time"])

        self.add_row_button = QPushButton("프로세스 추가")
        self.run_button = QPushButton("시뮬레이션 실행")

        # 입력 패널 구성
        input_layout.addWidget(self.pcore_label)
        input_layout.addWidget(self.pcore_input)
        input_layout.addWidget(self.ecore_label)
        input_layout.addWidget(self.ecore_input)
        input_layout.addWidget(self.core_label)
        input_layout.addWidget(self.algo_label)
        input_layout.addWidget(self.algo_choice)
        input_layout.addWidget(self.quantum_label)
        input_layout.addWidget(self.quantum_input)
        input_layout.addWidget(self.table)
        input_layout.addWidget(self.add_row_button)
        input_layout.addWidget(self.run_button)

        # 오른쪽 Gantt 차트 패널
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        # 레이아웃 배치
        main_layout.addLayout(input_layout, 2)  # 왼쪽 2 비율
        main_layout.addWidget(self.canvas, 3)   # 오른쪽 3 비율

        self.setLayout(main_layout)

        # 이벤트 연결
        self.add_row_button.clicked.connect(self.add_row)
        self.run_button.clicked.connect(self.run_simulation)

    def update_ecore_limit(self):
        max_ecore = 4 - self.pcore_input.value()
        self.ecore_input.setMaximum(max_ecore)

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)

    def run_simulation(self):
        print("▶ run_simulation() 호출됨")  # 1단계: 함수 진입 확인

        pcore_count = self.pcore_input.value()
        ecore_count = self.ecore_input.value()
        total_cores = pcore_count + ecore_count

        print(f"▶ 선택된 코어: P={pcore_count}, E={ecore_count}")  # 2단계: 코어 수 확인

        if total_cores == 0:
            print("❗ 최소 1개 이상의 코어를 선택해야 합니다.")
            return

        algorithm_name = self.algo_choice.currentText()
        quantum = self.quantum_input.value() if algorithm_name == "RR" else None
        print(f"▶ 알고리즘: {algorithm_name}, Quantum: {quantum}")  # 3단계: 알고리즘 확인

        processes = []
        for row in range(self.table.rowCount()):
            try:
                pid_item = self.table.item(row, 0)
                arrival_item = self.table.item(row, 1)
                burst_item = self.table.item(row, 2)

                if not pid_item or not arrival_item or not burst_item:
                    print(f"❗ Row {row}에 빈 셀이 있음")
                    continue

                pid = int(pid_item.text())
                arrival = int(arrival_item.text())
                burst = int(burst_item.text())

                print(f"✅ Process 추가됨: PID={pid}, arrival={arrival}, burst={burst}")
                processes.append(Process(pid, arrival, burst))

            except Exception as e:
                print(f"❗ 프로세스 생성 중 오류 발생 (row={row}): {e}")
                return

        scheduler_algo = create_scheduler(algorithm_name, quantum)
        print("✅ 스케줄러 생성 완료")

        multicore_scheduler = MultiCoreScheduler(total_cores, scheduler_algo)
        multicore_scheduler.load_processes(processes)
        multicore_scheduler.run()

        timelines = multicore_scheduler.get_timelines()
        print("🟩 get_timelines 결과:", timelines)

        self.plot_gantt_chart(timelines)

    def plot_gantt_chart(self, timelines):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        draw_gantt_chart(ax, timelines)

        self.canvas.draw()

def run():
    app = QApplication(sys.argv)
    window = SchedulerUI()
    window.show()
    sys.exit(app.exec_())
