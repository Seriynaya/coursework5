import requests
from celery import shared_task

from config import settings
from habits.models import Habit
from users.models import User


@shared_task
def telegram_reminder():
    """
    Задача отправки уведомления в телеграм
    """

    for habits in Habit.object.all():
        message = (
            f"Не забудьте выполнить привычку: {habits.action}\n"
            f"Время выполнения: {habits.time}\n"
            f"Место выполнения: {habits.spot}."
        )
        params = {"text": message, "tg_id": User.tg_id}
        requests.get(
            f"http://api.telegram.org/bot{settings.TELEGRAM_API_KEY}/sendMessage",
            params=params,
        )
