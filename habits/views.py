from django.shortcuts import get_object_or_404
from django_celery_beat.models import PeriodicTask
from rest_framework import generics

from habits.models import Habit
from habits.paginators import HabitPagination
from habits.serializers import HabitSerializer, SimpleHabitSerializer
from users.permissions import IsUser


class HabitCreateAPIView(generics.CreateAPIView):
    """Создание новой привычки"""

    serializer_class = HabitSerializer

    def save_habit(self, serializer):
        """Сохраняет привычку и настраивает напоминания"""
        habit = serializer.save(user=self.request.user)

        if not habit.sign_pleasant_habit:
            self.setup_reminders(habit)

    def setup_reminders(self, habit):
        """Настраивает напоминания в Telegram"""
        if habit.user.tg_chat_id:  # Если у пользователя есть Telegram ID
            from habits.services import create_schedule, create_task

            schedule = create_schedule(habit.periodicity)
            create_task(schedule, habit)

    perform_create = save_habit


class SimpleHabitListAPIView(generics.ListAPIView):
    """Список публичных привычек"""

    serializer_class = SimpleHabitSerializer
    queryset = Habit.objects.filter(sign_pleasant_habit=True)


class UserHabitListAPIView(generics.ListAPIView):
    """Список привычек текущего пользователя"""

    serializer_class = HabitSerializer

    def get_user_habits(self):
        return Habit.objects.filter(user=self.request.user)

    get_queryset = get_user_habits


class HabitDetailAPIView(generics.RetrieveAPIView):
    """Просмотр одной привычки"""

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [IsUser]


class HabitUpdateAPIView(generics.UpdateAPIView):
    """Обновление привычки"""

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [IsUser]

    def update_habit(self, serializer):
        """Обновляет привычку и напоминания"""
        habit = serializer.save(user=self.request.user)

        if not habit.sign_pleasant_habit:
            self.update_reminders(habit)

    def update_reminders(self, habit):
        """Обновляет напоминания в Telegram"""
        if habit.user.tg_chat_id:
            from habits.services import create_schedule, create_task

            task = get_object_or_404(
                PeriodicTask, name=f"Отправить напоминание {habit.pk}"
            )
            task.delete()
            schedule = create_schedule(habit.frequency)
            create_task(schedule, habit)

    perform_update = update_habit


class HabitListAPIView(generics.ListAPIView):
    serializer_class = HabitSerializer
    pagination_class = HabitPagination

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)


class HabitRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = (IsUser,)


class HabitDestroyAPIView(generics.DestroyAPIView):
    """Удаление привычки"""

    queryset = Habit.objects.all()
    permission_classes = [IsUser]
