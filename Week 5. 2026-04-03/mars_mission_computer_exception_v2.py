import random
from datetime import datetime #현재 날짜/시간 가져오기


# 더미 센서 클래스 생성
class DummySensor:
    #센서 값들을 한번에 관리하기 위해 env_values 데이터 저장소 생성
    def __init__(self):
        self.env_values = {}

    #센서 값 생성
    def set_env(self):
        # random.uniform : 랜덤 값 생성
        # round : 소수점 2자리까지 자름 (가독성을 위해)
        self.env_values['mars_base_internal_temperature'] = round(random.uniform(18, 30), 2)
        self.env_values['mars_base_external_temperature'] = round(random.uniform(0, 21), 2)
        self.env_values['mars_base_internal_humidity'] = round(random.uniform(50, 60), 2)
        self.env_values['mars_base_external_illuminance'] = round(random.uniform(500, 715), 2)
        self.env_values['mars_base_internal_co2'] = round(random.uniform(0.02, 0.1), 4)
        self.env_values['mars_base_internal_oxygen'] = round(random.uniform(4, 7), 2)

        # 값 범위 검증 (예외 상황 방지)
        if not (18 <= self.env_values['mars_base_internal_temperature'] <= 30):
            raise ValueError('내부 온도 값 이상')

        if not (0 <= self.env_values['mars_base_external_temperature'] <= 21):
            raise ValueError('외부 온도 값 이상')
        
        if not (50 <= self.env_values['mars_base_internal_humidity'] <= 60):
            raise ValueError('내부 습도 이상')
        
        if not (500 <= self.env_values['mars_base_external_illuminance'] <= 715):
            raise ValueError('외부 광량 이상')

        if not (0.02 <= self.env_values['mars_base_internal_co2'] <= 0.1):
            raise ValueError('내부 이산화탄소 농도 이상')

        if not (4 <= self.env_values['mars_base_internal_oxygen'] <= 7):
            raise ValueError('내부 산소 농도')

    # 센서 값 읽기+로그 저장
    def get_env(self):
        # set_env 비어있는지 확인
        if not self.env_values:
            raise ValueError('환경 값이 설정되지 않았습니다. set_env()를 먼저 호출하세요.')

        # 현재 시간 출력
        now = datetime.now()

        try:
            # 로그 문자열 만들기. key 값 있으면 문자열로 만들기
            log_line = (
                f'{now}, '
                f"내부 온도 : {self.env_values.get('mars_base_internal_temperature', 'N/A')}°C, | "
                f"외부 온도 : {self.env_values.get('mars_base_external_temperature', 'N/A')}°C, | "
                f"내부 습도 : {self.env_values.get('mars_base_internal_humidity', 'N/A')}%, | "
                f"외부 광량 : {self.env_values.get('mars_base_external_illuminance', 'N/A')} W/m², | "
                f"내부 CO2 : {self.env_values.get('mars_base_internal_co2', 'N/A')}%, | "
                f"내부 산소 : {self.env_values.get('mars_base_internal_oxygen', 'N/A')}% |\n"
            )

            # 파일 저장 예외 처리
            with open('mars_log_exception_v2.txt', 'a', encoding='utf-8') as f:
                f.write(log_line)

        except IOError:
            print('로그 파일 저장 중 오류 발생')

        return self.env_values


# 실행 코드 (객체 생성)
ds = DummySensor()

# 값 생성
ds.set_env()

# 값 가져오기 + 로그 저장
env = ds.get_env()

# 출력
print(f"내부 온도 : {env['mars_base_internal_temperature']}°C")
print(f"외부 온도 : {env['mars_base_external_temperature']}°C")
print(f"내부 습도 : {env['mars_base_internal_humidity']}%")
print(f"외부 광량 : {env['mars_base_external_illuminance']} W/m²")
print(f"내부 CO2 : {env['mars_base_internal_co2']}%")
print(f"내부 산소 : {env['mars_base_internal_oxygen']}%")