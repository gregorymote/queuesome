from background_task.apps import BackgroundTasksAppConfig


class QueuesomeBackgroundTasksConfig(BackgroundTasksAppConfig):
    """Keep the dependency's models aligned with its shipped migrations."""

    default_auto_field = 'django.db.models.AutoField'
