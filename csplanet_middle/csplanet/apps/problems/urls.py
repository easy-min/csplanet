# csplanet/apps/problems/urls.py

from django.urls import path
from .views.create_objective  import objective_upsert, detail_objective
from .views.create_subjective import subjective_upsert, detail_subjective
from .views                    import select_problem_type

app_name = 'problems'

urlpatterns = [
    path('create/',                 select_problem_type,   name='select_problem_type'),

    # 객관식
    path('objective/create/',       objective_upsert,      name='create_objective'),
    path('objective/<int:pk>/',     detail_objective,      name='detail_objective'),
    path('objective/<int:pk>/edit/',objective_upsert,      name='edit_objective'),

    # 주관식
    path('subjective/create/',      subjective_upsert,     name='create_subjective'),
    path('subjective/detail/<int:pk>/', detail_subjective,  name='detail_subjective'),
    path('subjective/<int:pk>/edit/',    subjective_upsert,  name='edit_subjective'),
]
