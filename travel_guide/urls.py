"""
URL configuration for travel_guide project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
#from guide.views import home
from guide import views
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name= 'home'),
    path('district/', views.district_page, name='district_page'),
    path('districts/<int:id>/', views.district_detail, name='district_detail'),
    path('place/<int:id>/', views.place_detail, name='place_detail'),
    path('feedback/<int:place_id>/', views.feedback_view, name='feedback'),
    path('feedbacks/', views.all_feedback_view, name='all_feedbacks'),
    path('search/', views.search_view, name='search'),
    path('auth/', views.handle_auth, name='handle_auth'),
    path('logout/', views.handle_logout, name='handle_logout'),
    path('check_login_status/', views.check_login_status, name='check_login_status'),
    path('place/<int:place_id>/review/', views.submit_review, name='submit_review'),
    path('place/<int:place_id>/review/load_more/', views.load_more_reviews, name='load_more_reviews'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)