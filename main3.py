def analyze_by_level(file_name):
    # 단어를 지정하지 않고 'ERROR'나 'CRITICAL' 태그 자체를 탐지
    target_levels = ['WARNING', 'ERROR', 'CRITICAL', 'FATAL']
    with open(file_name, 'r', encoding='utf-8') as f:
        for line in f:
            if any(level in line for level in target_levels):
                print(f'[위험 감지]: {line.strip()}')

analyze_by_level('mission_computer_main1.log')