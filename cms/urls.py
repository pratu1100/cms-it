
from django.contrib import admin
from django.urls import path, include
from . import views 
from django.conf.urls.static import static
from django.conf import settings 
# from django.contrib.auth.views import login
# from django.contrib import admin

admin.site.site_header = 'CMS administration'                    # default: "Django Administration"
# admin.site.index_title = 'Features area'                 # default: "Site administration"
admin.site.site_title = 'CMS' # default: "Django site admin"

urlpatterns = [
	path('jet/',include('jet.urls')),
	path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    path('admin/', admin.site.urls),
    path('',views.index,name="index"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('faculty/', include('faculty.urls')),
    path('hod/', include('hod.urls')),
    path('assistant/',include('labassistant.urls')),
    path('guest/',include('guest.urls')),
    path('password/change',views.password_change,name="password_change")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
