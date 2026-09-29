from datetime import datetime
from statistics import get_all_statistics


def general_report(students, projects, progress):
    start = get_all_statistics(students, projects, progress)

    report = []

    report.append("=" * 60)
    report.append("Báo cáo nghiên cứu khoa học")
    report.append("=" * 60)

    report.append(f"Ngày báo cáo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    report.append(f"Tổng số sinh viên: {start['total_students']}")

    report.append("Tổng số sinh viên tham gia nghiên cứu khoa học:")
    report.append("-" * 60)
    report.append(f"Tổng số sinh viên: {start['total_students']}")

    report.append("Tổng số đề tài nghiên cứu khoa học theo lĩnh vực:")
    report.append("-" * 60)
    for field, count in start['projects_by_field'].items():
        report.append(f"{field}: {count}")

    report.append("Tỉ lệ đề tài theo trạng thái:")
    report.append("-" * 60)
    for status, percent in start['projects_by_status'].items():
        report.append(f"{status}: {percent}%")

    report.append("Tiến độ trung bình:")
    report.append("-" * 60)
    report.append(f"Tiến độ trung bình: {start['average_progress']}%")

    report.append("Điểm kết quả trung bình:")
    report.append("-" * 60)
    report.append(f"Điểm kết quả trung bình: {start['average_score']}")

    report.append("Top 5 đề tài có tiến độ cao nhất:")
    report.append("-" * 60)
    ranked_projects = sorted(start['top_5_projects'], key=lambda item: item.get('progress', 0), reverse=True)
    for i, item in enumerate(ranked_projects, start=1):
        project = item.get('project', {})
        progress_value = item.get('progress', 0)
        project_name = project.get('project_name', item.get('project_name', ''))
        report.append(f"{i}. {project_name}: {progress_value}%")

    report.append("Sinh viên tham gia theo khoa:")
    report.append("-" * 60)
    for faculty, count in start['students_by_faculty'].items():
        report.append(f"{faculty}: {count}")

    report.append("=" * 60)
    report.append("Kết thúc báo cáo")
    report.append("=" * 60)

    return "\n".join(report)


def save_report(students, projects, progress, filename="report.txt"):
    report = general_report(students, projects, progress)
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
    except Exception as e:
        print(f"Error saving report to file: {e}")
        return False