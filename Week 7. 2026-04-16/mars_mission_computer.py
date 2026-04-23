import time
import json
import sys
import os
import threading
import platform

# psutil (있으면 사용, 없으면 None)
try:
    import psutil
    print('psutil 있음')
except ImportError:
    print('psutil 없음')
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
        print(json.dumps(avg_values, indent=4, ensure_ascii=False))

        self.data_log = []
        self.start_time = time.time()

    # ✅ 시스템 정보 (psutil 유무 대응)
    def get_mission_computer_info(self):
        try:
            info = {}

            info['운영체제'] = platform.system()
            info['운영체제 버전'] = platform.version()
            info['CPU 타입'] = platform.processor()

            # CPU 코어 수
            try:
                if psutil:
                    info['CPU 코어 수'] = psutil.cpu_count(logical=True)
                else:
                    info['CPU 코어 수'] = os.cpu_count()
            except Exception as e:
                print(f'CPU 코어 수 오류: {e}')
                info['CPU 코어 수'] = 'N/A'

            # 메모리 크기 (여기가 문제일 가능성 큼)
            try:
                if psutil:
                    memory = psutil.virtual_memory()
                    info['메모리 크기(GB)'] = round(memory.total / (1024 ** 3), 2)
                else:
                    info['메모리 크기(GB)'] = 'N/A'
            except Exception as e:
                print(f'메모리 정보 오류: {e}')
                info['메모리 크기(GB)'] = 'N/A'

            print('\n[시스템 정보]')
            print(json.dumps(info, indent=4, ensure_ascii=False))

        except Exception as e:
            print(f'시스템 정보 오류: {e}')

    # ✅ 시스템 부하 (psutil 없으면 N/A)
    def get_mission_computer_load(self):
        try:
            load = {}

            if psutil:
                load['CPU 사용률(%)'] = psutil.cpu_percent(interval=1)
                load['메모리 사용률(%)'] = psutil.virtual_memory().percent
            else:
                load['CPU 사용률(%)'] = 'N/A'
                load['메모리 사용률(%)'] = 'N/A'

            print('\n[시스템 부하]')
            print(json.dumps(load, indent=4, ensure_ascii=False))

        except Exception as e:
            print(f'시스템 부하 오류: {e}')

    def get_sensor_data(self):
        while self.running:
            try:
                self.ds.set_env()
                sensor_data = self.ds.get_env()

                self.env_values = sensor_data
                self.data_log.append(sensor_data)

                print(json.dumps(self.env_values, indent=4, ensure_ascii=False))

            except Exception as e:
                print(f'센서 오류 발생: {e}')

            if time.time() - self.start_time >= 300:
                self.calculate_average()

            time.sleep(5)

        print('System stoped....')


def listen_for_stop(mc):
    input('종료하려면 Enter를 누르세요...\n')
    mc.stop()


if __name__ == '__main__':
    RunComputer = MissionComputer()

    # 시스템 정보 + 부하 출력
    RunComputer.get_mission_computer_info()
    RunComputer.get_mission_computer_load()

    input_thread = threading.Thread(target=listen_for_stop, args=(RunComputer,))
    input_thread.daemon = True
    input_thread.start()

    RunComputer.get_sensor_data()