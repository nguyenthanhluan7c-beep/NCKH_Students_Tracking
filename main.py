from pathlib import Path
import csv
import json

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = BASE_DIR / 'output'

CSV_FILES = {
    'students': DATA_DIR / 'students.csv',
    'projects': DATA_DIR / 'projects.csv',
    'progress': DATA_DIR / 'progress.csv',
}


def read_csv(file_path: Path) -> list[dict]:
    if not file_path.exists():
        raise FileNotFoundError(f'Không tìm thấy file: {file_path}')

    with file_path.open('r', encoding='utf-8-sig', newline='') as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            raise ValueError(f'File {file_path.name} không có header.')

        rows = []
        for row_number, row in enumerate(reader, start=2):
            item = dict(row)
            item['_row'] = row_number
            rows.append(item)
        return rows


def load_all_data() -> dict[str, list[dict]]:
    data = {}
    for name, path in CSV_FILES.items():
        data[name] = read_csv(path)
        print(f'[OK] {name}: {len(data[name])} bản ghi')
    return data


def build_data_structures(data: dict[str, list[dict]]) -> dict:
    students = data.get('students', [])
    projects = data.get('projects', [])
    progress = data.get('progress', [])

    student_ids = {r.get('student_id', '').strip() for r in students if r.get('student_id')}
    project_ids = {r.get('project_id', '').strip() for r in projects if r.get('project_id')}

    students_by_id = {r.get('student_id', '').strip(): r for r in students if r.get('student_id')}
    projects_by_id = {r.get('project_id', '').strip(): r for r in projects if r.get('project_id')}

    project_summaries = [
        (r.get('project_id', ''), r.get('project_name', ''), r.get('status', ''))
        for r in projects
    ]

    return {
        'students': students,
        'projects': projects,
        'progress': progress,
        'student_ids': student_ids,
        'project_ids': project_ids,
        'students_by_id': students_by_id,
        'projects_by_id': projects_by_id,
        'project_summaries': project_summaries,
    }


def run_cleaning(data):
    from cleanser import clean_all_data

    return clean_all_data(data)


def run_validation(data, cleaning_issues):
    from validator import validate_data

    return validate_data(data, cleaning_issues)

def run_statistics(data):
    from statistics import calculate_all_statistics

    return calculate_all_statistics(data)


def run_report(data, validation, statistics):
    from reports import generate_report

    OUTPUT_DIR.mkdir(exist_ok=True)
    generate_report(data, validation, statistics, OUTPUT_DIR / 'report.txt')
    print('[OK] Đã tạo output/report.txt')


def save_preview(structures):
    OUTPUT_DIR.mkdir(exist_ok=True)
    preview = {
        'student_count': len(structures['students']),
        'project_count': len(structures['projects']),
        'progress_count': len(structures['progress']),
        'student_id_set_size': len(structures['student_ids']),
        'project_id_set_size': len(structures['project_ids']),
        'first_project_summary': structures['project_summaries'][0] if structures['project_summaries'] else None,
    }
    with (OUTPUT_DIR / 'data_preview.json').open('w', encoding='utf-8') as file:
        json.dump(preview, file, ensure_ascii=False, indent=2)


def main():
    print('=' * 60)
    print('THEO DÕI NCKH SINH VIÊN - FIT4018 - NHÓM 3')
    print('=' * 60)

    data = load_all_data()
    data, cleaning_issues = run_cleaning(data)
    structures = build_data_structures(data)
    validation = run_validation(data, cleaning_issues)
    statistics = run_statistics(data)
    run_report(data, validation, statistics)
    save_preview(structures)

    print('\n--- TỔNG QUAN ---')
    print(f"Sinh viên: {len(structures['students'])}")
    print(f"Đề tài:    {len(structures['projects'])}")
    print(f"Tiến độ:   {len(structures['progress'])}")
    print(f"ID SV duy nhất: {len(structures['student_ids'])}")
    print(f"ID đề tài duy nhất: {len(structures['project_ids'])}")
    print(f"Lỗi dữ liệu: {len(validation['errors'])}")
    print(f"Cảnh báo:    {len(validation['warnings'])}")
    print('\n[OK] Pipeline hoàn tất.')


if __name__ == '__main__':
    from console import configure_console_encoding

    configure_console_encoding()
    main()
