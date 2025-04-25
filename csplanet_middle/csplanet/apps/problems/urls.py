# csplanet/apps/problems/urls.py
from django.urls import path
from .views import (
    solve_problems,
    select_problem_type,
    create_objective,
    create_subjective,
)

app_name = 'problems'

urlpatterns = [
    # 문제 목록
    #path('',                   list_problems,         name='list'),
    # 객관식/주관식 출제 선택
    path('create/',            select_problem_type,   name='select_problem_type'),
    # 문제 풀러가기 (앱 네임스페이스 안에서도 제공 가능)
    path('solve/',             solve_problems,       name='solve_problems'),
    # 객관식 문제 생성
    path('objective/create/',  create_objective,      name='create_objective'),
    # 주관식 문제 생성
    path('subjective/create/', create_subjective,     name='create_subjective'),
]
