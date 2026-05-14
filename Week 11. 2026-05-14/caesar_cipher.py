def read_password_file(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print('오류: password.txt 파일을 찾을 수 없습니다.')
    except PermissionError:
        print('오류: password.txt 파일을 읽을 권한이 없습니다.')
    except UnicodeDecodeError:
        print('오류: 파일 인코딩을 확인해야 합니다.')
    except Exception as error:
        print('알 수 없는 파일 읽기 오류가 발생했습니다:', error)

    return None


def save_result_file(file_name, text):
    try:
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(text)
        print('해독 결과가 result.txt 파일로 저장되었습니다.')
    except PermissionError:
        print('오류: result.txt 파일을 저장할 권한이 없습니다.')
    except Exception as error:
        print('알 수 없는 파일 저장 오류가 발생했습니다:', error)


def decode_character(character, shift):
    if 'a' <= character <= 'z':
        return chr((ord(character) - ord('a') - shift) % 26 + ord('a'))

    if 'A' <= character <= 'Z':
        return chr((ord(character) - ord('A') - shift) % 26 + ord('A'))

    return character


def caesar_cipher_decode(target_text):
    decoded_results = []

    for shift in range(26):
        decoded_text = ''

        for character in target_text:
            decoded_text += decode_character(character, shift)

        decoded_results.append(decoded_text)
        print('[' + str(shift) + '번 자리수]')
        print(decoded_text)
        print('-' * 50)

    return decoded_results


def find_dictionary_match(decoded_results):
    dictionary_words = [
        'the',
        'door',
        'open',
        'password',
        'mars',
        'emergency',
        'storage',
        'key',
        'hello',
        'mission',
        'security'
    ]

    for index, decoded_text in enumerate(decoded_results):
        lower_text = decoded_text.lower()

        for word in dictionary_words:
            if word in lower_text:
                print('사전 단어가 발견되었습니다.')
                print('추천 자리수:', index)
                print('발견 단어:', word)
                print('추천 해독 결과:')
                print(decoded_text)
                return index

    return None


def get_user_shift_number():
    while True:
        user_input = input('저장할 해독 자리수를 입력하세요. 예: 3, 종료: q > ')

        if user_input == 'q':
            return None

        if user_input.isdigit():
            shift_number = int(user_input)

            if 0 <= shift_number <= 25:
                return shift_number

        print('0부터 25 사이의 숫자 또는 q를 입력해야 합니다.')


def main():
    target_text = read_password_file('password.txt')

    if target_text is None:
        return

    decoded_results = caesar_cipher_decode(target_text)

    recommended_shift = find_dictionary_match(decoded_results)

    if recommended_shift is not None:
        user_input = input('추천 결과를 result.txt로 저장할까요? y/n > ')

        if user_input.lower() == 'y':
            save_result_file('result.txt', decoded_results[recommended_shift])
            return

    shift_number = get_user_shift_number()

    if shift_number is None:
        print('프로그램을 종료합니다.')
        return

    save_result_file('result.txt', decoded_results[shift_number])


if __name__ == '__main__':
    main()