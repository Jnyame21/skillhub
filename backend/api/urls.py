from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path 
from api.views import *


urlpatterns = [
    path('', root, name='root'),
    path('server_time', get_current_server_time),
    path('refresh_server', refresh_server),
    path('login', UserAuthView.as_view(), name='token_obtain_pair'),
    path('logout', logout_user),
    path('api/token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('user/data', get_user_data),
    
    # superuser
    path('superuser/data', superuser_data),

    # Student
    path('student/signup', student_signup),
    path('student/data', student_data),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
