import re

import structlog
from dependency_injector.wiring import Provide, inject
from mmpy_bot import Message, Plugin, listen_to

from src.bot.schemas import Action, Actions, Attachment, Integration
from src.bot.services.week_routine import NotifyService
from src.depends import Container

FRIDAY_TIME_SENDING_MESSAGE = 11
DAY_OF_WEEK_FRI = "fri"
LOGGER = structlog.get_logger()


class WeekRoutine(Plugin):
    action_yes = Actions(
        id="Yes", name="Да", type="botton", integration=Integration(url="", context=Action(action="yes"))
    )

    action_no = Actions(
        id="No", name="Нет", type="botton", integration=Integration(url="", context=Action(action="no"))
    )

    every_friday_message = Attachment(
        text="Хочешь ли принять участие в random coffee на следующей неделе?", actions=[action_yes, action_no]
    )

    @listen_to("/send_asking_message", re.IGNORECASE)
    @inject
    async def send_asking_message(
        self, message: Message, routine_service: NotifyService = Provide[Container.week_routine_service]
    ):
        """Отправка сообщения по команде в канал"""
        await routine_service.notify_all_users(self, attachments=self.every_friday_message, title="Тестовая отправка")

    def on_start(
        self,
        routine_service: NotifyService = Provide[Container.week_routine_service,],
        scheduler=Provide[Container.scheduler],
    ):
        scheduler.add_job(
            routine_service.notify_all_users,
            "cron",
            day_of_week=DAY_OF_WEEK_FRI,
            hour=FRIDAY_TIME_SENDING_MESSAGE,
            kwargs=dict(plugin=self, attachments=self.every_friday_message, title="Еженедельный пятничный опрос"),
        )
        # -----------------------------------для теста:
        # scheduler.add_job(
        #     routine_service.notify_all_users,
        #     'interval', seconds=20,
        #     kwargs=dict(
        #         plugin=self,
        #         attachments=self.every_friday_message,
        #         title="Еженедельный пятничный опрос"
        #     )
        # )
        # -----------------------------------

        scheduler.start()

    @listen_to("stop jobs", re.IGNORECASE)
    def cancel_jobs(self, message, scheduler=Provide[Container.scheduler]):
        scheduler.shutdown()
        self.driver.reply_to(message, "All jobs cancelled.")
