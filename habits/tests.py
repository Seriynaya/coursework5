from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from habits.models import Habit

User = get_user_model()


class TestHabitModel(TestCase):
    """Тесты модели привычки"""

    def setUp(self):
        self.user = User.objects.create(username="test_user")
        self.habit_data = {
            "spot": "Дом",
            "time": "14:00",
            "action": "Чтение",
            "sign_pleasant_habit": True,
            "periodicity": 2,
            "award": "",
            "time_to_complete": 100,
            "sign_publicity": True,
            "user": self.user,
        }

    def test_create_habit(self):
        habit = Habit.objects.create(**self.habit_data)
        self.assertEqual(habit.action, "Чтение")
        self.assertEqual(habit.spot, "Дом")

    def test_habit_str(self):
        habit = Habit.objects.create(**self.habit_data)
        self.assertEqual(str(habit), "Чтение")


class TestHabitAPI(TestCase):
    """Тесты API привычек"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username="api_user")
        self.client.force_authenticate(user=self.user)

        self.habit = Habit.objects.create(
            user=self.user,
            spot="Офис",
            action="Работа",
            time="09:00",
            time_to_complete=90,
            sign_publicity=False,
        )

    def test_create_habit(self):
        response = self.client.post(
            "/habits/",
            {
                "spot": "Спортзал",
                "action": "Тренировка",
                "time": "18:00",
                "time_to_complete": 60,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_habit(self):
        response = self.client.patch(
            f"/habits/{self.habit.id}/", {"action": "Обновленная задача"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.habit.refresh_from_db()
        self.assertEqual(self.habit.action, "Обновленная задача")

    def test_delete_habit(self):
        response = self.client.delete(f"/habits/{self.habit.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Habit.objects.filter(id=self.habit.id).exists())

    def test_public_habits_list(self):
        Habit.objects.create(
            user=self.user, action="Публичная привычка", sign_publicity=True
        )
        response = self.client.get("/public-habits/")
        self.assertEqual(len(response.data), 1)
