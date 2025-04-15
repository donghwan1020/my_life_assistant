import streamlit as st
from datetime import datetime
from google_api import connect_gsheets, upload_to_drive, extract_file_id_from_url, get_drive_image_url


st.set_page_config(page_title="날씨 사진 기록", layout="wide")

st.title("👗나의 날씨 & 사진 기록 앱")

# 세션 상태 초기화
if "show_form" not in st.session_state:
    st.session_state["show_form"] = False

# "오늘 기록하기" 버튼 처리
if st.button("📅 오늘 기록하기"):
    st.session_state["show_form"] = True
    st.rerun()  # 페이지 새로고침 (리로드)

if st.session_state["show_form"]:
    # ✅ 오늘 기록 폼
    with st.form("weather_form", clear_on_submit=True):
        date = st.date_input("날짜", value=datetime.today())
        image = st.file_uploader("📷 오늘의 사진", type=["jpg", "png"])
        tags = st.text_input("태그 (콤마로 구분)", help="태그를 입력하세요. 예: #여름, #출근, #편안한")

        st.subheader("🌤️ 날씨 정보")
        # 최저, 최고 기온 입력 필드에서 소수점 없이 정수만 입력 받기
        temp_min = int(st.number_input("최저 기온 (°C)", min_value=-50, max_value=50, step=1, value=0))
        temp_max = int(st.number_input("최고 기온 (°C)", min_value=-50, max_value=50, step=1, value=20))

        humidity = st.slider("습도 (%)", 0, 100, 50)
        weather = st.selectbox("날씨 상태", ["맑음", "흐림", "비", "눈", "황사", "기타"])
        season = st.selectbox("계절", ["봄", "여름", "가을", "겨울"])

        comment = st.text_area("📝 내 느낌/메모")

        submitted = st.form_submit_button("저장")
        if submitted:
            if image:
                # Drive에 이미지 업로드
                image_url = upload_to_drive(image, st.secrets["drive"]["drive_folder_id"])

                # Sheets에 데이터 추가
                client = connect_gsheets()
                sheet = client.open_by_key(st.secrets["sheet"]["sheet_id"]).sheet1

                sheet.append_row([
                    str(datetime.now()),  # 기록 ID
                    date.strftime("%Y-%m-%d"),
                    image_url,
                    str(temp_min),
                    str(temp_max),
                    str(humidity),
                    weather,
                    comment,
                    season,
                    tags
                ])
                
                st.success("기록이 저장되었습니다! 🎉")
                st.session_state["show_form"] = False
                st.rerun()  # 폼 제출 후 페이지 새로고침
else:
    # ✅ 첫 화면: 필터 & 기록 리스트
    st.subheader("📖 기록된 사진들")

    try:
        client = connect_gsheets()
        sheet = client.open_by_key(st.secrets["sheet"]["sheet_id"]).sheet1
        records = sheet.get_all_records()

        if not records:
            st.info("기록이 없습니다.")
        else:
            # 최신순으로 출력
            cols_per_row = 3  # 한 줄에 몇 개씩 보여줄지 설정
            rows = [records[i:i + cols_per_row] for i in range(0, len(records), cols_per_row)]
            
            for row in reversed(rows):  # 최신 순
                columns = st.columns(cols_per_row)
                for col, r in zip(columns, row):
                    image_url = r.get('Image URL') or r.get('image_url') or ''
                    if image_url:
                        file_id = extract_file_id_from_url(image_url)
                        thumbnail_url = get_drive_image_url(file_id)

                        with col:
                            card_html = f"""
                            <div style="
                                border: 1px solid #e0e0e0;
                                border-radius: 16px;
                                padding: 16px;
                                margin: 10px;
                                box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
                                width: 270px;
                                display: inline-block;
                                vertical-align: top;
                                background-color: #ffffff;
                            ">
                                <img src="{thumbnail_url}" style="width:250px; height:300px; object-fit:cover; border-radius: 12px;">
                                <div style="margin-top: 10px; font-size: 14px;">
                                    <strong>📅 날짜:</strong> {r.get('Date', '')}<br>
                                    <strong>🌡 온도:</strong> {r.get('Min Temp', '')}°C ~ {r.get('Max Temp', '')}°C<br>
                                    <strong>💧 습도:</strong> {r.get('Humidity', '')}%<br>
                                    <strong>⛅ 날씨:</strong> {r.get('Weather', '')}<br>
                                    <strong>🍂 계절:</strong> {r.get('Season', '')}<br>
                                    <strong>🏷 태그:</strong> {r.get('Tags', '')}<br>
                                    <strong>📝 메모:</strong> {r.get('Comment', '')}
                                </div>
                            </div>
                            """

                            st.markdown(card_html, unsafe_allow_html=True)

                    else:
                        st.warning("이미지 링크가 누락된 기록이 있습니다.")
    except Exception as e:
        st.error(f"기록을 불러오는 중 오류가 발생했습니다: {e}")



