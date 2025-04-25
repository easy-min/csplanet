# solve_problems.py
from django.shortcuts import render

def solve_problems(request):
    """문제 풀러가기 메인 페이지"""
    return render(request, "problems/solve_problems.html")
