''' Подгружаем список ингридиентов.'''

import csv

from django.conf import settings
from django.core.management import BaseCommand
from recipes.models import Ingredients

TABLES = {
    Ingredients: 'ingredients.csv',
}


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for model, csv_files in TABLES.items():
            with open(
                f'{settings.BASE_DIR}/data/{csv_files}',
                'r',
                encoding='utf-8',
            ) as csv_file:
                reader = csv.reader(csv_file)
                model.objects.bulk_create(
                    model(name=data[0], measurement_unit=data[1])
                    for data in reader
                )
        self.stdout.write(self.style.SUCCESS('Все данные загружены'))
