
from django.contrib import admin
from django.urls import path, include
from . import views 
from django.conf.urls.static import static
from django.conf import settings 

urlpatterns = [
	path('jet/',include('jet.urls')),
    path('admin/', admin.site.urls),
    path('',views.index,name="index"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('faculty/', include('faculty.urls')),
    path('hod/', include('hod.urls')),
    path('assistant/',include('labassistant.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
