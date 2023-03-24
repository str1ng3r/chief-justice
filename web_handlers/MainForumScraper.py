import asyncio

import feedparser
import aiohttp

from utils.enums import CaseType
from utils.models import Case
from database_managers.CaseManager import CaseManager
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
        cases = dict()

        async with aiohttp.ClientSession() as session:
            async with asyncio.TaskGroup() as tg:
                for case_type, url in self.URLS.items():
                    tasks[case_type] = tg.create_task(session.get(url))

            for case_type, response in tasks.items():
                feed = feedparser.parse(await response.result().text())
                for case in feed.entries:
                    Case(name=case['title'], url=case['link'], case_type=case_type).save()
                    cases[case['title']] = [case['link'], case_type]

        async with CaseManager() as cm:
            await cm.add_case(cases)
