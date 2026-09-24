from collections import Counter

def total_students(students):

    return len(students)

def project_by_field(projects):
    return dict(Counter(project['field'] for project in projects))


def projects_by_status(projects):
    total_projects = len(projects)
    if total_projects == 0:
        return {}
    counts = Counter(project['status'] for project in projects)
    return {
        status: round(count / total_projects * 100, 2)
        for status, count in counts.items()
    }

def average_progress(progress):
    if not progress:
        return 0

    value = [float(item.get('progress', 0))
             for item in progress]
    return round(sum(value) / len(value), 2)

def average_score(progress):
    if not progress:
        return 0

    score = [float(item.get('score', 0))
             for item in progress]
    return round(sum(score) / len(score), 2)

def top_5_projects(projects, progress):
    if not projects or not progress:
        return []

    project_scores = {}
    for project in projects:
        project_id = project['id']
        project_progress = next(
            (item for item in progress if item['project_id'] == project_id), None)
        if project_progress:
            project_scores[project_id] = float(project_progress.get('score', 0))

    top_projects = sorted(project_scores.items(), key=lambda x: x[1], reverse=True)[:5]
    return [next((project for project in projects if project['id'] == proj_id), None) for proj_id, _ in top_projects]

def student_by_faculty(students):
    return dict(Counter(student['faculty'] for student in students))

def get_all_statistics(students, projects, progress):
    return {
        'total_students': total_students(students),
        'projects_by_field': project_by_field(projects),
        'projects_by_status': projects_by_status(projects),
        'average_progress': average_progress(progress),
        'average_score': average_score(progress),
        'top_5_projects': top_5_projects(projects, progress),
        'students_by_faculty': student_by_faculty(students)
    }
    