import asyncio

import feedparser
import aiohttp

from utils.enums import CaseType
from utils.models import Case
from config import RSS_KEY, RSS_MEMBER


class MainForumScraper:
    URLS = {
        CaseType.CRIMINAL: f'https://forum.gta.world/en/forum/389-criminal-division.xml/'
                           f'?member={RSS_MEMBER}&key={RSS_KEY}',
        CaseType.CIVIL: f'https://forum.gta.world/en/forum/390-civil-division.xml/?member={RSS_MEMBER}&key={RSS_KEY}',
        CaseType.TRAFFIC: f'https://forum.gta.world/en/forum/708-traffic-division.xml/'
                          f'?member={RSS_MEMBER}&key={RSS_KEY}'
    }

    def __init__(self):
        pass

    async def get_cases(self) -> None:
        tasks = dict()

        async with aiohttp.ClientSession() as session:
            async with asyncio.TaskGroup() as tg:
                for case_type, url in self.URLS.items():
                    tasks[case_type] = tg.create_task(session.get(url))

            for case_type, response in tasks.items():
                feed = feedparser.parse(await response.result().text())
                for case in feed.entries:
                    Case.objects(url=case['link']).modify(upsert=True,
                                                          set_on_insert__name=case['title'],
                                                          set_on_insert__case_type=case_type,
                                                          set_on_insert__archived=False,
                                                          set_on_insert__justice=False)
