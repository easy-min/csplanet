# csplanet/apps/exams/urls.py
from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    #path('', views.exam_list, name='list'),
    #path('<int:pk>/', views.exam_detail, name='detail'),
    # 추가로 create, update 등 엔드포인트를 정의…
]
