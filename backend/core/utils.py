import hashlib
import uuid
from datetime import datetime


def generate_unique_id():
    return str(uuid.uuid4())


def hash_file_content(content):
    return hashlib.sha256(content).hexdigest()


def parse_date(date_str, formats=None):
    if formats is None:
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except (ValueError, TypeError):
            continue
    return None


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def clean_string(value):
    if isinstance(value, str):
        return value.strip().upper()
    return str(value).strip().upper() if value else ''
