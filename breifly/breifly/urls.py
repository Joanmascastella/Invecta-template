from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
import breiflyplatform.views as views
import breiflyplatform.error_handlers as error_handler

urlpatterns = [
    path('', views.landing_page, name='home'),
    path('home/', views.landing_page, name='home'),
    path('custom-admin/dashboard/', views.admin_page, name='admin'),
    path('custom-admin/dashboard/users', views.user_management_page, name='user_management_page'),
    path('custom-admin/dashboard/items', views.item_management_page, name='item_management_page'),
    path('download/csv/', views.download_csv, name='download_item'),
    path('upload/csv/', views.upload_csv, name='upload_csv'),
    path('update-item/<uuid:id>/', views.item_management_page, name='update_item'),
    path('create-item/', views.item_management_page, name='create_item'),
    path('delete-items/<uuid:id>/', views.item_management_page, name='delete_item'),
    path('update-user/<uuid:id>/', views.user_management_page, name='update_user'),
    path('delete-user/<uuid:id>/', views.user_management_page, name='delete_user'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout_view'),
    path('error/page/', views.error_page, name="error_page"),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'breiflyplatform.error_handlers.custom_page_not_found_view'
handler500 = 'breiflyplatform.error_handlers.custom_error_view'
handler400 = 'breiflyplatform.error_handlers.custom_bad_request_view'