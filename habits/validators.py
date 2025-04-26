from datetime import datetime

from rest_framework import serializers

from habits.models import Habit


class HabitValidator:
    """Валидатор для проверки корректности данных привычки"""

    def validate_time_to_complete(self, attrs):
        """Проверяет, что время выполнения привычки не превышает 2 минут"""
        if attrs.get("time_to_complete", 0) > 120:
            raise serializers.ValidationError(
                "Время выполнения должно быть меньше 2 минут (120 секунд)"
            )

    def validate_related_habit(self, attrs):
        """Проверяет, что связанная привычка является приятной"""
        if not attrs.get("related_habit_id"):
            return

        related_habit = Habit.objects.get(pk=attrs["related_habit_id"])
        if not related_habit.is_pleasant:
            raise serializers.ValidationError(
                "Можно выбирать только приятные привычки в качестве связанных"
            )

    def validate_reward_and_related(self, attrs):
        """Проверяет, что не выбраны одновременно и награда,
         и связанная привычка"""
        if attrs.get("related_habit_id") and attrs.get("award"):
            raise serializers.ValidationError(
                "Нельзя одновременно выбирать связанную привычку и награду"
            )

    def validate_pleasant_habit(self, attrs):
        """Проверяет корректность настроек для приятной привычки"""
        is_pleasant = attrs.get("sign_pleasant_habit", False)

        if is_pleasant:
            if any(
                [
                    attrs.get("related_habit_id"),
                    attrs.get("award"),
                    attrs.get("periodicity"),
                    attrs.get("time"),
                ]
            ):
                raise serializers.ValidationError(
                    "Приятная привычка не может иметь награду,"
                    " связанную привычку или регулярность выполнения"
                )
        else:
            has_award = (
                attrs.get("award") and attrs.get("periodicity") and attrs.get("time")
            )
            has_related = (
                attrs.get("related_habit_id")
                and attrs.get("periodicity")
                and attrs.get("time")
            )

            if not (has_award or has_related):
                raise serializers.ValidationError(
                    "Полезная привычка должна иметь награду или связанную привычку, "
                    "а также время и регулярность выполнения"
                )

    def validate_time_settings(self, attrs):
        """Проверяет корректность временных настроек"""
        periodicity = attrs.get("periodicity", "")
        time = attrs.get("time")
        end_time = attrs.get("end_time")

        if not periodicity:
            return

        # Проверки для привычек, выполняемых несколько раз в день
        if "x" in periodicity:
            if not end_time:
                raise serializers.ValidationError(
                    "Для привычек, выполняемых несколько раз в день,"
                    " нужно указать время окончания"
                )
        elif end_time:
            raise serializers.ValidationError(
                "Время окончания можно указывать только для привычек,"
                " выполняемых несколько раз в день"
            )

        # Проверки корректности временного диапазона
        if time and end_time:
            time_date = datetime.fromisoformat(time).date()
            end_date = datetime.fromisoformat(end_time).date()

            if time_date != end_date:
                raise serializers.ValidationError(
                    "Время начала и окончания должны быть в один день"
                )
            if end_time <= time:
                raise serializers.ValidationError(
                    "Время окончания должно быть позже времени начала"
                )

    def validate_days_week(self, attrs):
        """Проверяет корректность выбора дней недели"""
        periodicity = attrs.get("periodicity", "")
        days = attrs.get("days_week")

        if "d" in periodicity and not days:
            raise serializers.ValidationError(
                "Для привычек, выполняемых в определенные дни"
                " недели, нужно указать эти дни"
            )
        elif "d" not in periodicity and days:
            raise serializers.ValidationError(
                "Дни недели можно указывать только для привычек,"
                " выполняемых в определенные дни"
            )

    def __call__(self, attrs):
        """Основной метод валидации"""
        self.validate_time_to_complete(attrs)
        self.validate_related_habit(attrs)
        self.validate_reward_and_related(attrs)
        self.validate_pleasant_habit(attrs)
        self.validate_time_settings(attrs)
        self.validate_days_week(attrs)
