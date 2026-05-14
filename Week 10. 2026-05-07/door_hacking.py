import itertools
import multiprocessing
import os
import queue
import string
import time
import zipfile
import zlib


ZIP_FILE_NAME = 'emergency_storage_key.zip'
PASSWORD_FILE_NAME = 'password.txt'
EXTRACT_DIR = 'emergency_storage_key'

PASSWORD_LENGTH = 6
DIGITS = string.digits
LETTERS = string.ascii_lowercase
CHARACTERS = DIGITS + LETTERS

WORKER_COUNT = max(1, multiprocessing.cpu_count() - 1)
QUEUE_SIZE = 5000
PROGRESS_INTERVAL = 2


STORY_WORDS = [
    'coffee',
    'oxygen',
    'storage',
    'emerge',
    'mars',
    'base',
    'door',
    'key',
    'food',
    'water',
    'rescue',
    'space',
    'human',
    'life',
    'open',
    'lock',
]


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
    '654321',
    '987654',
    'abcdef',
    'qwerty',
    'abc123',
    '123abc',
    '260507',
    '050726',
    '202605',
]


def format_time(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)

    return f'{minutes}분 {secs}초'


def find_target_file(zip_file):
    target_file = None

    for file_info in zip_file.infolist():
        if file_info.filename.endswith('/'):
            continue

        if file_info.file_size == 0:
            continue

        if target_file is None:
            target_file = file_info
            continue

        if file_info.compress_size < target_file.compress_size:
            target_file = file_info

    if target_file is None:
        return None

    return target_file.filename


def check_zip_file():
    if not os.path.exists(ZIP_FILE_NAME):
        print(f'[오류] 파일을 찾을 수 없습니다: {ZIP_FILE_NAME}')
        return None

    try:
        with zipfile.ZipFile(ZIP_FILE_NAME, 'r') as zip_file:
            return find_target_file(zip_file)

    except zipfile.BadZipFile:
        print('[오류] 정상적인 ZIP 파일이 아닙니다.')

    except OSError as error:
        print('[오류] ZIP 파일을 여는 중 문제가 발생했습니다.')
        print(error)

    return None


def try_password(zip_file, target_file, password):
    try:
        with zip_file.open(target_file, pwd=password.encode('utf-8')) as file:
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


def make_priority_passwords():
    used = set()

    for password in COMMON_PASSWORDS:
        if len(password) == PASSWORD_LENGTH and password not in used:
            used.add(password)
            yield password

    for word in STORY_WORDS:
        if len(word) == PASSWORD_LENGTH and word not in used:
            used.add(word)
            yield word

    for word in STORY_WORDS:
        if len(word) >= PASSWORD_LENGTH:
            continue

        remain = PASSWORD_LENGTH - len(word)

        for number in range(10 ** remain):
            password = word + str(number).zfill(remain)

            if password not in used:
                used.add(password)
                yield password

        for number in range(10 ** remain):
            password = str(number).zfill(remain) + word

            if password not in used:
                used.add(password)
                yield password

    for number in range(1000000):
        password = str(number).zfill(6)

        if password not in used:
            used.add(password)
            yield password


def number_to_base36_password(number):
    indexes = []

    for _ in range(PASSWORD_LENGTH):
        indexes.append(number % len(CHARACTERS))
        number //= len(CHARACTERS)

    indexes.reverse()

    return ''.join(CHARACTERS[index] for index in indexes)


def make_bruteforce_passwords():
    total = len(CHARACTERS) ** PASSWORD_LENGTH

    for number in range(total):
        yield number_to_base36_password(number)


def password_producer(work_queue, found_event, mode):
    if mode == 'priority':
        generator = make_priority_passwords()
    else:
        generator = make_bruteforce_passwords()

    for password in generator:
        if found_event.is_set():
            break

        work_queue.put(password)

    for _ in range(WORKER_COUNT):
        work_queue.put(None)


def password_worker(
    worker_id,
    work_queue,
    result_queue,
    found_event,
    target_file
):
    attempts = 0
    last_print_time = time.time()
    start_time = time.time()

    try:
        with zipfile.ZipFile(ZIP_FILE_NAME, 'r') as zip_file:
            while not found_event.is_set():
                try:
                    password = work_queue.get(timeout=1)

                except queue.Empty:
                    continue

                if password is None:
                    break

                attempts += 1

                if try_password(zip_file, target_file, password):
                    found_event.set()
                    result_queue.put((worker_id, password, attempts))
                    break

                now = time.time()

                if now - last_print_time >= PROGRESS_INTERVAL:
                    elapsed = now - start_time

                    print(
                        f'[worker-{worker_id}] '
                        f'시도={attempts:,}회 | '
                        f'현재={password} | '
                        f'경과={format_time(elapsed)}',
                        flush=True
                    )

                    last_print_time = now

    except OSError as error:
        print(f'[worker-{worker_id}] ZIP 파일 처리 오류: {error}')


