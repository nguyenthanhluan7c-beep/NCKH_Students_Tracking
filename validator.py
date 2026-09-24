def get_ids(records, key):
    """Trích tập ID (Set) từ list dict, bỏ qua giá trị rỗng."""
    return {r[key] for r in records if r.get(key)}

def get_ids_including_invalid(valid, invalid, key):
    """ID từ cả dòng hợp lệ lẫn dòng lỗi.

    Cần khi đối chiếu: một sinh viên bị loại vì gpa='abc' vẫn LÀ sinh viên tồn tại,
    không được báo 'mồ côi' oan ở file khác.
    """
    ids = get_ids(valid, key)
    ids |= {b["record"][key] for b in invalid if b["record"].get(key)}
    return ids

def find_duplicates(records, key):
    """Trả về Set các ID xuất hiện > 1 lần."""
    seen, dups = set(), set()
    for r in records:
        value = r.get(key)
        if not value:
            continue
        if value in seen:
            dups.add(value)
        else:
            seen.add(value)
    return dups


def remove_duplicates(records, key):
    
    seen, unique, removed = set(), [], []
    for r in records:
        value = r.get(key)
        if not value:
            unique.append(r)
        elif value in seen:
            removed.append(r)
        else:
            seen.add(value)
            unique.append(r)
    return unique, removed

def find_missing_fields(records, required, key):
    """Trả về list (ID hoặc 'dòng #i', Set các trường thiếu)."""
    result = []
    for i, r in enumerate(records):
        empty = {f for f in required if r.get(f) in (None, "")}
        if empty:
            result.append((r.get(key) or f"dòng #{i}", empty))
    return result

def find_orphans(child_ids, parent_ids):
    """ID ở file con KHÔNG tồn tại ở file cha (phép trừ tập hợp)."""
    return set(child_ids) - set(parent_ids)


def compare_files(ids_a, ids_b):
    """So sánh 2 tập ID bằng phép toán tập hợp."""
    a, b = set(ids_a), set(ids_b)
    return {"chung": a & b, "chi_co_o_a": a - b, "chi_co_o_b": b - a}

def find_out_of_range(records, field, low, high, key):
    """List (ID, giá trị) có field nằm ngoài [low, high]."""
    bad = []
    for r in records:
        v = r.get(field)
        if isinstance(v, (int, float)) and not (low <= v <= high):
            bad.append((r.get(key), v))
    return bad


def find_invalid_values(records, field, allowed, key):
    """List (ID, giá trị) có field không thuộc Set giá trị cho phép."""
    return [(r.get(key), r[field]) for r in records
            if r.get(field) and r[field] not in allowed]


def is_valid_email(email):
    """Kiểm tra email đơn giản, không cần regex."""
    if not email or email.count("@") != 1:
        return False
    name, domain = email.split("@")
    return bool(name) and "." in domain and not domain.startswith(".") and not domain.endswith(".")

PROJECT_STATUS = {"Hoàn thành", "Đang thực hiện", "Tạm dừng"}
RESULT_VALUES = {"Xuất sắc", "Tốt", "Khá", "Đạt", "Chưa đạt"}


def validate_all(students, projects, progress, students_bad=(), projects_bad=()):

    student_ids = get_ids_including_invalid(students, students_bad, "student_id")
    project_ids = get_ids_including_invalid(projects, projects_bad, "project_id")

    return {
        "trung_id": {
            "students": find_duplicates(students, "student_id"),
            "projects": find_duplicates(projects, "project_id"),
            "progress": find_duplicates(progress, "progress_id"),
        },
        "id_khong_ton_tai": {
            "projects.leader_id -> students": find_orphans(get_ids(projects, "leader_id"), student_ids),
            "progress.student_id -> students": find_orphans(get_ids(progress, "student_id"), student_ids),
            "progress.project_id -> projects": find_orphans(get_ids(progress, "project_id"), project_ids),
        },
        "ngoai_khoang": {
            "students.gpa (0-4)": find_out_of_range(students, "gpa", 0, 4, "student_id"),
            "progress.progress (0-100)": find_out_of_range(progress, "progress", 0, 100, "progress_id"),
            "progress.score (0-10)": find_out_of_range(progress, "score", 0, 10, "progress_id"),
        },
        "gia_tri_khong_hop_le": {
            "projects.status": find_invalid_values(projects, "status", PROJECT_STATUS, "project_id"),
            "progress.result": find_invalid_values(progress, "result", RESULT_VALUES, "progress_id"),
        },
        "thieu_truong": {
            "projects": find_missing_fields(projects, {"field"}, "project_id"),
            "progress": find_missing_fields(progress, {"result"}, "progress_id"),
        },
        "sinh_vien_khong_tham_gia": student_ids - get_ids(progress, "student_id"),
    }

def print_report(report):
    """In báo cáo validate_all() dễ đọc."""
    for section, content in report.items():
        print(f"\n### {section}")
        if isinstance(content, dict):
            for name, items in content.items():
                print(f"  - {name}: {sorted(items, key=str) if isinstance(items, set) else items}")
        else:
            print(f"  {len(content)} mục: {sorted(content)}")


if __name__ == "__main__":
    import os
    from cleaners import load_all

    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    data = load_all(data_dir)
    (s, s_bad), (p, p_bad), (g, _) = data["students"], data["projects"], data["progress"]
    print_report(validate_all(s, p, g, students_bad=s_bad, projects_bad=p_bad))