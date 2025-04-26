from rest_framework import serializers

from habits.models import Habit
from habits.validators import HabitValidator


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = "__all__"
        validators = [HabitValidator()]

    def prepare_data(self, data):
        """Подготавливает данные перед проверкой"""
        if self.instance:  # Если привычка уже существует
            # Если дни недели не указаны - берем текущие
            if "days_of_week" not in data:
                data["days_of_week"] = [
                    day.id for day in self.instance.days_of_week.all()
                ]
            # Для всех полей, которые не пришли - берем текущие значения
            for field_name in self.fields:
                if field_name not in data:
                    data[field_name] = getattr(self.instance, field_name)
        return data


class SimpleHabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = ["action", "sign_pleasant_habit", "time_to_complete"]
