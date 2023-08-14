import re

from dependency_injector.wiring import Container, Provide, inject
from mmpy_bot import Message, Plugin, listen_to

from src.core.db.repository.admin import AdminRepository
from src.settings import Settings


@inject
class Admin(Plugin):
    @listen_to("Admin", re.IGNORECASE)
    async def admin(self, message: Message, settings: Settings):
        admin_id = AdminRepository.get_admin_id(self, settings)
        if message.user_id == admin_id:
            self.driver.reply_to(message, "Привет, админ!")
        else:
            self.driver.reply_to(message, "Недостаточно прав!")
