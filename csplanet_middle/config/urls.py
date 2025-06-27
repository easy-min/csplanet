from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    # path(
    #     "about/",
    #     TemplateView.as_view(template_name="pages/about.html"),
    #     name="about",
    # ),
    # # Django Admin, use {% url 'admin:index' %}
    # path(settings.ADMIN_URL, admin.site.urls),
    # # User management
    # path("users/", include("csplanet.users.urls", namespace="users")),
    # path("accounts/", include("allauth.urls")),

    # # 문제 생성 관리
    # path("problems/", include("csplanet.apps.problems.urls", namespace="problems")),

    # # 시험 응시시 관리
    # path("exams/", include("csplanet.apps.exams.urls", namespace="exams")),

    # *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]

# API URLS
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from csplanet.apps.exams.urls import admin_urls  # 반드시 import
api_urlpatterns = [
    path("api/problems/", include("csplanet.apps.problems.urls", namespace='problems')),
    path("api/users/", include("csplanet.users.urls", namespace='users')),
    path("api/admin/", include("csplanet.apps.exams.urls.admin_urls", namespace='admin-exams')),
    # path("api/admin/", include((admin_urls.urlpatterns, admin_urls.app_name), namespace='admin-exams')),
    path('api/exams/', include('csplanet.apps.exams.urls.user_urls', namespace='user-exams')),
    path('admin/', admin.site.urls),
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="api-schema"), name="api-docs"),
]

urlpatterns += api_urlpatterns

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
            *urlpatterns,
        ]
