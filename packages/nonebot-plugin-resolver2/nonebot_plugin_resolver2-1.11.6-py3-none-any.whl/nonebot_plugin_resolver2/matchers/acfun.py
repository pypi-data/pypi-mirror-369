import re

from nonebot import logger

from ..config import NICKNAME
from ..exception import handle_exception
from ..parsers import AcfunParser
from .helper import obhelper
from .preprocess import ExtractText, on_url_keyword

acfun = on_url_keyword("acfun.cn")

parser = AcfunParser()


@acfun.handle()
@handle_exception()
async def _(text: str = ExtractText()):
    matched = re.search(r"(?:ac=|/ac)(\d+)", text)
    if not matched:
        logger.info("acfun 链接中不包含 acid, 忽略")
        return
    acid = int(matched.group(1))
    url = f"https://www.acfun.cn/v/ac{acid}"
    m3u8_url, video_desc = await parser.parse_url(url)
    await acfun.send(f"{NICKNAME}解析 | 猴山 - {video_desc}")

    video_file = await parser.download_video(m3u8_url, acid)
    await acfun.send(obhelper.video_seg(video_file))
