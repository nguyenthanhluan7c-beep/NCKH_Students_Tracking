# Phần của Nguyễn Thành Luân

## Phụ trách
- Đọc 3 CSV
- Tổ chức List / Tuple / Dictionary / Set
- main.py
- app.py
- Tích hợp các module của nhóm
- Giao diện Streamlit

## Chạy
```bash
pip install -r requirements.txt
python main.py
streamlit run app.py
```

## Tải dữ liệu CSV
Trong giao diện, tải lần lượt ba file sinh viên, đề tài và tiến độ rồi bấm **Phân tích dữ liệu**. Ứng dụng kiểm tra các cột bắt buộc và xử lý file trong phiên hiện tại, không chép file vào thư mục dự án.

## Giao diện
- Tải lên ba file CSV và phân tích dữ liệu trực tiếp
- Tổng số sinh viên / đề tài / bản ghi tiến độ
- Tiến độ trung bình
- Lọc đề tài theo trạng thái và lĩnh vực
- Bảng dữ liệu
- Biểu đồ tiến độ
- Thống kê nghiệp vụ từ statistics.py
- Cảnh báo lỗi từ validator.py
