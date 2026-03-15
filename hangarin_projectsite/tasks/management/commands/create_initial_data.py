from django.core.management.base import BaseCommand
from tasks.models import Priority, Category, Task, SubTask, Note
from faker import Faker
import random
from django.utils import timezone

class Command(BaseCommand):
    help = 'Create initial data for Hangarin'

    def handle(self, *args, **kwargs):
        fake = Faker()

        categories = ['Work', 'School', 'Personal', 'Finance', 'Projects']
        priorities = ['High', 'Medium', 'Low', 'Critical', 'Optional']
        
        for cat in categories:
            Category.objects.get_or_create(name=cat)
        for prio in priorities:
            Priority.objects.get_or_create(name=prio)

        self.stdout.write("Categories and Priorities created.")

        statuses = ["Pending", "In Progress", "Completed"]
        
        for _ in range(20):
            Task.objects.create(
                title=fake.sentence(nb_words=5),
                description=fake.paragraph(nb_sentences=3),
                deadline=timezone.make_aware(fake.date_time_this_month()),
                status=fake.random_element(elements=statuses),
                category=Category.objects.order_by('?').first(),
                priority=Priority.objects.order_by('?').first()
            )
        
        self.stdout.write(self.style.SUCCESS('Fake tasks generated successfully!'))