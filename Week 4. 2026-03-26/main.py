# =============================================================================
# 화성 기지 재고 관리 시스템
# 목적: 화성 기지에 적재된 물질들의 인화성을 분석하고, 위험 물질을 분류·저장·보고
# 흐름: CSV 읽기 → 인화성 정렬 → 위험 물질 필터링 → CSV/BIN 저장 → 보고서 작성
# =============================================================================

import pickle  # 파이썬 객체를 이진 파일로 저장/불러오기 위한 표준 라이브러리

# ── 파일 경로 상수 ─────────────────────────────────────────────────────────────
REPORT_FILE_PATH = 'Mars_Base_Inventory_Report.md'   # 최종 마크다운 보고서 저장 경로
CSV_FILE_PATH    = 'Mars_Base_Inventory_List.csv'    # 원본 재고 CSV 파일 경로
BIN_FILE_PATH    = 'Mars_Base_Inventory_List.bin'    # 정렬된 전체 목록을 저장할 이진 파일 경로
DANGER_CSV_PATH  = 'Mars_Base_Inventory_danger.csv'  # 위험 물질만 따로 저장할 CSV 경로

# ── 분석 기준 상수 ─────────────────────────────────────────────────────────────
FLAMMABILITY_INDEX = 4    # CSV에서 인화성 값이 위치한 열 번호 (0부터 시작, 5번째 열)
DANGER_THRESHOLD   = 0.7  # 이 값 이상이면 '위험 물질'로 분류

# =============================================================================
# 함수 0. read_csv  ─  CSV 파일을 읽어 출력
# # =============================================================================
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


# =============================================================================
# 함수 1. list_csv  ─  CSV 파일을 읽어 2차원 리스트로 반환
# =============================================================================
def list_csv(file_name):
    """CSV 파일을 읽어서 2차원 리스트로 반환합니다."""

    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            # 파일의 모든 줄을 읽고, 각 줄 앞뒤의 공백·줄바꿈을 제거
            words = [word.strip() for word in file.readlines()]

    # ── 예외 처리 ──────────────────────────────────────────────────────────────
    except FileNotFoundError:
        # 파일 자체가 없을 때: 이후 모든 작업이 불가능하므로 가장 먼저 처리
        print(f'[오류] 파일을 찾을 수 없습니다: {file_name}')
        return []

    except PermissionError:
        # 읽기 권한이 없을 때: 화성 기지처럼 제한된 환경에서 발생 가능
        print(f'[오류] 파일 읽기 권한이 없습니다: {file_name}')
        return []

    except UnicodeDecodeError:
        # UTF-8로 읽기 실패 시: 한글 포함 파일이 CP949로 저장된 경우를 대비해 재시도
        print('[오류] UTF-8 인코딩 실패, CP949로 재시도합니다...')
        try:
            with open(file_name, 'r', encoding='cp949') as file:
                words = [word.strip() for word in file.readlines()]
        except Exception as e:
            print(f'[오류] 재시도 실패: {e}')
            return []

    except Exception as e:
        # 위에서 잡지 못한 모든 예외를 마지막 안전망으로 처리
        print(f'[오류] 파일 읽기 중 예외 발생: {e}')
        return []

    # 파일은 열렸지만 내용이 아예 없는 경우 → 빈 리스트 반환
    if not words:
        print(f'[오류] 파일이 비어있습니다: {file_name}')
        return []

    # 각 줄을 쉼표(,)로 분리해 2차원 리스트(행 × 열)로 변환
    list_word = []
    for word in words:
        row = word.strip().split(',')  # "Water,1.0,1.0,3,0.2" → ['Water','1.0','1.0','3','0.2']
        list_word.append(row)

    return list_word  # [[헤더행], [데이터행1], [데이터행2], ...] 형태로 반환


