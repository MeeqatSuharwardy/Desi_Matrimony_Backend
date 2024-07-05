"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from backend.authentication.urls import urlpatterns as authentication_urls
from backend.events.urls import urlpatterns as event_urls
from backend.notifications.urls import urlpatterns as notifiction_urls
from backend.payments.urls import urlpatterns as payment_urls
from backend.swagger.urls import urlpatterns as swagger_urls
from backend.users.urls import urlpatterns as user_urls

urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [
    path('admin/', admin.site.urls),
    path('swagger/', include(swagger_urls)),
    path('api/', include(authentication_urls)),
    path('api/', include(user_urls)),
    path('api/', include(event_urls)),
    path('api/', include(payment_urls)),
    path('api/', include(notifiction_urls))
]
