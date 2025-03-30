from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_results, name='search_results'),
    path('composers/<int:composer_id>/', views.composer_detail, name='composer_detail'),
    path('compositions/<int:composition_id>/', views.composition_detail, name='composition_detail'),
]
