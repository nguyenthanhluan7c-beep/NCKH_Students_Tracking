import csv
import os

MISSING = {"", "n/a", "na", "null", "none", "-", "?"}


# ---------- 1. Đọc file ----------
def read_csv(path):
    """Đọc CSV -> list các dict. Lỗi file thì in thông báo và trả về []."""
    try:
        with open(path, encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        print(f"[LỖI] Không tìm thấy file: {path}")
    except (OSError, UnicodeDecodeError) as e:
        print(f"[LỖI] Không đọc được {path}: {e}")
    return []


# ---------- 2. Hàm làm sạch từng kiểu dữ liệu ----------
def strip_spaces(text):
    """'  Nguyễn   Văn  An ' -> 'Nguyễn Văn An' (bỏ đầu/cuối, gộp khoảng trắng giữa)."""
    return " ".join(str(text).split())


def is_missing(text):
    return strip_spaces(text).lower() in MISSING


def clean_id(text):
    """' sv001 ' -> 'SV001'."""
    return strip_spaces(text).upper()


def clean_name(text):
    """'  nguyễn   văn an' -> 'Nguyễn Văn An'."""
    return strip_spaces(text).title()


def clean_email(text):
    return strip_spaces(text).lower()

FACULTY_CANON = {
    "cntt": "CNTT",
    "kinh tế": "Kinh tế",
    "điện - điện tử": "Điện - Điện tử",
    "cơ khí": "Cơ khí",
}

def clean_faculty(text):
    text = strip_spaces(text)
    return FACULTY_CANON.get(text.lower(), text)


def to_float(text):
    """'8,5' / ' 8.5 ' -> 8.5 ; sai -> raise ValueError."""
    return float(strip_spaces(text).replace(",", "."))


def to_int(text):
    return int(float(strip_spaces(text).replace(",", ".")))


def split_tags(text, sep=";"):
    """'Python; SQL;  AI' -> ('Python', 'SQL', 'AI') - trả về Tuple."""
    return tuple(strip_spaces(p) for p in str(text).split(sep) if strip_spaces(p))

STUDENT_RULES = {
    "student_id": clean_id,
    "name": clean_name,
    "class": clean_id,
    "faculty": clean_faculty,
    "gpa": to_float,
}
STUDENT_REQUIRED = {"student_id", "name", "gpa"}        

PROJECT_RULES = {
    "project_id": clean_id,
    "project_name": clean_name,
    "field": strip_spaces,
    "leader_id": clean_id,
    "status": strip_spaces,
}
PROJECT_REQUIRED = {"project_id", "project_name", "leader_id"}

PROGRESS_RULES = {
    "progress_id": clean_id,
    "project_id": clean_id,
    "student_id": clean_id,
    "progress": to_float,
    "score": to_float,
    "result": strip_spaces,
}
PROGRESS_REQUIRED = {"progress_id", "project_id", "student_id", "progress", "score"}

def clean_record(raw, rules, required):
    """raw dict -> (record_sạch, list_lỗi)."""
    record, errors = {}, []
    for col, func in rules.items():
        value = raw.get(col)
        if value is None or is_missing(value):
            if col in required:
                errors.append(f"Thiếu giá trị cột '{col}'")
            record[col] = None
            continue
        try:
            record[col] = func(value)
        except (ValueError, TypeError):
            errors.append(f"Cột '{col}' sai định dạng: {value!r}")
            record[col] = None
    return record, errors

def clean_all(rows, rules, required):
    
    valid, invalid = [], []
    for line_no, raw in enumerate(rows, start=2):       
        try:
            record, errors = clean_record(raw, rules, required)
        except Exception as e:                            
            record, errors = {}, [f"Lỗi không xác định: {e}"]
        if errors:
            invalid.append({"line": line_no, "raw": raw, "record": record, "errors": errors})
        else:
            valid.append(record)
    return valid, invalid

def print_table(title, rows, columns):
    """In dữ liệu dạng bảng có căn cột."""
    print(f"\n{title}")
    if not rows:
        print("  (không có dữ liệu)")
        return

    widths = {}
    for col in columns:
        values = [str(row.get(col, "")) for row in rows]
        widths[col] = max(len(str(col)), *(len(v) for v in values))

    print(" | ".join(str(col).ljust(widths[col]) for col in columns))
    print("-+-".join("-" * widths[col] for col in columns))
    for row in rows:
        print(" | ".join(str(row.get(col, "")).ljust(widths[col]) for col in columns))


def show_invalid(title, invalid):
    """In bảng các dòng lỗi: số dòng + lỗi."""
    items = [{"Dòng": b["line"], "Lỗi": "; ".join(b["errors"])} for b in invalid]
    print_table(title, items, ["Dòng", "Lỗi"])

def load_all(data_dir):
    """Trả về Dictionary: {'students': (valid, invalid), 'projects': ..., 'progress': ...}."""
    specs = {
        "students": ("students.csv", STUDENT_RULES, STUDENT_REQUIRED),
        "projects": ("projects.csv", PROJECT_RULES, PROJECT_REQUIRED),
        "progress": ("progress.csv", PROGRESS_RULES, PROGRESS_REQUIRED),
    }
    result = {}
    for name, (filename, rules, required) in specs.items():
        rows = read_csv(os.path.join(data_dir, filename))
        result[name] = clean_all(rows, rules, required)
    return result


if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    for name, (valid, invalid) in load_all(data_dir).items():
        print(f"\n=== {name}: {len(valid)} hợp lệ, {len(invalid)} lỗi ===")
        show_invalid(f"DÒNG LỖI - {name}", invalid)