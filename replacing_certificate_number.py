import json
from pathlib import Path
import re
import time


def get_files(directory: str = 'response') -> list[Path]:
    """Возвращает список файлов RESPONSE с расширениями, содержащими три цифры."""
    return [file for file in Path(directory).glob('*') if
            re.search(r'\d{3}', file.suffix) and 'new' not in str(file)]


def save_snils_json(input_file: Path, json_output_file: Path) -> dict:
    """Сохраняет СНИЛС в JSON файл."""
    snils_dict = {}
    pattern_snils = re.compile(r'(О\d{3}-\d{3}-\d{3}\s\d{2})')
    pattern_soi = re.compile(r'(СОИ-\d{3})')

    with input_file.open('r', encoding='cp866') as f:
        text = f.read()

    for soi_match in pattern_soi.finditer(text):
        soi_text = text[soi_match.start() - 2595: soi_match.end()]
        snils_matches = pattern_snils.findall(soi_text)
        if snils_matches:
            snils_dict[snils_matches[-1][1:]] = ''
        else:
            print(soi_text)
            raise ValueError('СНИЛС не найден')

    with json_output_file.open('w', encoding='utf-8') as fjs:
        json.dump(snils_dict, fjs, indent=4)

    print(f"Общее количество записанных СНИЛС в JSON: {len(snils_dict)}")
    return snils_dict


def replace_num_cert(input_file: Path, json_templates_file: str) -> list:
    """Заменяет номера сертификатов в тексте."""
    pattern_snils = re.compile(r'(О\d{3}-\d{3}-\d{3}\s\d{2})')
    pattern_soi = re.compile(r'(СОИ-\d{3}-\d{2})')

    with open(json_templates_file, 'r', encoding='utf-8') as f:
        templates = json.load(f)

    with input_file.open('r', encoding='cp866') as f:
        text = f.read()

    split_text = re.split(pattern_snils, text)

    for key in templates.keys():
        try:
            index = split_text.index(f"О{key}")
            old_soi: str= pattern_soi.search(split_text[index + 1]).group() # type: ignore
            split_text[index + 1] = re.sub(old_soi, templates[key][7:], split_text[index + 1])
            print(f"Заменено: {key}")
        except (ValueError, AttributeError):
            print(f"Ошибка для ключа {key}: СОИ не совпадают или не найдено")
            raise

    print(f"Общее количество замен: {len(templates)}")
    return split_text


def create_new_response(original_file: Path, updated_text: list) -> None:
    """Сохраняет новый текст в файл."""
    new_file_path = original_file.with_name(original_file.stem + '_new' + original_file.suffix)
    print('Выполняется сохранение в файл')
    with new_file_path.open('w', encoding='cp866') as f:
        f.writelines(updated_text)


def main():
    files = get_files()
    for input_file in files:
        print(f"Обрабатываем файл: {input_file}")
        json_output_file = str(input_file) + '.json'
        # save_snils_json(file, json_file)
        updated_text = replace_num_cert(input_file, json_output_file)
        create_new_response(input_file, updated_text)


if __name__ == '__main__':
    start_time = time.time()
    main()
    print(f"Общее время: {time.time() - start_time:.2f} секунд.")
    
