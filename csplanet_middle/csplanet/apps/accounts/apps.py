# csplanet/apps/accounts/apps.py

from django.apps import AppConfig

class AccountsConfig(AppConfig):
    # 이 부분이 잘못돼 있으면 Django가 모듈을 못 찾습니다.
    # 반드시 아래처럼 전체 경로를 소문자로 적어야 합니다.
    name = 'csplanet.apps.accounts'
    verbose_name = 'Accounts'
