import csv
import os
import tempfile

from statistics import (total_students, average_progress, average_score, top_5_projects)
from NCKH_Students_Tracking.reports import general_report


students_normal = [
    {
        "student_id": "SV001",
        "name": " Đoàn Văn Sáng",
        "class": "CNTT1",
        "faculty": "Công nghệ thông tin",
        "gpa": 3.5
    },
    {
        "student_id": "SV002",
        "name": "Nguyễn Thị Lan",
        "class": "CNTT2",
        "faculty": "Công nghệ thông tin",
        "gpa": 3.8
    },
    {
        "student_id": "SV003",
        "name": "Trần Văn Hùng",
        "class": "CNTT1",
        "faculty": "Công nghệ thông tin",
        "gpa": 3.2
    },
    {
        "student_id": "SV004",
        "name": "Lê Thị Mai",
        "class": "CNTT3",
        "faculty": "Công nghệ thông tin",
        "gpa": 3.9
    },
    {
        "student_id": "SV005",
        "name": "Phạm Văn Nam",
        "class": "CNTT2",
        "faculty": "Công nghệ thông tin",
        "gpa": 3.6
    }
]

projects_normal = [
    {
        "id": 1,
        "title": "Nghiên cứu về trí tuệ nhân tạo",
        "field": "Công nghệ thông tin",
        "status": "Đang thực hiện"
    },
    {
        "id": 2,
        "title": "Phát triển ứng dụng di động",
        "field": "Công nghệ thông tin",
        "status": "Hoàn thành"
    },
    {
        "id": 3,
        "title": "Nghiên cứu về mạng máy tính",
        "field": "Công nghệ thông tin",
        "status": "Đang thực hiện"
    },
    {
        "id": 4,
        "title": "Phát triển hệ thống quản lý cơ sở dữ liệu",
        "field": "Công nghệ thông tin",
        "status": "Chưa bắt đầu"
    },
    {
        "id": 5,
        "title": "Nghiên cứu về an ninh mạng",
        "field": "Công nghệ thông tin",
        "status": "Hoàn thành"
    }
]

progress_normal = [
    {
        "project_id": 1,
        "progress": 80,
        "score": 8.5
    },
    {
        "project_id": 2,
        "progress": 100,
        "score": 9.0
    },
    {
        "project_id": 3,
        "progress": 60,
        "score": 7.5
    },
    {
        "project_id": 4,
        "progress": 0,
        "score": 0
    },
    {
        "project_id": 5,
        "progress": 100,
        "score": 9.5
    }
]

def test_case_1_normal_data():
    print("Test Case 1: Normal Data")
    assert total_students(students_normal) == 3
    assert average_progress(progress_normal) == 88.0
    assert average_score(progress_normal) == 8.0
    top = top_5_projects(projects_normal, progress_normal)
    assert len(top) == 5
    assert top[0]['id'] == 5

    report = general_report(students_normal, projects_normal, progress_normal)

    assert "Báo cáo nghiên cứu khoa học" in report
    assert "Phát triển hệ thống quản lý cơ sở dữ liệu" in report
    assert "Nghiên cứu về an ninh mạng" in report
    print("Test Case 1 Passed\n")
