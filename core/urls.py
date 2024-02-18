"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from api.views import index, realtime_page, realtime_page_jquery, keywords_page, targeted_area_page, historic_page
from django.views.generic import TemplateView

urlpatterns = [
    path('', index, name='index'),
    path('realtime-jquery/', realtime_page_jquery, name='realtime_page_jquery'),
    path('realtime/', realtime_page, name='realtime_page'),
    path('keywords/', keywords_page, name='keywords_page'),
    path('target-area/', targeted_area_page, name='target_area'),
    path('historic/', historic_page, name='historic_page'),

    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('scrapper/', include('scrapper.urls')),
    # re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    # re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),

]

urlpatterns += [
    re_path(r'^.*', TemplateView.as_view(template_name='django-website/index.html'))
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