def run_stage(stage_name, mode, target_file):
    print('=' * 60)
    print(f'{stage_name} 시작')
    print(f'작업 방식: 큐 기반 멀티프로세싱')
    print(f'사용 프로세스 수: {WORKER_COUNT}')
    print('=' * 60)

    work_queue = multiprocessing.Queue(maxsize=QUEUE_SIZE)
    result_queue = multiprocessing.Queue()
    found_event = multiprocessing.Event()

    producer = multiprocessing.Process(
        target=password_producer,
        args=(work_queue, found_event, mode)
    )

    workers = []

    for worker_id in range(1, WORKER_COUNT + 1):
        process = multiprocessing.Process(
            target=password_worker,
            args=(
                worker_id,
                work_queue,
                result_queue,
                found_event,
                target_file
            )
        )

        workers.append(process)

    start_time = time.time()

    producer.start()

    for process in workers:
        process.start()

    password = None
    found_worker_id = None
    found_attempts = 0

    try:
        while True:
            if not result_queue.empty():
                found_worker_id, password, found_attempts = result_queue.get()
                found_event.set()
                break

            if not producer.is_alive() and not any(
                process.is_alive() for process in workers
            ):
                break

            elapsed = time.time() - start_time

            print(
                f'\r[단계 진행 중] {stage_name} | '
                f'경과={format_time(elapsed)}',
                end='',
                flush=True
            )

            time.sleep(1)

    except KeyboardInterrupt:
        print('\n[중단] 사용자가 작업을 중단했습니다.')
        found_event.set()

    if producer.is_alive():
        producer.terminate()

    producer.join()

    for process in workers:
        if process.is_alive():
            process.terminate()

    for process in workers:
        process.join()

    print()

    if password is not None:
        elapsed = time.time() - start_time

        print('[성공] 암호 발견')
        print(f'[단계] {stage_name}')
        print(f'[worker] {found_worker_id}')
        print(f'[worker 반복 횟수] {found_attempts:,}')
        print(f'[암호] {password}')
        print(f'[단계 소요 시간] {format_time(elapsed)}')

        return password

    print(f'[종료] {stage_name}에서 찾지 못했습니다.')
    return None


def save_password(password):
    try:
        with open(PASSWORD_FILE_NAME, 'w', encoding='utf-8') as file:
            file.write(password)

        print(f'[저장] {PASSWORD_FILE_NAME} 저장 완료')

    except OSError as error:
        print('[오류] password.txt 저장 실패')
        print(error)


def extract_zip(password):
    try:
        os.makedirs(EXTRACT_DIR, exist_ok=True)

        with zipfile.ZipFile(ZIP_FILE_NAME, 'r') as zip_file:
            zip_file.extractall(
                EXTRACT_DIR,
                pwd=password.encode('utf-8')
            )

        print(f'[압축 해제] {EXTRACT_DIR} 폴더에 저장 완료')

    except OSError as error:
        print('[오류] 압축 해제 중 파일 오류 발생')
        print(error)

    except RuntimeError as error:
        print('[오류] 압축 해제 중 암호 오류 발생')
        print(error)

    except zlib.error as error:
        print('[오류] 압축 해제 중 압축 데이터 오류 발생')
        print(error)


def unlock_zip():
    total_start_time = time.time()
    start_text = time.strftime(
        '%Y-%m-%d %H:%M:%S',
        time.localtime(total_start_time)
    )

    print('=' * 60)
    print('Emergency Storage ZIP Password Unlocker')
    print('=' * 60)
    print(f'[시작 시간] {start_text}')
    print(f'[대상 파일] {ZIP_FILE_NAME}')
    print(f'[암호 조건] 숫자 + 소문자 알파벳 {PASSWORD_LENGTH}자리')
    print('-' * 60)

    target_file = check_zip_file()

    if target_file is None:
        return None

    print(f'[검사 대상 파일] {target_file}')
    print('-' * 60)

    password = run_stage(
        '1단계: 스토리 기반 우선 후보',
        'priority',
        target_file
    )

    if password is None:
        password = run_stage(
            '2단계: 전체 브루트포스',
            'bruteforce',
            target_file
        )

    if password is None:
        print('[실패] 암호를 찾지 못했습니다.')
        return None

    total_elapsed = time.time() - total_start_time

    print('=' * 60)
    print('[최종 성공]')
    print(f'[비밀번호] {password}')
    print(f'[총 소요 시간] {format_time(total_elapsed)}')
    print('=' * 60)

    save_password(password)
    extract_zip(password)

    return password


if __name__ == '__main__':
    multiprocessing.freeze_support()
    unlock_zip()