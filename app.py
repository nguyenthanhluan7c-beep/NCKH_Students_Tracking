from io import BytesIO

import pandas as pd
import streamlit as st

from cleanser import clean_all_data
from statistics import calculate_all_statistics
from validator import validate_data

CSV_COLUMNS = {
    'students': {'student_id', 'name', 'class', 'faculty', 'gpa'},
    'projects': {'project_id', 'project_name', 'field', 'leader_id', 'status'},
    'progress': {'progress_id', 'project_id', 'student_id', 'progress', 'score', 'result'},
}

st.set_page_config(page_title='Theo dõi NCKH sinh viên', page_icon='📚', layout='wide')


def parse_uploaded_csv(content: bytes, file_name: str, data_name: str) -> list[dict]:
    expected_columns = CSV_COLUMNS.get(data_name)
    if expected_columns is None:
        raise ValueError(f'Loại dữ liệu không được hỗ trợ: {data_name}')
    try:
        frame = pd.read_csv(BytesIO(content), encoding='utf-8-sig')
    except (UnicodeDecodeError, pd.errors.ParserError, pd.errors.EmptyDataError, ValueError) as error:
        raise ValueError(f'Không thể đọc {file_name}: {error}') from error

    frame.columns = [str(column).strip() for column in frame.columns]
    missing_columns = expected_columns - set(frame.columns)
    if missing_columns:
        columns = ', '.join(sorted(missing_columns))
        raise ValueError(f'{file_name} thiếu cột bắt buộc: {columns}.')
    return dataframe_to_records(frame)


def dataframe_to_records(df):
    if df.empty:
        return []
    return df.astype(object).where(pd.notna(df), None).to_dict(orient='records')


def prepare_pipeline(raw_data: dict[str, list[dict]]):
    data, cleaning_issues = clean_all_data(raw_data)
    validation = validate_data(data, cleaning_issues)
    statistics = calculate_all_statistics(data)
    frames = {name: pd.DataFrame(rows) for name, rows in data.items()}
    return (
        frames['students'],
        frames['projects'],
        frames['progress'],
        validation,
        statistics,
    )


def upload_and_analyze():
    with st.form('csv_analysis_form'):
        st.subheader('📤 Tải lên dữ liệu CSV')
        st.caption('Chọn đủ ba file CSV rồi bấm “Phân tích dữ liệu”. File chỉ được xử lý trong phiên này.')
        columns = st.columns(3)
        uploaded_files = {}
        for column, (name, label) in zip(
            columns,
            (
                ('students', 'Sinh viên'),
                ('projects', 'Đề tài'),
                ('progress', 'Tiến độ'),
            ),
        ):
            with column:
                uploaded_files[name] = st.file_uploader(
                    f'CSV {label}',
                    type='csv',
                    key=f'{name}_csv',
                )
        submitted = st.form_submit_button(
            'Phân tích dữ liệu',
            type='primary',
            key='analyze_csv_button',
        )

    if not submitted:
        return

    st.session_state.pop('analysis_result', None)
    st.session_state.pop('analysis_files', None)
    missing_files = [
        name for name, uploaded_file in uploaded_files.items()
        if uploaded_file is None
    ]
    if missing_files:
        labels = {
            'students': 'sinh viên',
            'projects': 'đề tài',
            'progress': 'tiến độ',
        }
        missing_labels = ', '.join(labels[name] for name in missing_files)
        st.error(f'Vui lòng tải lên các file CSV còn thiếu: {missing_labels}.')
        return

    try:
        raw_data = {
            name: parse_uploaded_csv(
                uploaded_files[name].getvalue(),
                uploaded_files[name].name,
                name,
            )
            for name in CSV_COLUMNS
        }
    except ValueError as error:
        st.error(str(error))
        return

    st.session_state['analysis_result'] = prepare_pipeline(raw_data)
    st.session_state['analysis_files'] = {
        name: uploaded_files[name].name for name in CSV_COLUMNS
    }


def show_overview(students, projects, progress):
    values = pd.to_numeric(progress.get('progress', pd.Series(dtype=float)), errors='coerce').dropna()
    values = values[values.between(0, 100)]
    avg = values.mean() if not values.empty else 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('👨‍🎓 Sinh viên', len(students))
    c2.metric('🔬 Đề tài', len(projects))
    c3.metric('📈 Bản ghi tiến độ', len(progress))
    c4.metric('🎯 Tiến độ TB', f'{avg:.1f}%')


