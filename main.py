LOG_FILE_PATH = 'mission_computer_main.log'
EXAM_FILE_PATH = 'mission_computer_main_example.log'


#def mission_computer_main(file_name):
#    with open(file_name, "r", encoding="utf-8") as f:
#        for line in f:
#            print(line, end="")


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

#3. 각 문장에 점수를 매기고 -일 경우 그 줄 출력
def value_mission_log(value):
    print("각 문장에 점수를 매기고 -일 경우 그 줄을 출력해라")
    score = 0
    save_line = []

    negative_words = ['unstable', 'explosion', 'powered down']

    with open("mission_computer_main.log", "r", encoding="utf-8") as f:
        for line in f:
            line_lower = line.lower()
            found = False #중복 제거
                
            for word in negative_words:
                if word in line_lower:
                    score -= 1
                    found = True

            if found:
                save_line.append(line.strip())
            
        print("최종 점수 : ", score)
        print("문제 있는 줄 : ")
        for l in save_line:
            print(l)


# mission_computer_main_example.log를 따로 만들어서 위험성 추출
def analyze_by_level(example):
    # 단어를 지정하지 않고 'ERROR'나 'CRITICAL' 태그 자체를 탐지
        target_levels = ['WARNING', 'ERROR', 'CRITICAL', 'FATAL']
        with open(example, 'r', encoding='utf-8') as f:
            for line in f:
                if any(level in line for level in target_levels):
                    print(f'[위험 감지]: {line.strip()}')

analyze_by_level('mission_computer_main_example.log')




def main():
#    mission_computer_main(LOG_FILE_PATH)
    process_mission_log(LOG_FILE_PATH)
    print()
    analyze_by_level(EXAM_FILE_PATH)
    print()
    value_mission_log(LOG_FILE_PATH)

if __name__ == '__main__':
    main()

    