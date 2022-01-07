from database_managers.DatabaseManagerBase import DatabaseManagerBase
from datetime import datetime


class LawyerManager(DatabaseManagerBase):
    def __init__(self):
        super().__init__()
        self.collection = self.db['attorneys']

    async def get_lawyer_by_bar_id(self, bar_id):
        """
        This function searches the database for a lawyer by it's bar id.
        :param bar_id: The bar ID, AKA their character ID
        :return: returns the lawyer object, or 1 if not found.
        """
        lawyer = await self.collection.find_one({'bar_id': bar_id})
        if lawyer is None:
            return 1
        return lawyer

    async def add_lawyer(self, lawyer_data):
        """
        Inserts a lawyer in the database.
        :param lawyer_data: List with details from the registry addition forum post, formatted properly.
        :return: 0, if inserted, 2 if lawyer already exist, 1 if error with lawyer_data
        """
        if len(lawyer_data) != 12:
            return 1
        if await self.get_lawyer_by_bar_id(lawyer_data[1]) != 1:
            return 2
        await self.collection.insert_one({
            'name': lawyer_data[0],
            'bar_id': lawyer_data[1],
            'firm': lawyer_data[2],
            'specialty': lawyer_data[3],
            'availability': lawyer_data[4],
            'billing': lawyer_data[5],
            'phone': lawyer_data[6],
            'email': lawyer_data[7],
            'forum_name': lawyer_data[8],
            'discord': lawyer_data[9],
            'exp_date': lawyer_data[10],
            'user_id': lawyer_data[11]
        })
        return 0

    async def edit_lawyer(self, bar_id, field, new_data):
        if await self.get_lawyer_by_bar_id(bar_id) == 1:
            return 1
        await self.collection.update_one({"bar_id": bar_id}, {
            '$set': {
                f'{field}': new_data
            }
        })
        return 0

    async def remove_lawyer(self, bar_id):
        if await self.get_lawyer_by_bar_id(bar_id) == 1:
            return 1
        await self.collection.delete_one({'bar_id': bar_id})
        return 0

    def get_lawyers(self):
        lawyers = self.collection.find({})
        return lawyers

    async def get_expired_lawyers(self):
        today = datetime.now().timestamp()
        expired_lawyers = self.collection.find({
            "exp_date": {"$lt": today}
        })
        return expired_lawyers

    async def set_expired_tag(self, bar_id):
        await self.collection.update_one({'bar_id': bar_id}, {
            '$set': {
                'expired': True
            }
        })

    async def renew(self, bar_id):
        two_months = datetime.now().timestamp() + 5_259_492
        await self.collection.update_one({'bar_id': bar_id}, {
            '$unset': {
                'expired': ''
            },
            '$set': {
                'exp_date': two_months
            }
        })
