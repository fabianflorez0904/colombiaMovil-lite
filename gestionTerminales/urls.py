from django.urls import path
from gestionTerminales import views

app_name = 'movimientos'

urlpatterns = [
    path('dashboard/',      views.terminales_dashboard,     name='terminales_dashboard'),
    path('dashboard/<int:pk>/',      views.terminal_dashboard,     name='terminal_dashboard'),
    path('crearRuta/<int:origen>/<int:bus>',      views.crear_ruta,     name='crear_ruta'),
    path('validar/', views.validar_cupo_distancia, name='validar_ajax'),
    path('guardar/', views.guardar_movimiento, name='guardar_movimiento'),
    path('api/terminal/<int:pk>/coords/', views.coordenadas_terminal, name='terminal_coord'),
    path('buses/', views.dashboard_buses, name='dashboard_buses'),
    path('buses/<int:pk>/', views.detalle_bus, name='detalle_bus'),
    path('movimientos/<int:pk>/', views.detalle_movimiento, name='detalle_movimiento'),


]
