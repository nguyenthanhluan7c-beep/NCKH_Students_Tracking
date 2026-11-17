from datetime import datetime
from pathlib import Path
from statistics import get_all_statistics


def general_report(students, projects, progress, statistics=None):
    start = statistics or get_all_statistics(students, projects, progress)

    report = []

    report.append("=" * 60)
    report.append("Báo cáo nghiên cứu khoa học")
    report.append("=" * 60)

    report.append(f"Ngày báo cáo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    report.append(f"Tổng số sinh viên: {start['total_students']}")

    report.append(
        f"Tổng số sinh viên tham gia nghiên cứu khoa học: "
        f"{start['participating_students']}"
    )
    report.append("-" * 60)

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
    ranked_projects = sorted(
        start['top_5_projects'],
        key=lambda item: item.get('progress', 0),
        reverse=True,
    )
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
    Path(filename).write_text(report, encoding="utf-8")
    return True


def generate_report(data, validation, statistics, filename="report.txt"):
    report = general_report(
        data.get("students", []),
        data.get("projects", []),
        data.get("progress", []),
        statistics,
    )
    report += "\n\nKết quả kiểm tra dữ liệu\n" + "=" * 60
    report += f"\nSố lỗi: {len(validation.get('errors', []))}"
    report += f"\nSố cảnh báo: {len(validation.get('warnings', []))}"
    for label, items in (
        ("Lỗi", validation.get("errors", [])),
        ("Cảnh báo", validation.get("warnings", [])),
    ):
        if items:
            report += f"\n\n{label}:"
            report += "".join(f"\n- {item}" for item in items)
    Path(filename).write_text(report, encoding="utf-8")
    return True