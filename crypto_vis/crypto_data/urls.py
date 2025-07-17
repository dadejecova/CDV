from django.urls import path
from crypto_data.views import portfolio
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page URL
    path('portfolio/', portfolio, name='portfolio'),
    path('portfolio/delete/<int:pk>/', views.delete_holding, name='delete_holding'),
   # path('about/', views.about, name='about'),  # About page URL
]