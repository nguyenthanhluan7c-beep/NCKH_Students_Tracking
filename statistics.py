from collections import Counter
import math


def _safe_float(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def total_students(students):
    return len(students)


def participating_students(students, progress):
    student_ids = {student.get('student_id') for student in students}
    participant_ids = {item.get('student_id') for item in progress}
    return len((student_ids & participant_ids) - {None, ''})


def project_by_field(projects):
    return dict(Counter(project.get('field') or 'Unknown' for project in projects))


def projects_by_status(projects):
    total_projects = len(projects)
    if total_projects == 0:
        return {}
    counts = Counter(project.get('status') or 'Unknown' for project in projects)
    return {
        status: round(count / total_projects * 100, 2)
        for status, count in counts.items()
    }


def average_progress(progress):
    values = []
    for item in progress:
        value = _safe_float(item.get('progress', 0))
        if value is not None and 0 <= value <= 100:
            values.append(value)
    if not values:
        return 0
    return round(sum(values) / len(values), 2)


def average_score(progress):
    values = []
    for item in progress:
        value = _safe_float(item.get('score', 0))
        if value is not None and 0 <= value <= 10:
            values.append(value)
    if not values:
        return 0
    return round(sum(values) / len(values), 2)


def top_5_projects(projects, progress):
    if not projects or not progress:
        return []

    grouped_scores = {}
    for item in progress:
        project_id = item.get('project_id')
        if not project_id:
            continue
        value = _safe_float(item.get('progress', 0))
        if value is None or not 0 <= value <= 100:
            continue
        if project_id not in grouped_scores:
            grouped_scores[project_id] = []
        grouped_scores[project_id].append(value)

    result = []
    seen_project_ids = set()
    for project in projects:
        project_id = project.get('project_id')
        if (
            not project_id
            or project_id in seen_project_ids
            or project_id not in grouped_scores
        ):
            continue
        seen_project_ids.add(project_id)
        project_progress = sum(grouped_scores[project_id]) / len(grouped_scores[project_id])
        result.append({
            'project_id': project_id,
            'project_name': project.get('project_name', ''),
            'project': project,
            'progress': round(project_progress, 2),
        })

    result.sort(key=lambda item: item['progress'], reverse=True)
    return result[:5]


def student_by_faculty(students):
    return dict(Counter(student.get('faculty') or 'Unknown' for student in students))


def get_all_statistics(students, projects, progress):
    return {
        'total_students': total_students(students),
        'participating_students': participating_students(students, progress),
        'projects_by_field': project_by_field(projects),
        'projects_by_status': projects_by_status(projects),
        'average_progress': average_progress(progress),
        'average_score': average_score(progress),
        'top_5_projects': top_5_projects(projects, progress),
        'students_by_faculty': student_by_faculty(students)
    }


def calculate_all_statistics(data):
    return get_all_statistics(
        data.get('students', []),
        data.get('projects', []),
        data.get('progress', []),
    )
    