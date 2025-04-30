from .exam import (
    exam_list, exam_create, exam_edit, exam_print, session_list
)
from .test import (
    list_exams as test_list_exams,
    solve_list, exam_take, exam_submit, exam_result, monthly_calendar
)

__all__ = [
    'exam_list', 'exam_create', 'exam_edit', 'exam_print', 'session_list',
    'test_list_exams', 'solve_list', 'exam_take', 'exam_submit', 'exam_result', 'monthly_calendar',
]
