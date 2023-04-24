import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов'

    def add_arguments(self, parser):
        parser.add_argument(
            'path_data', type=str, help='Путь к файлу с ингредиентами'
        )

    def handle(self, *args, **options):
        path_data = options.get('path_data')

        with open(path_data, 'r') as fdata:
            data = csv.reader(fdata)
            fields = ['name', 'measurement_unit']
            for row in data:
                record = dict(zip(fields, row))
                m = Ingredient(**record)
                m.save()
