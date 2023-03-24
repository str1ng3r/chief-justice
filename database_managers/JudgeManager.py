from __future__ import annotations

from database_managers.DatabaseManagerBase import DatabaseManagerBase


class JudgeManager(DatabaseManagerBase):
    def __init__(self):
        super().__init__()
        self.collection = self.db['judges']

    async def add_judge(self, name, position, user_id):
        result = await self.collection.find_one({
                {
                    'name': name
                }
        })

        if result is not None:
            await self.collection.update_one({'_id': result['_id']}, {
                '$set': {
                    'name': name,
                    'position': position,
                    'user_id': user_id
                }
            })
        else:
            await self.collection.insert_one({
                'name': name,
                'position': position,
                'user_id': user_id
            })

    async def remove_judge(self, name):
        result = await self.collection.delete_one({'name': name})
        if result.deleted_count == 0:
            return -1

    async def remove_all_judges(self):
        await self.collection.delete_many({})

    async def add_multiple_judges(self, judge_list):
        return await self.collection.insert_many(judge_list)

    async def get_all_judges(self):
        return self.collection.find({})

    async def __aenter__(self) -> JudgeManager:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
