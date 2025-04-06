import re, html
from bs4 import BeautifulSoup

def clean_html(raw: str) -> str:
    text = html.unescape(raw)                               # Unescape HTML entities
    text = re.sub(r'<[^>]+>', '', text)                     # Remove all HTML tags
    text = re.sub(r'~~~\([^)]*\)~~~', '', text)             # Remove spoiler formatting
    text = re.sub(r'~~~img\d+\(.*?\)~~~', '', text)         # Remove all the image embeds
    text = re.sub(
        r'https?://\S+\.(?:jpg|jpeg|png|gif|bmp|webp)(?:\?\S*)?',
        '',
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(r'(?m)^\s{0,3}#{1,6}\s*.*$', '', text)    # Remove lines starting with #…  
    text = re.sub(r'(?m)^-{3,}.*$',     '', text)           # Remove --- separators
    text = re.sub(r'(\*{1,2}|_{1,2}|~~)', '', text)         # Emphasis and strikethroughs

    text = BeautifulSoup(text, 'html.parser').get_text()
    text = re.sub(r'[*_]{1,2}', '', text)                   # Remove *italic*, **bold**, __underline__
    text = text.replace('~', '')                            # People use ~?
    return text.strip()