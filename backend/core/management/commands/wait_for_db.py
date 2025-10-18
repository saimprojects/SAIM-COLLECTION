from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
import time


class Command(BaseCommand):
    help = "Wait for database to be available"

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")
        conn = connections["default"]
        max_attempts = 30
        attempts = 0
        while attempts < max_attempts:
            try:
                conn.ensure_connection()
                self.stdout.write(self.style.SUCCESS("Database available!"))
                return
            except OperationalError:
                attempts += 1
                time.sleep(1)
        self.stdout.write(self.style.ERROR("Database not available after multiple attempts"))