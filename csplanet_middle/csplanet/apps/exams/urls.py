# csplanet/apps/exams/urls.py
# csplanet/apps/exams/urls.py
from django.urls import path
from .views import exam as exam_views, test as test_views
from .views import exam_detail

app_name = 'exams'
urlpatterns = [
    path('',                    exam_views.exam_list,      name='exam_list'),
    path('create/',             exam_views.exam_create,    name='exam_create'),
    path('<int:pk>/edit/',      exam_views.exam_edit,      name='exam_edit'),
    path('available/',          test_views.exam_available, name='exam_available'),
    path('<int:exam_pk>/take/', test_views.exam_take,      name='exam_take'),
    path('<int:session_pk>/submit/', test_views.exam_submit, name='exam_submit'),
    path('<int:session_pk>/result/', test_views.exam_result, name='exam_result'),
    path('<int:pk>/questions/', exam_detail, name='exam_detail'),
]