import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from rest_framework.exceptions import (
    APIException, 
    PermissionDenied, 
    NotAuthenticated, 
    ValidationError,
    NotFound
)

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    커스텀 예외 핸들러: 모든 API 예외를 로깅하고 일관된 응답 형식 제공
    """
    # REST framework의 기본 예외 핸들러 호출
    response = exception_handler(exc, context)
    
    # 뷰 정보 가져오기
    view = context.get('view', None)
    request = context.get('request', None)
    
    # 로깅 정보 구성
    view_name = view.__class__.__name__ if view else 'Unknown'
    user = getattr(request, 'user', 'Anonymous') if request else 'Unknown'
    method = getattr(request, 'method', 'Unknown') if request else 'Unknown'
    path = getattr(request, 'path', 'Unknown') if request else 'Unknown'
    
    # 예외 타입별 로깅
    exc_name = exc.__class__.__name__
    
    if response is not None:
        # DRF가 처리한 예외
        if response.status_code >= 500:
            logger.error(
                f"Server Error in {view_name}: {exc_name} - {str(exc)} | "
                f"User: {user} | {method} {path}",
                exc_info=True
            )
        elif response.status_code >= 400:
            logger.warning(
                f"Client Error in {view_name}: {exc_name} - {str(exc)} | "
                f"User: {user} | {method} {path}"
            )
        
        # 응답에 상태 코드와 에러 타입 추가
        custom_response_data = {
            'status_code': response.status_code,
            'error_type': exc_name,
            'detail': response.data.get('detail', str(exc)) if hasattr(response.data, 'get') else str(exc)
        }
        
        # ValidationError의 경우 필드별 에러 정보 유지
        if isinstance(exc, ValidationError):
            custom_response_data.update(response.data)
        
        response.data = custom_response_data
    else:
        # DRF가 처리하지 못한 예외 (500 에러)
        logger.error(
            f"Unhandled Exception in {view_name}: {exc_name} - {str(exc)} | "
            f"User: {user} | {method} {path}",
            exc_info=True
        )
        
        response = Response(
            {
                'status_code': 500,
                'error_type': exc_name,
                'detail': 'Internal server error occurred'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return response

def log_api_call(view_name, method_name, user, request_data=None, extra_info=None):
    """
    API 호출 로깅을 위한 헬퍼 함수
    """
    log_msg = f"{view_name}.{method_name} called by user: {user}"
    if request_data:
        log_msg += f" | Request data: {request_data}"
    if extra_info:
        log_msg += f" | Extra: {extra_info}"
    
    logger.info(log_msg)

def log_api_success(view_name, method_name, user, response_info=None):
    """
    API 성공 응답 로깅을 위한 헬퍼 함수
    """
    log_msg = f"{view_name}.{method_name} completed successfully for user: {user}"
    if response_info:
        log_msg += f" | Response: {response_info}"
    
    logger.info(log_msg)
