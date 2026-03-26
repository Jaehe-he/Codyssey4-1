import pickle

CSV_FILE_PATH = 'Mars_Base_Inventory_List.csv'

def Justprint(file_name):
    """csv 파일을 열고 출력만 합니다."""
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

def Listprint(file_name):
    """csv 파일을 객체 List 형태로 반환"""
    try:
        # 파일 열기
        with open(file_name, 'r', encoding='utf-8') as file:
            words=[word.strip() for word in file.readlines()]

        # 내용 출력
        print('---[리스트 출력]---')
        list_word=[]
        for word in words:
            row = word.strip().split(',')
            list_word.append(row)
        
        return list_word
    except FileNotFoundError:
        print(f"Error: '{file_name}' 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f'처리 중 예외 발생: {e}')    

def SortList(list_word):
    """Listprint를 인화성 높은 순으로 나열"""

    print('---[인화성 높은 순으로 나열]---')
    header = list_word[0] #헤더 분리
    data = list_word[1:] #데이터만

    data.sort(key=lambda x: float(x[4]), reverse=True) #인화성 기준 정렬

    return [header] + data #헤더+정렬 데이터 반환

def SubPrint(data):
    """인화성 물질 0.7 이상인 목록만 출력"""
    
    print('---[인화성 0.7 이상인 목록만 출력---]')
    SubList = []

    target = 0.7
    for data in data[1:]:
        if float(data[4]) >= target:
            SubList.append(data)
    
    return SubList

def SaveSupprint(SubList):
    with open('Mars_Base_Inventory_danger.csv', 'w', encoding='utf-8') as sub_file:
        for row in SubList:
            sub_file.write(','.join(row)+'\n')
    
    print('---[CSV 저장 완료]---')

def SaveBinprint(SortList):
    with open('Mars_Base_Inventory_List.bin', 'wb') as bin_file:
        pickle.dump(SortList, bin_file)
    
    print('---[BIN 저장 완료]---')

    # 이진 데이터 그대로 출력 (load 안하고 read로 읽기)
    with open('Mars_Base_Inventory_List.bin', 'rb') as bin_file:
        raw = bin_file.read()   # load() 대신 read() 사용

    print('---[이진 데이터 원본]---')
    print(raw)

def ReadBinPrint(SaveBinprint):
    with open('Mars_Base_Inventory_List.bin', 'rb') as bin_file:
        data = pickle.load(bin_file)

    print('---[BIN 파일을 텍스트로 복원]---')
    for row in data:
        line = ','.join(row)
        print(line)

    return data
        


def main():
    Justprint(CSV_FILE_PATH)
    print()

    inventory=Listprint(CSV_FILE_PATH)
    for row in inventory:
        print(row)
    
    print()
    sorted_list = SortList(inventory)
    for row in sorted_list:
        print(row)

    print()
    sub_list = SubPrint(sorted_list)
    for row in sub_list:
        print(row)

    SaveSupprint(sub_list)

    SaveBinprint(sorted_list)

    ReadBinPrint(sorted_list)
    

if __name__ == '__main__':
    main()