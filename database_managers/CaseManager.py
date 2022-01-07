from database_managers.DatabaseManagerBase import DatabaseManagerBase
from datetime import datetime


class CaseManager(DatabaseManagerBase):
    def __init__(self):
        super().__init__()
        self.collection = self.db['cases']

    async def get_available_cases(self):
        results = self.collection.find({"justice": 0})
        return results

    async def get_case_by_kv(self, key, value):
        # Finds a case based on a key/value
        return await self.collection.find_one({f'{key}': value})

    async def get_non_archived(self):
        results = self.collection.find({"archived": 0})
        return results

    async def make_unavailable(self, name, user):
        print('here')
        current_time = datetime.now()
        await self.collection.update_one({'name': name}, {
            '$set':
                {
                    'justice': 1,
                    'handler': user,
                    'month': current_time.month,
                    'year': current_time.year
                }
        })

    async def make_available(self, url):
        result = await self.collection.update_one({'url': url}, {
            '$set': {
                'justice': 0
            }, '$unset': {
                'handler': ''
            }
        })
        return result

    async def add_case(self, cases):
        """
        :param cases: dictionary of cases
        :return:
        """
        for name, values in cases.items():
            await self.collection.update_one({'url': values[0]}, {
                '$setOnInsert': {
                    'name': name,
                    'url': values[0],
                    'justice': 0,
                    'archived': 0,
                },
                '$set': {
                    'case_type': values[1]
                }
            }, upsert=True)

    async def archive_case(self, url):
        await self.collection.update_one({'url': url}, {
            '$set': {
                'archived': 1
            }
        })

    async def get_cases_year_month(self, year, month, judge_id=None):
        if judge_id is None:
            count = await self.collection.count_documents({"year": year, "month": month})
            if count == 0:
                return None
            return self.collection.find({"year": year, "month": month, "justice": 1})
        if judge_id is not None:
            count = await self.collection.count_documents({"year": year, "month": month, 'handler': judge_id})
            if count == 0:
                return None
            return self.collection.find({"year": year, "month": month, "justice": 1, 'handler': judge_id})
