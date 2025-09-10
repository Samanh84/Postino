import os
import json
from django.core.management.base import BaseCommand
from post.models import Province, City
from django.conf import settings


class Command(BaseCommand):
    help = "Load provinces and cities from Province.txt JSON file"

    def handle(self, *args, **kwargs):
        # مسیر فایل (کنار manage.py → پوشه data → Province.txt)
        file_path = os.path.join(settings.BASE_DIR, "data", "Province.txt")

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR("❌ Province.txt not found"))
            return

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in data:
            province_name = item["province"].strip()
            province_obj, _ = Province.objects.get_or_create(name=province_name)

            # اگه cities تعریف شده باشه
            cities = item.get("cities", [])
            for city_name in cities:
                City.objects.get_or_create(
                    name=city_name.strip(),
                    province=province_obj
                )

        self.stdout.write(self.style.SUCCESS("✅ Provinces and Cities loaded successfully"))
