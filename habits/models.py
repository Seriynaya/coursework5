from django.db import models

from users.models import User


class Week(models.Model):
    day = models.CharField(max_length=10, verbose_name="day week")


class Habit(models.Model):
    HABIT_PERIODICITY = (
        ("m x-y * * *", "every hour"),
        ("m x-y/2 * * *", "every 2 hours"),
        ("m x-y/3 * * *", "every 3 hours"),
        ("m x,z,y * * *", "3 times per day"),
        ("m x,y * * *", "2 times per day"),
        ("m h * * *", "every day"),
        ("m h */2 * *", "every 2 days"),
        ("m h */3 * *", "every 3 days"),
        ("m h * * d", "selected days"),
    )
    user = models.ForeignKey(
        User,
        verbose_name="user",
        on_delete=models.CASCADE,
        related_name="habits",
        null=True,
        blank=True,
    )
    spot = models.CharField(
        verbose_name="spot",
        max_length=250,
        help_text="Место, в котором необходимо выполнять привычку",
    )
    time = models.DateTimeField(
        verbose_name="time",
        null=True,
        blank=True,
        help_text="Время, в которое необходимо выполнять привычку",
    )
    action = models.CharField(
        verbose_name="action",
        max_length=250,
        help_text="Действие, которое предоставляет собой привычка",
    )
    sign_pleasant_habit = models.BooleanField(
        verbose_name="sign_pleasant_habit",
        help_text="Привычка, которую можно привязать к"
                  " выполнению полезной привычки",
    )
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        verbose_name="related habit",
        blank=True,
        null=True,
        help_text="Привычка, которая связана с другой привычкой,"
                  " важно указывать для полезных привычек, но не для приятных.",
    )
    periodicity = models.PositiveIntegerField(
        choices=HABIT_PERIODICITY,
        verbose_name="periodicity",
        default="m h * * *",
        blank=True,
        null=True,
        help_text="Периодичность выполнения привычки для напоминания в днях.",
    )
    award = models.CharField(
        verbose_name="award",
        max_length=250,
        blank=True,
        null=True,
        help_text="Чем пользователь должен себя"
                  " вознаградить после выполнения.",
    )
    time_to_complete = models.PositiveIntegerField(
        verbose_name="time to complete",
        help_text="Время, которое предположительно потратит"
                  " пользователь на выполнение привычки.",
    )
    sign_publicity = models.BooleanField(
        verbose_name="sign publicity",
        help_text="Привычки можно публиковать в общий"
                  " доступ, чтобы другие пользователи могли"
                  " брать в пример чужие привычки.",
    )
    end_time = models.DateTimeField(
        verbose_name="end time",
        null=True,
        blank=True,
        help_text="Время к которому пользователь закончит действие привычки",
    )
    days_week = models.ManyToManyField(
        Week,
        verbose_name="days_week",
        blank=True,
        null=True,
        help_text="Выберите день, в который осуществляется привычка",
    )

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"

    def __str__(self):
        return f"Привычка - {self.action}"
