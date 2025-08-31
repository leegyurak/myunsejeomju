from django.core.management.base import BaseCommand
from infrastructure.database.models import TableModel


class Command(BaseCommand):
    help = 'Seed the database with initial table data'

    def handle(self, *args, **options):
        # Clear existing table data
        TableModel.objects.all().delete()
        
        # Create 15 tables
        num_tables = 15
        for i in range(1, num_tables + 1):
            TableModel.objects.create(name=f"{i}번 테이블")
            
        self.stdout.write(
            self.style.SUCCESS(f'Successfully seeded {num_tables} tables')
        )