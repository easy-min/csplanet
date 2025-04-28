# csplanet/apps/problems/urls.py

from django.urls import path

# 새로 만든 뷰 함수들을 import
from .views.create_objective import (
    create_objective,
    detail_objective,
    edit_objective,
)
from .views import (
    solve_problems,
    select_problem_type,
    create_subjective,
)

app_name = 'problems'

urlpatterns = [
    # 객관식/주관식 출제 선택
    path('create/',            select_problem_type,   name='select_problem_type'),

    # 문제 풀러가기
    path('solve/',             solve_problems,        name='solve_problems'),

    # — 객관식 문제 생성/상세/수정 —
    path('objective/create/',  create_objective,      name='create_objective'),
    path('objective/<int:pk>/',     detail_objective,      name='detail_objective'),
    path('objective/<int:pk>/edit/', edit_objective,        name='edit_objective'),

    # 주관식 문제 생성
    path('subjective/create/', create_subjective,     name='create_subjective'),
]
