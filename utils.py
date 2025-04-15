from datetime import datetime

def format_date(date):
    """날짜를 'YYYY-MM-DD' 형식으로 반환"""
    return date.strftime("%Y-%m-%d")

def validate_image(file):
    """이미지 파일 검증 (확장자 체크 등)"""
    valid_extensions = ["jpg", "jpeg", "png"]
    file_extension = file.name.split('.')[-1].lower()
    if file_extension in valid_extensions:
        return True
    return False

def extract_tags(tags_input):
    """태그 입력을 처리하여 리스트로 반환 (콤마로 구분된 태그 처리)"""
    tags_list = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
    return tags_list

def format_temperature(temp):
    """온도 값 포맷 (소수점 한자리로 반환)"""
    try:
        return round(float(temp), 1)
    except ValueError:
        return None

def get_current_datetime():
    """현재 날짜 및 시간을 'YYYY-MM-DD HH:MM:SS' 형식으로 반환"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
