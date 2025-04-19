from django.core.management import BaseCommand, call_command

from habits.models import Week


class Command(BaseCommand):
    """Создает дни недели в базе данных"""

    def handle(self, *args, **options):
        Week.objects.all().delete()
        self.load_weekdays()
        self.print_success()

    def load_weekdays(self):
        """Загружает дни недели из фикстуры"""
        call_command("loaddata", "weekdays_fixture.json")

    def print_success(self):
        """Выводит сообщение об успешном выполнении"""
        self.stdout.write("Дни недели успешно созданы!")
