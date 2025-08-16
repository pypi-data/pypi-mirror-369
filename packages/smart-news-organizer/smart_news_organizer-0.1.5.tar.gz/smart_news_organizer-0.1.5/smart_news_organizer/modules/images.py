from PyQt5.QtGui import QPixmap, QImage, QColor
from io import BytesIO
import requests

# url = data['media_thumbnail']['url']
def get_pixmap_from_url(url):
    fallback = QPixmap(100, 100)
    fallback.fill(QColor("white"))

    if not url:
        return fallback

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        image_data = BytesIO(response.content)
        pixmap = QPixmap()
        if pixmap.loadFromData(image_data.read()):
            return pixmap
    except Exception:
        pass

    return fallback


