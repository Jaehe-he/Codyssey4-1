import itertools
import os
import time
import zipfile
import zlib


ZIP_FILE_NAME = 'emergency_storage_key.zip'
PASSWORD_FILE_NAME = 'password.txt'
EXTRACT_DIR = 'emergency_storage_key'

CHARACTERS = '0123456789abcdefghijklmnopqrstuvwxyz'
PASSWORD_LENGTH = 6
PRINT_INTERVAL = 1000000

COMMON_PASSWORDS = [
    '123456',
    '000000',
    '111111',
    '222222',
    '333333',
    '444444',
    '555555',
    '666666',
    '777777',
    '888888',
    '999999',
    'abcdef',
    'qwerty',
    'abc123',
    'pass12',
    'mars01',
]


def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60

    return f'{hours:02d}:{minutes:02d}:{secs:05.2f}'


def print_progress(attempts, password, start_time):
    elapsed_time = time.time() - start_time

    print(
        f'반복 횟수: {attempts}, '
        f'현재 시도 암호: {password}, '
        f'진행 시간: {format_time(elapsed_time)}'
    )


def try_password(zip_file, password):
    password_bytes = password.encode('utf-8')

    try:
        file_list = zip_file.infolist()

        if not file_list:
            return False

        with zip_file.open(file_list[0], pwd=password_bytes) as file:
            file.read(1)

        return True

    except RuntimeError:
        return False

    except zipfile.BadZipFile:
        return False

    except zlib.error:
        return False

    except OSError:
        return False


def save_password(password):
    try:
        with open(PASSWORD_FILE_NAME, 'w', encoding='utf-8') as file:
            file.write(password)

        print(f'비밀번호 저장 완료: {PASSWORD_FILE_NAME}')

    except OSError as error:
        print(f'비밀번호 저장 중 오류 발생: {error}')


def extract_zip(zip_file, password):
    try:
        os.makedirs(EXTRACT_DIR, exist_ok=True)
        zip_file.extractall(EXTRACT_DIR, pwd=password.encode('utf-8'))

        print(f'압축 해제 완료: {EXTRACT_DIR} 폴더')
        return True

    except OSError as error:
        print(f'압축 해제 폴더 생성 중 오류 발생: {error}')
        return False

    except RuntimeError as error:
        print(f'압축 해제 중 오류 발생: {error}')
        return False

    except zlib.error as error:
        print(f'압축 해제 중 오류 발생: {error}')
        return False


def print_success(password, attempts, start_time):
    elapsed_time = time.time() - start_time

    print('-' * 50)
    print('암호 해제 성공!')
    print(f'비밀번호: {password}')
    print(f'총 반복 횟수: {attempts}')
    print(f'총 진행 시간: {format_time(elapsed_time)}')


def try_common_passwords(zip_file, start_time):
    attempts = 0

    print('자주 사용하는 비밀번호를 먼저 시도합니다.')

    for password in COMMON_PASSWORDS:
        attempts += 1

        if try_password(zip_file, password):
            return password, attempts

    print('자주 사용하는 비밀번호에서는 찾지 못했습니다.')
    print('-' * 50)

    return None, attempts


def brute_force_password(zip_file, start_time, start_attempts):
    attempts = start_attempts

    print('전체 조합 대입을 시작합니다.')

    for candidate in itertools.product(CHARACTERS, repeat=PASSWORD_LENGTH):
        password = ''.join(candidate)
        attempts += 1

        if attempts % PRINT_INTERVAL == 0:
            print_progress(attempts, password, start_time)

        if try_password(zip_file, password):
            return password, attempts

    return None, attempts


def unlock_zip():
    start_time = time.time()

    print('zip 암호 해제를 시작합니다.')
    print(
        f'시작 시간: '
        f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))}'
    )
    print(f'암호 조건: 숫자 + 소문자 알파벳, {PASSWORD_LENGTH}자리')
    print('-' * 50)

    if not os.path.exists(ZIP_FILE_NAME):
        print(f'{ZIP_FILE_NAME} 파일을 찾을 수 없습니다.')
        return None

    try:
        with zipfile.ZipFile(ZIP_FILE_NAME, 'r') as zip_file:
            password, attempts = try_common_passwords(zip_file, start_time)

            if password is None:
                password, attempts = brute_force_password(
                    zip_file,
                    start_time,
                    attempts
                )

            if password is not None:
                print_success(password, attempts, start_time)
                save_password(password)
                extract_zip(zip_file, password)

                return password

    except FileNotFoundError:
        print(f'{ZIP_FILE_NAME} 파일을 찾을 수 없습니다.')

    except zipfile.BadZipFile:
        print('올바른 zip 파일이 아닙니다.')

    except OSError as error:
        print(f'파일 처리 중 오류 발생: {error}')

    print('암호를 찾지 못했습니다.')
    return None


if __name__ == '__main__':
    unlock_zip()