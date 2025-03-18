from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
import breiflyplatform.views as views
from django.conf.urls.i18n import set_language
import breiflyplatform.error_handlers as error_handler # this is correct
# Base URL patterns
urlpatterns = [
    path('i18n/setlang/', set_language, name='set_language'),  # Language switching
]


# Language-aware patterns
urlpatterns += i18n_patterns(
    path('', views.landing_page, name='home'),
    path('home/', views.landing_page, name='home'),
    path('custom-admin/dashboard/', views.admin_page, name='admin'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout_view'),
    path('error/page/', views.error_page, name="error_page"),
    
    prefix_default_language=True,
)

# Static file serving
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ...
handler404 = 'breiflyplatform.error_handlers.custom_page_not_found_view'
handler500 = 'breiflyplatform.error_handlers.custom_error_view'
handler400 = 'breiflyplatform.error_handlers.custom_bad_request_view'