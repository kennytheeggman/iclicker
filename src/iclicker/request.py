import requests
import datetime
import logging

logger = logging.getLogger(__name__)

def POST(url: str, data: dict | None, headers: dict | None):
    res = requests.post(url, json=data, headers=headers)
    logger.debug(f"POST: {url}")
    return res

def GET(url: str, data: dict | None, headers: dict | None):
    res = requests.get(url, data=data, headers=headers)
    logger.debug(f"GET: {url}")
    return res

def gen_headers(content_type: str | None = None, auth: str | None = None):
    iso_date = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    ret_dict = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.5",
        "Client-Tag": f"ICLICKER/STUDENT-WEB/{iso_date}/Win/NT 10.0/Firefox/Web-Browser/136.0",
        "Connection": "keep-alive",
        "DNT": "1",
        "Host": "api.iclicker.com",
        "Origin": "https://student.iclicker.com",
        "Reef-Auth-Type": "oauth",
        "Referer": "https://student.iclicker.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Sec-GPC": "1",
        "TE": "Trailers",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0"
    }
    if content_type is not None:
        ret_dict["Content-Type"] = content_type
    if auth is not None:
        ret_dict["Authorization"] = auth
    return ret_dict
