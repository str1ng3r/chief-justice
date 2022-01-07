from database_managers.DatabaseManagerBase import DatabaseManagerBase


class ReminderManager(DatabaseManagerBase):
    def __init__(self):
        super().__init__()
        self.collection = self.db['reminders']

    async def get_all_reminders(self):
        return await self.collection.find({}).to_list(length=None)

    async def count_reminders(self):
        return await self.collection.count_documents({})

    async def create_reminder(self, user_id, reminder_date, reminder_text):
        await self.collection.insert_one({
            'user_id': user_id,
            'reminder_date': reminder_date,
            'reminder_text': reminder_text
        })

    async def delete_reminder(self, reminder_id):
        await self.collection.delete_one({
            '_id': reminder_id
        })

    async def close(self):
        self.client.close()
