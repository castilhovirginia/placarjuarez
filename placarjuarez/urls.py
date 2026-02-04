"""
URL configuration for placarjuarez project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from placar.views import home, creditos, ranking_geral
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', home, name='home'),
                  path('creditos', creditos, name='creditos'),
                  path('ranking/<int:campeonato_id>/', ranking_geral, name='ranking_geral'),
              ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
