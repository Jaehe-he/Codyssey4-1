import time
import json #딕셔너리를 JSON 형태로 출력
import sys #다른 폴더에 있는 파일 가져오기 위해
import os #파일 경로 다루기 위해
import threading #입력(종료)와 출력(센서 반복) 동시 처리

from mars_mission_computer_exception import DummySensor

# Week 5 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
week5_path = os.path.join(current_dir, '..', 'Week 5. 2026-04-03')
sys.path.append(week5_path)


class MissionComputer:
    def __init__(self):
        self.env_values = {}
        self.ds = DummySensor() #DummySensor를 ds로 인스턴스화
        self.running = True #반복실행

        # 평균 계산용
        self.data_log = []
        self.start_time = time.time()

    def stop(self):
        self.running = False

    #5분 평균 계산하는 함수
    def calculate_average(self):
        if not self.data_log:
            return

        avg_values = {}

        for key in self.data_log[0]:
            avg_values[key] = sum(d[key] for d in self.data_log) / len(self.data_log)

        print('\n[5분 평균 값]')
        print(json.dumps(avg_values, indent=4))

        self.data_log = []
        self.start_time = time.time()

    def get_sensor_data(self):
        while self.running:
            try:
                # 1. 값 생성
                self.ds.set_env()

                # 2. 값 가져오기
                sensor_data = self.ds.get_env()

                # 저장
                self.env_values = sensor_data
                self.data_log.append(sensor_data)

                # 출력 (JSON)
                print(json.dumps(self.env_values, indent=4))

            except Exception as e:
                print(f'센서 오류 발생: {e}')

            # 5분 평균 체크
            if time.time() - self.start_time >= 300:
                self.calculate_average()

            time.sleep(5)

        print('System stoped....')


def listen_for_stop(mc):
    input('종료하려면 Enter를 누르세요...\n')
    mc.stop()


if __name__ == '__main__':
    RunComputer = MissionComputer()

    input_thread = threading.Thread(target=listen_for_stop, args=(RunComputer,))
    input_thread.daemon = True
    input_thread.start()

    RunComputer.get_sensor_data()