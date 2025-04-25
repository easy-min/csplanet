# create_problem.py
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def select_problem_type(request):
    """객관식/주관식 문제 출제 선택 페이지"""
    return render(request, "problems/create_problem.html")