# =============================================================================
# 함수 2. sort_by_flammability  ─  인화성 기준 내림차순 정렬
# =============================================================================
def sort_by_flammability(list_word):
    """인화성 기준 내림차순 정렬한 리스트를 반환합니다."""

    # 이전 단계(read_csv)가 실패하면 빈 리스트가 넘어오므로 먼저 확인
    if not list_word or len(list_word) < 2:
        print('[오류] 정렬할 데이터가 없습니다.')
        return []

    header = list_word[0]   # 첫 번째 행은 헤더(컬럼명)이므로 분리해 보존
    data   = list_word[1:]  # 실제 데이터 행들만 추출

    # 인화성 값이 숫자로 변환 가능한 '유효한 행'만 골라냄
    valid_data = []
    for row in data:
        try:
            if len(row) < FLAMMABILITY_INDEX + 1:
                # 열 개수가 부족한 불완전한 행은 건너뜀 (데이터 오염 방지)
                print(f'[경고] 컬럼 수 부족으로 건너뜁니다: {row}')
                continue
            float(row[FLAMMABILITY_INDEX])  # 숫자 변환 가능 여부만 확인 (결과는 버림)
            valid_data.append(row)
        except ValueError:
            # 인화성 열에 숫자가 아닌 값이 들어있는 행은 정렬 불가 → 건너뜀
            print(f'[경고] 인화성 값이 숫자가 아닙니다. 건너뜁니다: {row}')

    # lambda로 인화성 열을 float 변환 후 비교 → reverse=True 로 높은 순 정렬
    valid_data.sort(key=lambda x: float(x[FLAMMABILITY_INDEX]), reverse=True)

    return [header] + valid_data  # 헤더를 맨 앞에 다시 붙여서 반환


# =============================================================================
# 함수 3. filter_danger  ─  인화성 0.7 이상인 위험 물질만 필터링
# =============================================================================
def filter_danger(list_word):
    """인화성 0.7 이상인 목록만 필터링해서 반환합니다."""

    # 정렬 단계가 실패했을 경우 빈 리스트가 넘어올 수 있으므로 확인
    if not list_word:
        print('[오류] 분류할 데이터가 없습니다.')
        return []

    sub_list = []
    for row in list_word[1:]:  # 헤더(0번 인덱스)를 제외하고 데이터 행만 순회
        try:
            if float(row[FLAMMABILITY_INDEX]) >= DANGER_THRESHOLD:
                sub_list.append(row)  # 기준값 이상이면 위험 목록에 추가
        except ValueError:
            # 인화성 값이 숫자로 변환 안 되는 행은 건너뜀
            print(f'[경고] 인화성 값 변환 실패, 건너뜁니다: {row}')
        except IndexError:
            # 열 개수가 부족한 행이 섞여 있을 경우 건너뜀
            print(f'[경고] 컬럼 수 부족, 건너뜁니다: {row}')

    # 위험 물질이 하나도 없으면 저장 작업 불필요 → 안내 메시지 출력
    if not sub_list:
        print('[안내] 인화성 0.7 이상인 위험 물질이 없습니다.')

    return sub_list  # 헤더 없이 위험 물질 데이터 행만 반환


# =============================================================================
# 함수 4. save_csv  ─  리스트를 CSV 파일로 저장
# =============================================================================
def save_csv(data, file_path):
    """리스트를 CSV 파일로 저장합니다."""

    # 저장할 데이터가 없으면 빈 파일이 생성되는 것을 방지
    if not data:
        print('[안내] 저장할 데이터가 없습니다.')
        return

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            for row in data:
                f.write(','.join(row) + '\n')  # 각 행의 요소를 쉼표로 합쳐 한 줄로 저장
        print(f'---[CSV 저장 완료: {file_path}]---')

    except PermissionError:
        # 화성 기지 환경에서 쓰기 권한이 제한될 수 있음
        print(f'[오류] 파일 쓰기 권한이 없습니다: {file_path}')
    except OSError as e:
        # 디스크 용량 부족, 잘못된 경로 등 파일 시스템 수준의 오류
        print(f'[오류] CSV 저장 중 오류 발생: {e}')


