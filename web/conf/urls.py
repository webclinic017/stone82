"""conf URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path, re_path

# views
from index import views as index_views
from hello import views as hello_views
from balance import views as balance_views


urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^(?P<name>[A-Z][a-z]*)$', hello_views.sayHello),
    path('index/', index_views.main_view),
    path('balance/', balance_views.main_view)
]
