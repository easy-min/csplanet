from django.urls import path
from .views import exam as exam_views
from .views import test as test_views

app_name = 'exams'

# 관리자용 URL (staff 전용)
admin_patterns = [
    path('manmage/',                     exam_views.exam_list,   name='exam_list'),
    path('manmage/create/',              exam_views.exam_create, name='exam_create'),
    path('manmage/<int:pk>/edit/',       exam_views.exam_edit,   name='exam_edit'),
    path('manmage/<int:exam_id>/print/', exam_views.exam_print,  name='exam_print'),
    path('manmage/<int:exam_pk>/sessions/', exam_views.session_list,  name='session_list'),
]

# 사용자용 URL
user_patterns = [
    path('',                           test_views.list_exams,        name='list_exams'),
    path('calendar/',                  test_views.monthly_calendar,  name='monthly_calendar'),
    path('solve/<int:exam_pk>/',       test_views.solve_list,        name='solve_list'),
    path('take/<int:exam_pk>/',        test_views.exam_take,         name='exam_take'),
    path('submit/<int:session_pk>/',   test_views.exam_submit,       name='exam_submit'),
    path('result/<int:session_pk>/',   test_views.exam_result,       name='exam_result'),
]

urlpatterns = admin_patterns + user_patterns
