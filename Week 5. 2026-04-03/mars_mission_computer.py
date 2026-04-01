import random
from datetime import datetime

# 더미 센서 클래스 생성
class DummySensor:
    def __init__(self):
        self.env_values = {}

    def set_env(self):
        self.env_values['mars_base_internal_temperature'] = random.uniform(18, 30)
        self.env_values['mars_base_external_temperature'] = random.uniform(0, 21)
        self.env_values['mars_base_internal_humidity'] = random.uniform(50, 60)
        self.env_values['mars_base_external_illuminance'] = random.uniform(500, 715)
        self.env_values['mars_base_internal_co2'] = random.uniform(0.02, 0.1)
        self.env_values['mars_base_internal_oxygen'] = random.uniform(4, 7)

    def get_env(self):
        now = datetime.now()

        log_line = (
            f'{now}, '
            f"{self.env_values['mars_base_internal_temperature']}, "
            f"{self.env_values['mars_base_external_temperature']}, "
            f"{self.env_values['mars_base_internal_humidity']}, "
            f"{self.env_values['mars_base_external_illuminance']}, "
            f"{self.env_values['mars_base_internal_co2']}, "
            f"{self.env_values['mars_base_internal_oxygen']}\n"
        )

        with open('mars_log.txt', 'a') as f:
            f.write(log_line)

        return self.env_values

ds = DummySensor()

ds.set_env()
env = ds.get_env()

print(env)    