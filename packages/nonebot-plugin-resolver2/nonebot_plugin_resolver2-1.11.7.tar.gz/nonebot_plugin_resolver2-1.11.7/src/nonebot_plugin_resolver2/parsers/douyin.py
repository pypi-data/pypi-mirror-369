import json
import re
from typing import Any

import httpx
from nonebot import logger

from ..constants import COMMON_TIMEOUT
from ..exception import ParseException
from .data import ANDROID_HEADER, IOS_HEADER, ParseResult
from .utils import get_redirect_url


class DouyinParser:
    def __init__(self):
        self.ios_headers = IOS_HEADER.copy()
        self.android_headers = {"Accept": "application/json, text/plain, */*", **ANDROID_HEADER}

    def _build_iesdouyin_url(self, _type: str, video_id: str) -> str:
        return f"https://www.iesdouyin.com/share/{_type}/{video_id}"

    def _build_m_douyin_url(self, _type: str, video_id: str) -> str:
        return f"https://m.douyin.com/share/{_type}/{video_id}"

    async def parse_share_url(self, share_url: str) -> ParseResult:
        if matched := re.match(r"(video|note)/([0-9]+)", share_url):
            # https://www.douyin.com/video/xxxxxx
            _type, video_id = matched.group(1), matched.group(2)
            iesdouyin_url = self._build_iesdouyin_url(_type, video_id)
        else:
            # https://v.douyin.com/xxxxxx
            iesdouyin_url = await get_redirect_url(share_url)
            # https://www.iesdouyin.com/share/video/7468908569061100857/?region=CN&mid=0&u_
            matched = re.search(r"(slides|video|note)/(\d+)", iesdouyin_url)
            if not matched:
                raise ParseException(f"无法从 {share_url} 中解析出 ID")
            _type, video_id = matched.group(1), matched.group(2)
            if _type == "slides":
                return await self.parse_slides(video_id)
        for url in [
            self._build_m_douyin_url(_type, video_id),
            share_url,
            iesdouyin_url,
        ]:
            try:
                return await self.parse_video(url)
            except ParseException as e:
                logger.warning(f"failed to parse {url[:60]}, error: {e}")
                continue
            except Exception as e:
                logger.warning(f"failed to parse {url[:60]}, unknown error: {e}")
                continue
        raise ParseException("作品已删除，或资源直链获取失败, 请稍后再试")

    async def parse_video(self, url: str) -> ParseResult:
        async with httpx.AsyncClient(headers=self.ios_headers, verify=False, timeout=COMMON_TIMEOUT) as client:
            response = await client.get(url)
            response.raise_for_status()
            text = response.text
        data: dict[str, Any] = self._format_response(text)
        # 获取图集图片地址
        images: list[str] = []
        # 如果data含有 images，并且 images 是一个列表
        if "images" in data and isinstance(data["images"], list):
            # 获取每个图片的url_list中的第一个元素，非空时添加到images列表中
            for img in data["images"]:
                assert isinstance(img, dict)
                if (
                    "url_list" in img
                    and isinstance(img["url_list"], list)
                    and len(img["url_list"]) > 0
                    and len(img["url_list"][0]) > 0
                ):
                    images.append(img["url_list"][0])

        # 获取视频播放地址
        video_url: str = data["video"]["play_addr"]["url_list"][0].replace("playwm", "play")

        if video_url:
            # 获取重定向后的mp4视频地址
            video_url = await get_redirect_url(video_url)

        share_info = ParseResult(
            title=data["desc"],
            cover_url=data["video"]["cover"]["url_list"][0],
            pic_urls=images,
            video_url=video_url,
            author=data["author"]["nickname"],
            # author=Author(
            #     # uid=data["author"]["sec_uid"],
            #     name=data["author"]["nickname"],
            #     avatar=data["author"]["avatar_thumb"]["url_list"][0],
            # ),
        )
        return share_info

    def _format_response(self, text: str) -> dict[str, Any]:
        pattern = re.compile(
            pattern=r"window\._ROUTER_DATA\s*=\s*(.*?)</script>",
            flags=re.DOTALL,
        )
        find_res = pattern.search(text)

        if not find_res or not find_res.group(1):
            raise ParseException("can't find _ROUTER_DATA in html")

        json_data = json.loads(find_res.group(1).strip())

        # 获取链接返回json数据进行视频和图集判断,如果指定类型不存在，抛出异常
        # 返回的json数据中，视频字典类型为 video_(id)/page
        VIDEO_ID_PAGE_KEY = "video_(id)/page"
        # 返回的json数据中，视频字典类型为 note_(id)/page
        NOTE_ID_PAGE_KEY = "note_(id)/page"
        if VIDEO_ID_PAGE_KEY in json_data["loaderData"]:
            original_video_info = json_data["loaderData"][VIDEO_ID_PAGE_KEY]["videoInfoRes"]
        elif NOTE_ID_PAGE_KEY in json_data["loaderData"]:
            original_video_info = json_data["loaderData"][NOTE_ID_PAGE_KEY]["videoInfoRes"]
        else:
            raise ParseException("failed to parse Videos or Photo Gallery info from json")

        # 如果没有视频信息，获取并抛出异常
        if len(original_video_info["item_list"]) == 0:
            err_msg = "failed to parse video info from HTML"
            if len(filter_list := original_video_info["filter_list"]) > 0:
                err_msg = filter_list[0]["detail_msg"] or filter_list[0]["filter_reason"]
            raise ParseException(err_msg)

        return original_video_info["item_list"][0]

    async def parse_slides(self, video_id: str) -> ParseResult:
        url = "https://www.iesdouyin.com/web/api/v2/aweme/slidesinfo/"
        params = {
            "aweme_ids": f"[{video_id}]",
            "request_source": "200",
        }
        async with httpx.AsyncClient(headers=self.android_headers, verify=False) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            resp = response.json()
        detail = resp.get("aweme_details")
        if not detail:
            raise ParseException("can't find aweme_details in json")
        data = detail[0]
        title = data.get("share_info").get("share_desc_info")
        images = []
        dynamic_images = []
        for image in data.get("images"):
            video = image.get("video")
            if video:
                dynamic_images.append(video["play_addr"]["url_list"][0])
            else:
                images.append(image["url_list"][0])

        return ParseResult(
            title=title,
            cover_url="",
            author=data["author"]["nickname"],
            # author=Author(
            #     name=data["author"]["nickname"],
            #     avatar=data["author"]["avatar_thumb"]["url_list"][0],
            # ),
            pic_urls=images,
            dynamic_urls=dynamic_images,
        )
