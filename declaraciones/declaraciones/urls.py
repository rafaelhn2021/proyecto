"""declaraciones URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, re_path
from django.conf.urls import include, url
from declaracion import urls
from sitio import urls
from api import urls
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', include('sitio.urls')),
    path('admin/', admin.site.urls),
    path('declaracion/', include('declaracion.urls')),
    path('api/', include('api.urls')),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('reset_password/', auth_views.PasswordResetView.as_view(), name ='reset_password'),  
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name ='password_reset_done'),  
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(), name ='password_reset_confirm'),  
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name ='password_reset_complete')
]

# front-edit
#urlpatterns += [
#    url(r'^front-edit/', include('front.urls')),
#]

admin.site.site_header = 'Administración de Declaraciones'
admin.site.site_title = 'Administración de Declaraciones'
admin.site.index_title =  'Bienvenido a la administración del sistema'