def show_projects(projects):
    st.subheader('🔬 Danh sách đề tài')
    if projects.empty:
        st.warning('Chưa có dữ liệu đề tài.')
        return

    filtered = projects.copy()
    col1, col2 = st.columns(2)

    if 'status' in filtered.columns:
        statuses = sorted(filtered['status'].dropna().astype(str).unique().tolist())
        with col1:
            selected = st.selectbox('Lọc theo trạng thái', ['Tất cả'] + statuses)
        if selected != 'Tất cả':
            filtered = filtered[filtered['status'].astype(str) == selected]

    if 'field' in filtered.columns:
        fields = sorted(filtered['field'].dropna().astype(str).unique().tolist())
        with col2:
            selected = st.selectbox('Lọc theo lĩnh vực', ['Tất cả'] + fields)
        if selected != 'Tất cả':
            filtered = filtered[filtered['field'].astype(str) == selected]

    st.dataframe(filtered, width='stretch', hide_index=True)


def show_progress(progress):
    st.subheader('📊 Phân tích tiến độ')
    if progress.empty or 'progress' not in progress.columns:
        st.warning('Chưa có dữ liệu progress hợp lệ.')
        return

    chart = progress.copy()
    chart['progress'] = pd.to_numeric(chart['progress'], errors='coerce')
    chart = chart.dropna(subset=['progress'])
    chart = chart[chart['progress'].between(0, 100)]
    if chart.empty:
        st.warning('Không có giá trị progress hợp lệ.')
        return

    if 'project_id' in chart.columns:
        grouped = chart.groupby('project_id')['progress'].mean().sort_values(ascending=False).head(10)
        st.bar_chart(grouped)
    else:
        st.line_chart(chart['progress'])


def show_validation(validation):
    st.subheader('⚠️ Kiểm tra dữ liệu')
    errors = validation.get('errors', [])
    warnings = validation.get('warnings', [])
    c1, c2 = st.columns(2)
    with c1:
        if errors:
            st.error(f'Phát hiện {len(errors)} lỗi.')
            for item in errors[:10]:
                st.write(f'- {item}')
        else:
            st.success('Không phát hiện lỗi nghiêm trọng.')
    with c2:
        if warnings:
            st.warning(f'Có {len(warnings)} cảnh báo.')
            for item in warnings[:10]:
                st.write(f'- {item}')
        else:
            st.info('Không có cảnh báo.')


def show_statistics(statistics):
    st.subheader('📈 Thống kê nghiệp vụ')
    if not statistics:
        st.info('Chưa có kết quả từ statistics.py.')
        return
    items = list(statistics.items())
    for start in range(0, len(items), 4):
        cols = st.columns(4)
        for col, (key, value) in zip(cols, items[start:start + 4]):
            with col:
                if isinstance(value, (int, float)):
                    st.metric(str(key), f'{value:.2f}' if isinstance(value, float) else value)
                else:
                    st.write(f'**{key}**')
                    st.json(value)


def main():
    st.title('📚 Theo dõi NCKH sinh viên')
    st.caption('FIT4018 – Lập trình Python | Nhóm 3 – Chủ đề 12')

    st.sidebar.header('⚙️ Điều khiển')
    if st.sidebar.button('🧹 Xóa kết quả phân tích'):
        st.session_state.pop('analysis_result', None)
        st.session_state.pop('analysis_files', None)
        st.rerun()
    st.sidebar.info('Tải lên ba file CSV để bắt đầu phân tích.')

    upload_and_analyze()
    analysis = st.session_state.get('analysis_result')
    if analysis is None:
        st.info('Tải lên đủ ba file CSV và bấm “Phân tích dữ liệu” để xem kết quả.')
        return

    students, projects, progress, validation, statistics = analysis
    if students.empty and projects.empty and progress.empty:
        st.error('Các file CSV không có bản ghi dữ liệu hợp lệ.')
        return

    source_files = st.session_state.get('analysis_files', {})
    st.caption('Đang phân tích: ' + ', '.join(source_files.values()))
    tab1, tab2, tab3, tab4 = st.tabs(['🏠 Tổng quan', '🔬 Đề tài', '📊 Tiến độ', '⚠️ Kiểm tra dữ liệu'])
    with tab1:
        show_overview(students, projects, progress)
        show_statistics(statistics)
    with tab2:
        show_projects(projects)
    with tab3:
        show_progress(progress)
    with tab4:
        show_validation(validation)


if __name__ == '__main__':
    main()
