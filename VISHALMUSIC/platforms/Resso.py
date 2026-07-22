import re
from typing import Union

import aiohttp
from bs4 import BeautifulSoup
from py_yt import VideosSearch


class RessoAPI:
    def __init__(self):
        self.regex = r"^(https:\/\/m.resso.com\/)(.*)$"
        self.base = "https://m.resso.com/"

    async def valid(self, link: str):
        if re.search(self.regex, link):
            return True
        else:
            return False

    async def track(self, url, playid: Union[bool, str] = None):
        if playid:
            url = self.base + url
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return False
                html = await response.text()
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all("meta"):
            if tag.get("property", None) == "og:title":
                title = tag.get("content", None)
            if tag.get("property", None) == "og:description":
                des = tag.get("content", None)
                try:
                    des = des.split("·")[0]
                except:
                    pass
        if des == "":
            return
        results = VideosSearch(title, limit=1)
        search_result = await results.next()
        result_list = search_result.get("result", [])
        if not result_list or len(result_list) == 0:
            return
        result = result_list[0]
        title = result.get("title", "")
        ytlink = result.get("link", "")
        vidid = result.get("id", "")
        duration_min = result.get("duration", "")
        thumbnails = result.get("thumbnails", [])
        thumbnail = thumbnails[0].get("url", "") if thumbnails else ""
        thumbnail = thumbnail.split("?")[0] if thumbnail else ""
        track_details = {
            "title": title,
            "link": ytlink,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid
