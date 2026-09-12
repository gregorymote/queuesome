from background_task.models import CompletedTask, Task
from django.db import models
from django.test import SimpleTestCase


class BackgroundTaskSchemaTests(SimpleTestCase):
    def test_dependency_primary_keys_match_its_published_migrations(self):
        self.assertIsInstance(Task._meta.pk, models.AutoField)
        self.assertNotIsInstance(Task._meta.pk, models.BigAutoField)
        self.assertIsInstance(CompletedTask._meta.pk, models.AutoField)
        self.assertNotIsInstance(CompletedTask._meta.pk, models.BigAutoField)
