from django.apps import AppConfig


class ExamsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'csplanet.apps.exams'
    def ready(self):
        # signals 패키지의 모든 모듈을 로드
        import csplanet.apps.exams.signals.creation
