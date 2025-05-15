from django.contrib import admin
from .models import Municipio, Terminal, Bus, Movimiento
from leaflet.admin import LeafletGeoAdmin

@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display   = ('nombre_municipio', 'cod_municipio', 'nombre_departamento')
    search_fields  = ('nombre_municipio',)

@admin.register(Terminal)
class TerminalAdmin(LeafletGeoAdmin):
    list_display   = ('__str__', 'capacidad')
    list_filter    = ('municipio',)

@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display   = ('placa','terminal_actual', 'activo')
    list_filter    = ('activo',)

@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display   = ('bus', 'origen', 'destino', 'distancia_km', 'hora_salida', 'hora_llegada')
    list_filter    = ('origen', 'destino')