# =============================================================================
# 함수 5. save_bin  ─  리스트를 이진 파일(pickle)로 저장 + 원본 바이트 출력
# =============================================================================
def save_bin(data, file_path):
    """리스트를 이진 파일(pickle)로 저장합니다."""

    # 저장할 데이터가 없으면 빈 bin 파일 생성을 방지
    if not data:
        print('[안내] 저장할 데이터가 없습니다.')
        return

    try:
        with open(file_path, 'wb') as bin_file:
            pickle.dump(data, bin_file)  # 파이썬 객체를 이진 직렬화하여 저장
        print(f'---[BIN 저장 완료: {file_path}]---')

        # pickle.load() 대신 raw read()로 이진 원본 바이트 그대로 출력 (학습/확인 목적)
        with open('Mars_Base_Inventory_List.bin', 'rb') as bin_file:
            raw = bin_file.read()

        print('---[이진 데이터 원본]---')
        print(raw)  # b'\x80\x05\x95...' 형태의 바이트 문자열이 출력됨

    except PermissionError:
        print(f'[오류] 파일 쓰기 권한이 없습니다: {file_path}')
    except OSError as e:
        print(f'[오류] BIN 저장 중 오류 발생: {e}')


# =============================================================================
# 함수 6. read_bin  ─  이진 파일을 읽어 리스트로 복원 후 출력
# =============================================================================
def read_bin(file_path):
    """이진 파일을 읽어서 리스트로 복원 후 출력합니다."""

    try:
        with open(file_path, 'rb') as bin_file:
            data = pickle.load(bin_file)  # 이진 파일을 역직렬화해 원래 파이썬 리스트로 복원

        print('---[BIN 파일을 텍스트로 복원]---')
        for row in data:
            print(','.join(row))  # 복원된 각 행을 쉼표로 합쳐 CSV처럼 출력

        return data

    except FileNotFoundError:
        # save_bin()이 실행되기 전에 read_bin()이 호출되는 순서 오류 방지
        print(f'[오류] BIN 파일을 찾을 수 없습니다: {file_path}')
        return []
    except pickle.UnpicklingError:
        # 파일이 손상되었거나 pickle 형식이 아닌 다른 파일을 읽으려 할 때
        print('[오류] BIN 파일이 손상되어 읽을 수 없습니다.')
        return []
    except PermissionError:
        print(f'[오류] BIN 파일 읽기 권한이 없습니다: {file_path}')
        return []
    except OSError as e:
        print(f'[오류] BIN 읽기 중 오류 발생: {e}')
        return []


