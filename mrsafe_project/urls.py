from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
import os
# quiz_ai/urls.py (project-level)
from django.contrib import admin
from django.urls import path, include
from mrsafe_app.views.views_files import public_landing  # adjust as needed



urlpatterns = [
    # Redirect root to home view
    path('home', lambda request: redirect('mrsafe_app:home')),

    # Include app routes
    path('mrsafe/', include('mrsafe_app.urls', namespace='mrsafe_app')),  # ✅ namespaced
    
    
    path('', public_landing, name='index'), 
    


    # Admin and rich editor
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),



    # ✅ Serve ads.txt from static folder
    re_path(r'^ads.txt$', serve, {
        'document_root': os.path.join(settings.BASE_DIR, 'static'),
        'path': 'ads.txt'
    }),
]
# Static and media files (development only)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
