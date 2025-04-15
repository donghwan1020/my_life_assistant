import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime
import os
import base64
from PIL import Image
from io import BytesIO
from googleapiclient.http import MediaIoBaseUpload
from urllib.parse import urlparse, parse_qs

# 구글 서비스 인증
def connect_gsheets():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )
    client = gspread.authorize(creds)
    return client

def connect_drive():
    scope = ["https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )
    service = build("drive", "v3", credentials=creds)
    return service

# 사진 Google Drive에 업로드
def upload_to_drive(image_file, folder_id):
    drive_service = connect_drive()

    # 확장자 추출 및 이미지 열기
    filename = image_file.name
    extension = os.path.splitext(filename)[1].lower().replace('.', '')  # 예: 'png', 'jpg'

    # 지원하는 이미지 확장자 목록
    supported_extensions = ["jpg", "jpeg", "png", "webp", "bmp"]
    if extension not in supported_extensions:
        raise ValueError(f"지원하지 않는 이미지 형식입니다: {extension}")

    image = Image.open(image_file)

    # 이미지 저장 버퍼 준비
    buffer = BytesIO()
    image_format = "JPEG" if extension in ["jpg", "jpeg"] else extension.upper()
    image.save(buffer, format=image_format)
    buffer.seek(0)

    # 파일 메타데이터 및 업로드 준비
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_metadata = {
        "name": f"{timestamp}.{extension}",
        "parents": [folder_id]
    }
    media = MediaIoBaseUpload(buffer, mimetype=f"image/{extension}")

    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    file_id = uploaded_file["id"]
    
    # 🔥 공개 링크로 접근 가능하도록 권한 부여
    drive_service.permissions().create(
        fileId=file_id,
        body={"role": "reader", "type": "anyone"},
    ).execute()
    
    
    return f"https://drive.google.com/uc?id={file_id}"


def extract_file_id_from_url(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    return query.get("id", [None])[0]

def get_drive_image_url(file_id: str):
    return f"https://drive.google.com/thumbnail?id={file_id}"
