import logging
import webbrowser

log = logging.getLogger(__name__)

def open_url(url: str, new: int = 2) -> str:
    """
    Открыть URL в браузере.
    new: 0 same window, 1 new window, 2 new tab (чаще всего удобно).
    """
    if not url:
        raise ValueError("uri is empty")

    ok = webbrowser.open(url, new=new)
    if not ok:
        log.warning("webbrowser.open returned False for url=%r", url)
