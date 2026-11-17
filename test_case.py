import csv
import os
import tempfile

from cleanser import clean_all, to_float, to_int
from statistics import (
    total_students,
    participating_students,
    average_progress,
    average_score,
    top_5_projects,
)
from reports import general_report
from validator import find_duplicates, find_out_of_range


students_normal = [
    {
        "student_id": "SV001",
        "name": "Nguyen Van A",
        "class": "CNTT1",
        "faculty": "CNTT",
        "gpa": 3.2
    },
    {
        "student_id": "SV002",
        "name": "Tran Thi B",
        "class": "CNTT2",
        "faculty": "CNTT",
        "gpa": 3.5
    },
    {
        "student_id": "SV003",
        "name": "Le Van C",
        "class": "KTPM1",
        "faculty": "KTPM",
        "gpa": 3.0
    }
]


projects_normal = [
    {
        "project_id": "DT001",
        "project_name": "AI trong giao duc",
        "field": "AI",
        "leader_id": "SV001",
        "status": "Dang thuc hien"
    },
    {
        "project_id": "DT002",
        "project_name": "Quan ly NCKH",
        "field": "Web",
        "leader_id": "SV002",
        "status": "Hoan thanh"
    }
]


progress_normal = [
    {
        "progress_id": "P001",
        "project_id": "DT001",
        "student_id": "SV001",
        "progress": 80,
        "score": 8
    },
    {
        "progress_id": "P002",
        "project_id": "DT002",
        "student_id": "SV002",
        "progress": 100,
        "score": 9
    }
]

def test_case_1_normal_data():
    print("Test Case 1: Normal Data")
    assert total_students(students_normal) == 3
    assert participating_students(students_normal, progress_normal) == 2
    assert average_progress(progress_normal) == 90.0
    assert average_score(progress_normal) == 8.5
    top = top_5_projects(projects_normal, progress_normal)
    assert len(top) == 2
    assert top[0]['project_id'] == "DT002"
    assert top[1]['project_id'] == "DT001"
    duplicate_project = dict(projects_normal[0], project_name="Duplicate project row")
    top_with_duplicate = top_5_projects(
        projects_normal + [duplicate_project], progress_normal
    )
    assert [item['project_id'] for item in top_with_duplicate] == ["DT002", "DT001"]

    report = general_report(students_normal, projects_normal, progress_normal)

    assert "AI trong giao duc" in report
    assert "Quan ly NCKH" in report
    assert "Tổng số sinh viên tham gia nghiên cứu khoa học: 2" in report
    print("Test Case 1 Passed\n")

def test_case_2_empty_data():
    print("Test Case 2: Empty and malformed data")
    assert total_students([]) == 0
    assert average_progress([]) == 0
    assert average_score([]) == 0
    assert top_5_projects([], []) == []
    out_of_range_progress = [
        {"progress": 120, "score": 11},
        {"progress": -1, "score": -1},
        {"progress": 50, "score": 8},
    ]
    assert average_progress(out_of_range_progress) == 50
    assert average_score(out_of_range_progress) == 8

    duplicates = find_duplicates(
        [{"student_id": "SV001"}, {"student_id": "SV001"}], "student_id"
    )
    assert duplicates == {"SV001"}
    out_of_range = find_out_of_range(
        [{"progress_id": "P001", "progress": 120}], "progress", 0, 100, "progress_id"
    )
    assert out_of_range == [("P001", 120)]
    assert to_float("8,5") == 8.5
    assert to_int("8") == 8
    for invalid_number in ("abc", "nan", "inf"):
        try:
            to_float(invalid_number)
        except ValueError:
            continue
        raise AssertionError(f"Expected ValueError for {invalid_number!r}")
    try:
        to_int("2.5")
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for non-integer input")

    cleaned, invalid = clean_all(
        [{"student_id": "SV001", "name": "", "gpa": "3.2"}],
        {
            "student_id": lambda value: value,
            "name": lambda value: value,
            "gpa": to_float,
        },
        {"student_id", "name", "gpa"},
    )
    assert cleaned == []
    assert invalid[0]["line"] == 2
    assert "name" in invalid[0]["errors"][0]
    print("Test Case 2 Passed\n")


def test_case_3_bad_file():
    print("Test Case 3: Bad File Handling")

    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".csv", encoding="utf-8", newline=""
    ) as bad_file:
        bad_filename = bad_file.name
        writer = csv.writer(bad_file)
        writer.writerow(["student_id", "name"])
        writer.writerow(["SV001", "Nguyen Van A"])

    try:
        with open(bad_filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            required_columns = {"student_id", "name", "class", "faculty", "gpa"}
            actual_columns = set(reader.fieldnames or [])
            missing_columns = required_columns - actual_columns
            if missing_columns:
                raise ValueError(
                    f"Thiếu cột dữ liệu: {', '.join(missing_columns)}"
                )
    except ValueError as ve:
        print(f"Caught expected ValueError: {ve}")
        print("Test Case 3 Passed\n")
    finally:
        if os.path.exists(bad_filename):
            os.remove(bad_filename)


def test_case_4_csv_upload():
    from pathlib import Path
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(Path(__file__).with_name("app.py")).run()
    app.button(key="analyze_csv_button").click().run()
    assert not app.exception
    assert app.error

    uploads = {
        "students_csv": (
            "students.csv",
            b"student_id,name,class,faculty,gpa\nSV001,Student One,C1,CNTT,3.5\n",
        ),
        "projects_csv": (
            "projects.csv",
            "project_id,project_name,field,leader_id,status\n"
            "DT001,Project One,AI,SV001,Đang thực hiện\n".encode("utf-8"),
        ),
        "progress_csv": (
            "progress.csv",
            "progress_id,project_id,student_id,progress,score,result\n"
            "PG001,DT001,SV001,50,8,Tốt\n".encode("utf-8"),
        ),
    }
    for key, (filename, content) in uploads.items():
        app.file_uploader(key=key).set_value((filename, content, "text/csv"))
    app.button(key="analyze_csv_button").click().run()

    assert not app.exception
    assert len(app.metric) == 8
    assert len(app.session_state["analysis_result"][0]) == 1
    assert app.session_state["analysis_files"] == {
        key.removesuffix("_csv"): filename
        for key, (filename, _) in uploads.items()
    }

    app.file_uploader(key="students_csv").set_value(
        ("wrong.csv", b"wrong,columns\nvalue,value\n", "text/csv")
    )
    app.button(key="analyze_csv_button").click().run()
    assert not app.exception
    assert any("thiếu cột bắt buộc" in error.value.lower() for error in app.error)
    assert "analysis_result" not in app.session_state
    print("Test Case 4 Passed\n")


if __name__ == "__main__":
    from console import configure_console_encoding

    configure_console_encoding()
    test_case_1_normal_data()
    test_case_2_empty_data()
    test_case_3_bad_file()
    test_case_4_csv_upload()
    print("All test cases executed.")