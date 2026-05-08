from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('', views.property_list, name='property_list'),
    path('add/', views.property_add, name='property_add'),
    path('<int:property_id>/', views.property_detail, name='property_detail'),
    path('<int:property_id>/edit/', views.property_edit, name='property_edit'),
    path('<int:property_id>/delete/', views.property_delete, name='property_delete'),
]
