import re, html

def clean_html(raw: str) -> str:
    text = html.unescape(raw)  # Unescape HTML entities
    text = re.sub(r'<[^>]+>', '', text)  # Remove all HTML tags
    text = re.sub(r'[*_]{1,2}', '', text)  # Remove *italic*, **bold**, __underline__
    return text.strip()