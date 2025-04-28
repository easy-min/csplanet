# csplanet/apps/exams/views/__init__.py
from .exam import exam_list, exam_create, exam_edit, exam_detail
from .test import exam_available, exam_take, exam_submit, exam_result

__all__ = [
    'exam_list', 'exam_create', 'exam_edit',
    'exam_available', 'exam_take', 'exam_submit', 'exam_result', exam_detail
]