import time
import json
import sys
import os
import threading
import platform

# psutil (시스템 정보 및 부하 확인용)
try:
    import psutil
except ImportError:
    psutil = None

# Week 5 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
week5_path = os.path.join(current_dir, '..', 'Week 5. 2026-04-03')
sys.path.append(week5_path)

from mars_mission_computer_exception import DummySensor


class MissionComputer:
    def __init__(self):
        self.env_values = {}
        self.ds = DummySensor()
        self.running = True

        # 평균 계산용
        self.data_log = []
        self.start_time = time.time()

    def stop(self):
        self.running = False

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

    # ✅ 시스템 정보 출력
    def get_mission_computer_info(self):
        try:
            info = {}

            info['os'] = platform.system()
            info['os_version'] = platform.version()
            info['cpu_type'] = platform.processor()

            if psutil:
                info['cpu_cores'] = psutil.cpu_count(logical=True)
                memory = psutil.virtual_memory()
                info['memory_gb'] = round(memory.total / (1024 ** 3), 2)
            else:
                info['cpu_cores'] = 'N/A'
                info['memory_gb'] = 'N/A'

            print('\n[시스템 정보]')
            print(json.dumps(info, indent=4))

        except Exception as e:
            print(f'시스템 정보 오류: {e}')

    # ✅ 시스템 부하 출력
    def get_mission_computer_load(self):
        try:
            load = {}

            if psutil:
                load['cpu_usage'] = psutil.cpu_percent(interval=1)
                load['memory_usage'] = psutil.virtual_memory().percent
            else:
                load['cpu_usage'] = 'N/A'
                load['memory_usage'] = 'N/A'

            print('\n[시스템 부하]')
            print(json.dumps(load, indent=4))

        except Exception as e:
            print(f'시스템 부하 오류: {e}')

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

    # ✅ 문제 8 요구사항: 시스템 정보 + 부하 출력
    RunComputer.get_mission_computer_info()
    RunComputer.get_mission_computer_load()

    input_thread = threading.Thread(target=listen_for_stop, args=(RunComputer,))
    input_thread.daemon = True
    input_thread.start()

    RunComputer.get_sensor_data()