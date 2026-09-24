from pathlib import Path
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'

st.set_page_config(page_title='Theo dõi NCKH sinh viên', page_icon='📚', layout='wide')


@st.cache_data
def load_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path, encoding='utf-8-sig')


def safe_load(name: str) -> pd.DataFrame:
    path = DATA_DIR / f'{name}.csv'
    if not path.exists():
        return pd.DataFrame()
    try:
        return load_csv(str(path))
    except Exception as error:
        st.error(f'Không thể đọc {path.name}: {error}')
        return pd.DataFrame()


def dataframe_to_records(df):
    return [] if df.empty else df.to_dict(orient='records')


def prepare_pipeline():
    students = safe_load('students')
    projects = safe_load('projects')
    progress = safe_load('progress')
    data = {
        'students': dataframe_to_records(students),
        'projects': dataframe_to_records(projects),
        'progress': dataframe_to_records(progress),
    }

    try:
        from cleaners import clean_all_data
        data = clean_all_data(data)
    except (ImportError, AttributeError):
        pass

    try:
        from validators import validate_all
        validation = validate_all(data)
    except (ImportError, AttributeError):
        validation = {'valid': True, 'errors': [], 'warnings': []}

    try:
        from statistics import calculate_all_statistics
        statistics = calculate_all_statistics(data)
    except (ImportError, AttributeError):
        statistics = {}

    return students, projects, progress, validation, statistics


def show_overview(students, projects, progress):
    values = pd.to_numeric(progress.get('progress', pd.Series(dtype=float)), errors='coerce').dropna()
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

    st.dataframe(filtered, use_container_width=True, hide_index=True)


def show_progress(progress):
    st.subheader('📊 Phân tích tiến độ')
    if progress.empty or 'progress' not in progress.columns:
        st.warning('Chưa có dữ liệu progress hợp lệ.')
        return

    chart = progress.copy()
    chart['progress'] = pd.to_numeric(chart['progress'], errors='coerce')
    chart = chart.dropna(subset=['progress'])
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
                st.metric(str(key), f'{value:.2f}' if isinstance(value, float) else value)


def main():
    st.title('📚 Theo dõi NCKH sinh viên')
    st.caption('FIT4018 – Lập trình Python | Nhóm 3 – Chủ đề 12')

    st.sidebar.header('⚙️ Điều khiển')
    if st.sidebar.button('🔄 Tải lại dữ liệu'):
        st.cache_data.clear()
        st.rerun()
    st.sidebar.info('Quản lý sinh viên, đề tài, tiến độ và kết quả nghiên cứu khoa học.')

    students, projects, progress, validation, statistics = prepare_pipeline()

    if students.empty and projects.empty and progress.empty:
        st.error('Chưa có dữ liệu CSV. Đặt 3 file vào thư mục data/.')
        st.stop()

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
