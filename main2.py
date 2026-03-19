import sys

def process_mission_log(file_name):
    """
    로그 파일을 읽고 분석하여 출력 및 오류 로그를 추출합니다.
    """
    try:
        # 파일 열기 (UTF-8 인코딩 준수)
        with open(file_name, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file.readlines()]

        # 4. 전체 내용 출력
        print('--- [전체 로그 출력] ---')
        for line in lines:
            print(line)

        # [보너스 1] 시간 역순 정렬 출력
        print('\n--- [시간 역순 정렬 출력] ---')
        reversed_lines = sorted(lines[1:], reverse=True)  # 헤더 제외 정렬
        for line in reversed_lines:
            print(line)

        # [보너스 2] 문제가 되는 부분(unstable, explosion)만 추출하여 저장
        error_logs = [line for line in lines if 'unstable' in line or 'explosion' in line]
        with open('error_analysis.txt', 'w', encoding='utf-8') as error_file:
            for error in error_logs:
                error_file.write(error + '\n')
        
        return lines

    except FileNotFoundError:
        print(f"Error: '{file_name}' 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f'처리 중 예외 발생: {e}')

if __name__ == '__main__':
    # 메인 실행부
    log_file = 'mission_computer_main.log'
    process_mission_log(log_file)