# =============================================================================
# 함수 7. write_report  ─  분석 결과를 마크다운 보고서로 저장
# =============================================================================
def write_report(inventory, sorted_list, sub_list):
    """분석 결과를 마크다운 보고서로 저장합니다."""

    # inventory 또는 sorted_list 중 하나라도 없으면 보고서 작성 불가
    if not inventory or not sorted_list:
        print('[오류] 보고서 작성에 필요한 데이터가 없습니다.')
        return

    lines = []  # 보고서의 각 줄을 담을 리스트 (나중에 한꺼번에 파일에 씀)

    # ── 제목 및 구분선 ─────────────────────────────────────────────────────────
    lines.append('# 화성 기지 인화성 물질 분류 보고서\n\n')
    lines.append('---\n\n')

    # ── 섹션 1: 분석 개요 (전체/위험/안전 물질 수 요약 테이블) ──────────────────
    lines.append('## 1. 분석 개요\n\n')
    lines.append('| 항목 | 내용 |\n')
    lines.append('|------|------|\n')
    lines.append(f'| 전체 적재 물질 수 | {len(inventory) - 1} 종 |\n')   # 헤더 행 제외
    lines.append(f'| 인화성 위험 기준 | {DANGER_THRESHOLD} 이상 |\n')
    lines.append(f'| 위험 물질 수 | {len(sub_list)} 종 |\n')
    lines.append(f'| 안전 물질 수 | {len(inventory) - 1 - len(sub_list)} 종 |\n')
    lines.append('\n')

    # ── 섹션 2: 최고 위험 물질 (정렬이 완료된 상태이므로 sub_list[0]이 가장 위험) ─
    lines.append('## 2. 최고 위험 물질\n\n')
    if sub_list:
        top = sub_list[0]  # 인화성 내림차순 정렬 후 필터링했으므로 첫 번째가 가장 위험
        lines.append(f'- **물질명**: {top[0]}\n')
        lines.append(f'- **인화성 지수**: {top[FLAMMABILITY_INDEX]}\n')
        lines.append(f'- **비중**: {top[1]}\n')
        lines.append(f'- **강도**: {top[3]}\n')
    else:
        lines.append('- 위험 물질이 없습니다.\n')
    lines.append('\n')

    # ── 섹션 3: 위험 물질 전체 목록 테이블 ────────────────────────────────────
    lines.append(f'## 3. 위험 물질 목록 (인화성 {DANGER_THRESHOLD} 이상)\n\n')
    lines.append('| 물질명 | 비중 | Specific Gravity | 강도 | 인화성 지수 |\n')
    lines.append('|--------|------|-----------------|------|------------|\n')
    for row in sub_list:
        lines.append(f'| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} |\n')
    lines.append('\n')

    # ── 섹션 4: 전체 물질 목록 (위험 여부 표시 포함) ───────────────────────────
    lines.append('## 4. 전체 물질 목록 (인화성 높은 순)\n\n')
    lines.append('| 물질명 | 비중 | Specific Gravity | 강도 | 인화성 지수 | 위험 여부 |\n')
    lines.append('|--------|------|-----------------|------|------------|----------|\n')
    for row in sorted_list[1:]:  # 헤더 행(인덱스 0) 제외하고 데이터만 순회
        try:
            # 인화성 기준 이상이면 위험 이모지, 미만이면 안전 이모지 표시
            danger = '⚠️ 위험' if float(row[FLAMMABILITY_INDEX]) >= DANGER_THRESHOLD else '✅ 안전'
        except ValueError:
            danger = '❓ 불명'  # 인화성 값이 숫자로 변환 안 될 경우
        lines.append(f'| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {danger} |\n')
    lines.append('\n')

    # ── 섹션 5: 결론 (위험 물질 유무에 따라 내용 분기) ────────────────────────
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

    # ── 파일 저장 ──────────────────────────────────────────────────────────────
    try:
        with open(REPORT_FILE_PATH, 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(line)  # lines 리스트의 각 줄을 순서대로 파일에 씀
        print(f'---[보고서 저장 완료: {REPORT_FILE_PATH}]---')

    except PermissionError:
        print(f'[오류] 보고서 파일 쓰기 권한이 없습니다: {REPORT_FILE_PATH}')
    except OSError as e:
        print(f'[오류] 보고서 저장 중 오류 발생: {e}')


# =============================================================================
# main  ─  전체 파이프라인을 순서대로 실행
# =============================================================================
def main():
    # ── 0단계: CSV 읽기 및 전체 내용 출력 ─────────────────────────────────────
    print('---[전체 내용 출력]---')
    read_csv(CSV_FILE_PATH)

    # ── 1단계: CSV를 List로 출력 ─────────────────────────────────────
    print('---[2차열 List로 출력]---')
    inventory = list_csv(CSV_FILE_PATH)
    if not inventory:
        # CSV 로드가 실패하면 이후 작업이 전혀 불가능하므로 즉시 종료
        print('[오류] 데이터 로드 실패. 프로그램을 종료합니다.')
        return
    for row in inventory:
        print(row)

    # ── 2단계: 인화성 내림차순 정렬 ───────────────────────────────────────────
    print('\n---[인화성 높은 순으로 나열]---')
    sorted_list = sort_by_flammability(inventory)
    if not sorted_list:
        print('[오류] 정렬 실패. 프로그램을 종료합니다.')
        return
    for row in sorted_list:
        print(row)

    # ── 3단계: 위험 물질 필터링 (인화성 0.7 이상) ─────────────────────────────
    print(f'\n---[인화성 {DANGER_THRESHOLD} 이상인 목록만 출력]---')
    sub_list = filter_danger(sorted_list)
    for row in sub_list:
        print(row)

    # ── 4단계: 위험 물질 목록을 별도 CSV로 저장 ───────────────────────────────
    save_csv(sub_list, DANGER_CSV_PATH)

    # ── 5단계: 전체 정렬 목록을 이진 파일(BIN)으로 저장 ──────────────────────
    save_bin(sorted_list, BIN_FILE_PATH)

    # ── 6단계: BIN 파일을 다시 읽어 텍스트로 복원·출력 ───────────────────────
    read_bin(BIN_FILE_PATH)

    # ── 7단계: 전체 분석 결과를 마크다운 보고서로 저장 ───────────────────────
    write_report(inventory, sorted_list, sub_list)


# 이 파일이 직접 실행될 때만 main()을 호출 (다른 파일에서 import 시에는 실행 안 됨)
if __name__ == '__main__':
    main()