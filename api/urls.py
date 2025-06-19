from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('form', views.form_view, name='form'),
    path('get_options/', views.get_options, name='get_options'),
    path('predict/', views.predict, name='predict'),
    path('register', views.register, name='register'),
    path('login', views.loginPage, name='login'),
    path('logoutUser', views.logoutUser, name='logoutUser'),
    path('car', views.car, name='car'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('admin_dashboard', views.admin_dashboard, name='admin_dashboard'),
    
    # Cars
    path('cars', views.cars_view, name='cars_view'),
    path('create_cars', views.create_cars, name='create_cars'),
    path('edit_cars/<str:pk>', views.edit_cars, name='edit_cars'),
    path('delete_cars/<str:pk>', views.delete_cars, name='delete_cars'),
    path('wishlist/toggle/<int:pk>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlists', views.wishlists, name='wishlists'),
    path('validate_payment/<str:pk>', views.validate_payment, name='validate_payment'),
    
    path('car_detail/<str:pk>', views.car_detail, name='car_detail'),
    path('reserve/<str:pk>', views.create_reservations, name='create_reservations'),
    path('cancel/<str:pk>', views.cancel_reservations, name='cancel_reservations'),
    path('validate/<str:pk>', views.validate_reservations, name='validate_reservations'),
    
    # Brands
    path('brands', views.brands_view, name='brands_view'),
    path('create_brands', views.create_brands, name='create_brands'),
    path('edit_brands/<str:pk>', views.edit_brands, name='edit_brands'),
    path('delete_brands/<str:pk>', views.delete_brands, name='delete_brands'),
    
    #Colors
    path('colors', views.colors_view, name='colors_view'),
    path('create_colors', views.create_colors, name='create_colors'),
    path('edit_colors/<str:pk>', views.edit_colors, name='edit_colors'),
    path('delete_colors/<str:pk>', views.delete_colors, name='delete_colors'),
    
    # Interior Colors
    path('interior_colors', views.interior_colors_view, name='interior_colors_view'),
    path('create_interior_colors', views.create_interior_colors, name='create_interior_colors'),
    path('edit_interior_colors/<str:pk>', views.edit_interior_colors, name='edit_interior_colors'),
    path('delete_interior_colors/<str:pk>', views.delete_interior_colors, name='delete_interior_colors'),
    
    # Interior Colors
    path('body', views.body_view, name='body_view'),
    path('create_body', views.create_body, name='create_body'),
    path('edit_body/<str:pk>', views.edit_body, name='edit_body'),
    path('delete_body/<str:pk>', views.delete_body, name='delete_body'),
    
    # Requests
    path('requests', views.requests_view, name='requests_view'),
]
