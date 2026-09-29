import csv
import os
import tempfile

from statistics import (total_students, average_progress, average_score, top_5_projects)
from reports import general_report


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
    assert average_progress(progress_normal) == 90.0
    assert average_score(progress_normal) == 8.5
    top = top_5_projects(projects_normal, progress_normal)
    assert len(top) == 2
    assert top[1]['project_id'] == "DT002"

    report = general_report(students_normal, projects_normal, progress_normal)

    assert "AI trong giao duc" in report
    assert "Quan ly NCKH" in report
    print("Test Case 1 Passed\n")

def test_case_2_empty_data():
    print("Test Case 2: Empty Data")

    invalid_progress = [
        {
            "progress_id": "P001",
            "project_id": "DT001",
            "student_id": "SV001",
            "progress": 120,
            "score": 8
        },
        {
            "progress_id": "P002",
            "project_id": "DT999",
            "student_id": "SV999",
            "progress": 50,
            "score": 11
        }
    ]

    try:
        for item in invalid_progress:
            progress = item.get("progress", 0)
            score = item.get("score", 0)

            if not 0 <= progress <= 100:
                print(
                    f"Cảnh báo: progress không hợp lệ: "
                    f"{progress}"
                )

            if not 0 <= score <= 10:
                print(
                    f"Cảnh báo: score không hợp lệ: "
                    f"{score}"
                )
        result = average_progress(invalid_progress)
        assert result == 85.0

        print("Test Case 2 Passed\n")
    except Exception as e:
        print(f"Test Case 2 Failed: {e}\n")
        assert False, f"Test Case 2 Failed: {e}"


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

if __name__ == "__main__":
    test_case_1_normal_data()
    test_case_2_empty_data()
    test_case_3_bad_file()
    print("All test cases executed.")