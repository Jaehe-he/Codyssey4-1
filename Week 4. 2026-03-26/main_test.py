REPORT_FILE_PATH = 'Mars_Base_Inventory_Report.md'

import pickle

CSV_FILE_PATH = 'Mars_Base_Inventory_List.csv'
BIN_FILE_PATH = 'Mars_Base_Inventory_List.bin'
DANGER_CSV_PATH = 'Mars_Base_Inventory_danger.csv'
FLAMMABILITY_INDEX = 4
DANGER_THRESHOLD = 0.7

def read_csv(file_name):
    """
    CSV 파일을 읽어 출력합니다.
    """
    try:
        # 파일 열기 (UTF-8 인코딩 준수)
        with open(file_name, 'r', encoding='utf-8') as file:
            lines=[line.strip() for line in file.readlines()]

        # 전체 내용 출력
        print('---[전체 내용 출력]---')
        for line in lines:
            print(line)
    
    except FileNotFoundError:
        print(f"Error: '{file_name}' 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f'처리 중 예외 발생: {e}')



def list_csv(file_name):
    """
    CSV 파일을 읽어서 2차원 리스트로 반환합니다.

    [예외 이유]
    - FileNotFoundError : CSV 파일이 없으면 이후 모든 작업이 불가능하므로 가장 먼저 처리
    - PermissionError   : 화성 기지 환경에서 파일 접근 권한이 제한될 수 있음
    - UnicodeDecodeError: CSV 파일이 UTF-8이 아닌 다른 인코딩일 경우 CP949로 재시도
    - 빈 파일 체크      : 파일은 존재하지만 내용이 없으면 정렬/분류 작업이 불가능
    """
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            words = [word.strip() for word in file.readlines()]

    except FileNotFoundError:
        print(f'[오류] 파일을 찾을 수 없습니다: {file_name}')
        return []
    except PermissionError:
        print(f'[오류] 파일 읽기 권한이 없습니다: {file_name}')
        return []
    except UnicodeDecodeError:
        print('[오류] UTF-8 인코딩 실패, CP949로 재시도합니다...')
        try:
            with open(file_name, 'r', encoding='cp949') as file:
                words = [word.strip() for word in file.readlines()]
        except Exception as e:
            print(f'[오류] 재시도 실패: {e}')
            return []
    except Exception as e:
        print(f'[오류] 파일 읽기 중 예외 발생: {e}')
        return []

    # 빈 파일 체크
    if not words:
        print(f'[오류] 파일이 비어있습니다: {file_name}')
        return []

    list_word = []
    for word in words:
        row = word.strip().split(',')
        list_word.append(row)

    return list_word


def sort_by_flammability(list_word):
    """
    인화성 기준 내림차순 정렬한 리스트를 반환합니다.

    [예외 이유]
    - 빈 리스트 체크  : 앞 단계(read_csv)가 실패하면 빈 리스트가 넘어올 수 있음
    - ValueError      : CSV 인화성 컬럼이 숫자가 아닌 문자일 경우 정렬 자체가 불가능
    - IndexError      : CSV 컬럼 수가 부족한 불량 데이터 행이 있을 경우
    """
    if not list_word or len(list_word) < 2:
        print('[오류] 정렬할 데이터가 없습니다.')
        return []

    header = list_word[0]
    data = list_word[1:]

    valid_data = []
    for row in data:
        try:
            if len(row) < FLAMMABILITY_INDEX + 1:
                print(f'[경고] 컬럼 수 부족으로 건너뜁니다: {row}')
                continue
            float(row[FLAMMABILITY_INDEX])
            valid_data.append(row)
        except ValueError:
            print(f'[경고] 인화성 값이 숫자가 아닙니다. 건너뜁니다: {row}')

    valid_data.sort(key=lambda x: float(x[FLAMMABILITY_INDEX]), reverse=True)

    return [header] + valid_data


def filter_danger(list_word):
    """
    인화성 0.7 이상인 목록만 필터링해서 반환합니다.

    [예외 이유]
    - 빈 리스트 체크 : 정렬 단계가 실패하면 빈 리스트가 넘어올 수 있음
    - ValueError     : 인화성 값이 숫자로 변환 안 될 경우 해당 행만 건너뜀
    - IndexError     : 컬럼 수가 부족한 행이 섞여 있을 경우
    - 빈 결과 체크   : 인화성 0.7 이상 물질이 하나도 없으면 저장/격리 작업 불필요
    """
    if not list_word:
        print('[오류] 분류할 데이터가 없습니다.')
        return []

    sub_list = []
    for row in list_word[1:]:
        try:
            if float(row[FLAMMABILITY_INDEX]) >= DANGER_THRESHOLD:
                sub_list.append(row)
        except ValueError:
            print(f'[경고] 인화성 값 변환 실패, 건너뜁니다: {row}')
        except IndexError:
            print(f'[경고] 컬럼 수 부족, 건너뜁니다: {row}')

    if not sub_list:
        print('[안내] 인화성 0.7 이상인 위험 물질이 없습니다.')

    return sub_list


def save_csv(data, file_path):
    """
    리스트를 CSV 파일로 저장합니다.

    [예외 이유]
    - 빈 데이터 체크 : 저장할 데이터가 없으면 빈 파일이 생성되는 것을 방지
    - PermissionError: 화성 기지 환경에서 파일 쓰기 권한이 제한될 수 있음
    - OSError        : 디스크 용량 부족, 경로 오류 등 파일 시스템 문제
    """
    if not data:
        print('[안내] 저장할 데이터가 없습니다.')
        return

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            for row in data:
                f.write(','.join(row) + '\n')
        print(f'---[CSV 저장 완료: {file_path}]---')

    except PermissionError:
        print(f'[오류] 파일 쓰기 권한이 없습니다: {file_path}')
    except OSError as e:
        print(f'[오류] CSV 저장 중 오류 발생: {e}')


def save_bin(data, file_path):
    """
    리스트를 이진 파일(pickle)로 저장합니다.

    [예외 이유]
    - 빈 데이터 체크 : 저장할 데이터가 없으면 빈 bin 파일 생성을 방지
    - PermissionError: 파일 쓰기 권한이 없을 경우
    - OSError        : 디스크 용량 부족, 경로 오류 등 파일 시스템 문제
    """
    if not data:
        print('[안내] 저장할 데이터가 없습니다.')
        return

    try:
        with open(file_path, 'wb') as bin_file:
            pickle.dump(data, bin_file)
        print(f'---[BIN 저장 완료: {file_path}]---')

        with open('Mars_Base_Inventory_List.bin', 'rb') as bin_file:
            raw = bin_file.read()   # load() 대신 read() 사용

        print('---[이진 데이터 원본]---')
        print(raw)

    except PermissionError:
        print(f'[오류] 파일 쓰기 권한이 없습니다: {file_path}')
    except OSError as e:
        print(f'[오류] BIN 저장 중 오류 발생: {e}')


def read_bin(file_path):
    """
    이진 파일을 읽어서 리스트로 복원 후 출력합니다.

    [예외 이유]
    - FileNotFoundError  : bin 파일이 저장되기 전에 읽으려 할 경우
    - pickle.UnpicklingError: bin 파일이 손상되거나 다른 형식일 경우
    - PermissionError    : 파일 읽기 권한이 없을 경우
    - OSError            : 파일 시스템 문제
    """
    try:
        with open(file_path, 'rb') as bin_file:
            data = pickle.load(bin_file)

        print('---[BIN 파일을 텍스트로 복원]---')
        for row in data:
            print(','.join(row))

        return data

    except FileNotFoundError:
        print(f'[오류] BIN 파일을 찾을 수 없습니다: {file_path}')
        return []
    except pickle.UnpicklingError:
        print('[오류] BIN 파일이 손상되어 읽을 수 없습니다.')
        return []
    except PermissionError:
        print(f'[오류] BIN 파일 읽기 권한이 없습니다: {file_path}')
        return []
    except OSError as e:
        print(f'[오류] BIN 읽기 중 오류 발생: {e}')
        return []

def write_report(inventory, sorted_list, sub_list):
    """
    분석 결과를 마크다운 보고서로 저장합니다.

    [예외 이유]
    - 빈 데이터 체크 : 데이터가 없으면 보고서 작성 불가
    - PermissionError: 파일 쓰기 권한이 없을 경우
    - OSError        : 디스크 용량 부족 등 파일 시스템 문제
    """
    if not inventory or not sorted_list:
        print('[오류] 보고서 작성에 필요한 데이터가 없습니다.')
        return

    lines = []

    # 제목
    lines.append('# 화성 기지 인화성 물질 분류 보고서\n\n')
    lines.append('---\n\n')

    # 1. 분석 개요
    lines.append('## 1. 분석 개요\n\n')
    lines.append('| 항목 | 내용 |\n')
    lines.append('|------|------|\n')
    lines.append(f'| 전체 적재 물질 수 | {len(inventory) - 1} 종 |\n')
    lines.append(f'| 인화성 위험 기준 | {DANGER_THRESHOLD} 이상 |\n')
    lines.append(f'| 위험 물질 수 | {len(sub_list)} 종 |\n')
    lines.append(f'| 안전 물질 수 | {len(inventory) - 1 - len(sub_list)} 종 |\n')
    lines.append('\n')

    # 2. 최고 위험 물질
    lines.append('## 2. 최고 위험 물질\n\n')
    if sub_list:
        top = sub_list[0]  # 이미 인화성 내림차순 정렬된 상태
        lines.append(f'- **물질명**: {top[0]}\n')
        lines.append(f'- **인화성 지수**: {top[FLAMMABILITY_INDEX]}\n')
        lines.append(f'- **비중**: {top[1]}\n')
        lines.append(f'- **강도**: {top[3]}\n')
    else:
        lines.append('- 위험 물질이 없습니다.\n')
    lines.append('\n')

    # 3. 위험 물질 목록 (인화성 0.7 이상)
    lines.append(f'## 3. 위험 물질 목록 (인화성 {DANGER_THRESHOLD} 이상)\n\n')
    lines.append('| 물질명 | 비중 | Specific Gravity | 강도 | 인화성 지수 |\n')
    lines.append('|--------|------|-----------------|------|------------|\n')
    for row in sub_list:
        lines.append(f'| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} |\n')
    lines.append('\n')

    # 4. 전체 물질 목록 (인화성 높은 순)
    lines.append('## 4. 전체 물질 목록 (인화성 높은 순)\n\n')
    lines.append('| 물질명 | 비중 | Specific Gravity | 강도 | 인화성 지수 | 위험 여부 |\n')
    lines.append('|--------|------|-----------------|------|------------|----------|\n')
    for row in sorted_list[1:]:  # 헤더 제외
        try:
            danger = '⚠️ 위험' if float(row[FLAMMABILITY_INDEX]) >= DANGER_THRESHOLD else '✅ 안전'
        except ValueError:
            danger = '❓ 불명'
        lines.append(f'| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {danger} |\n')
    lines.append('\n')

    # 5. 결론
    lines.append('## 5. 결론\n\n')
    if sub_list:
        lines.append(
            f'화성 기지 내 전체 {len(inventory) - 1}종의 적재 물질 중 '
            f'인화성 지수 {DANGER_THRESHOLD} 이상인 위험 물질은 총 **{len(sub_list)}종**입니다.\n\n'
        )
        lines.append(
            f'가장 위험한 물질은 **{sub_list[0][0]}** (인화성 지수: {sub_list[0][FLAMMABILITY_INDEX]})으로 '
            f'즉시 기지 외부로 격리가 필요합니다.\n\n'
        )
        lines.append(
            f'위험 물질 목록은 **{DANGER_CSV_PATH}** 파일에 저장되었으며, '
            f'전체 정렬 목록은 **{BIN_FILE_PATH}** 파일에 이진 형태로 저장되었습니다.\n'
        )
    else:
        lines.append('화성 기지 내 인화성 위험 물질이 발견되지 않았습니다.\n')

    # 파일 저장
    try:
        with open(REPORT_FILE_PATH, 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(line)
        print(f'---[보고서 저장 완료: {REPORT_FILE_PATH}]---')

    except PermissionError:
        print(f'[오류] 보고서 파일 쓰기 권한이 없습니다: {REPORT_FILE_PATH}')
    except OSError as e:
        print(f'[오류] 보고서 저장 중 오류 발생: {e}')


def main():
    # 1단계 - CSV 전체 내용 출력
    print('---[전체 내용 출력]---')
    read_csv(CSV_FILE_PATH)

    # 1-1단계 - CSV를 list로 반환
    print('---[2차원 List로 반환]---')
    inventory = list_csv(CSV_FILE_PATH)
    if not inventory:
        print('[오류] 데이터 로드 실패. 프로그램을 종료합니다.')
        return
    for row in inventory:
        print(row)

    # 2단계 - 인화성 높은 순 정렬
    print('\n---[인화성 높은 순으로 나열]---')
    sorted_list = sort_by_flammability(inventory)
    if not sorted_list:
        print('[오류] 정렬 실패. 프로그램을 종료합니다.')
        return
    for row in sorted_list:
        print(row)

    # 3단계 - 인화성 0.7 이상 필터링 및 출력
    print(f'\n---[인화성 {DANGER_THRESHOLD} 이상인 목록만 출력]---')
    sub_list = filter_danger(sorted_list)
    for row in sub_list:
        print(row)

    # 4단계 - CSV 저장
    save_csv(sub_list, DANGER_CSV_PATH)

    # 5단계 - BIN 저장
    save_bin(sorted_list, BIN_FILE_PATH)

    # 6단계 - BIN 읽기 및 출력
    read_bin(BIN_FILE_PATH)

    # 7단계 - 보고서 작성
    write_report(inventory, sorted_list, sub_list)


if __name__ == '__main__':
    main()