class HRRN:

    def schedule(self, ready_queue, cores):
        time = 0

        while ready_queue:
            # 다음 프로세스 처리를 결정: 남은 프로세스의 도착시간 확인
            arrived = [p for p in ready_queue if p['arrival_time'] <= time]
            if not arrived:
                # 아직 도착하지 않은 프로세스가 있다면
                # time을 ready_queue안에 있는 도착시간 중 가장 작은 시점으로 감
                time = min(p['arrival_time'] for p in ready_queue)
                continue

            # 현재 도착한 작업들의 응답비율을 계산: (대기시간 + 실행시간) / 실행시간
            for p in arrived:
                wait_time = time - p['arrival_time']
                p['response_ratio'] = (wait_time + p['burst_time']) / p['burst_time']
            # 응답비율이 가장 큰 프로세스를 정하고 ready_queue에서 제거
            next_p = max(arrived, key=lambda x: x['response_ratio'])
            ready_queue.remove(p)

            # 실제 실행 시작 시점 계산
            start_time = max(time, next_p['arrival_time'])

            # 첫 번째 빈 코어에 할당
            for core in cores:
                # core.timeline이 비어있거나, 마지막 시작 시간 <= 현재 시각이면 idle
                if not core.timeline or core.timeline[-1][0] <= time:
                    # 결과를 튜플로 기록
                    core.timeline.append((start_time, p['pid']))
                    break

            # time을 종료 시점으로 이동
            time = start_time + next_p['burst_time']
            break