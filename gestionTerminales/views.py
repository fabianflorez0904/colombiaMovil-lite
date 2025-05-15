# apps/movimientos/views.py
import json
from django.shortcuts import render, redirect,get_object_or_404
from django.db.models import Count
from django import forms
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Bus, Terminal
from .utils.rutas import distancia_ruta_completa,formato_horas_hhmmss
from django.views.decorators.csrf import csrf_protect



from .models import Movimiento,Bus, Terminal
from .forms import NuevoMovimientoForm


def terminales_dashboard(request):
    # anotamos ocupación en la misma consulta
    terminales = Terminal.objects.select_related('municipio') \
                                 .annotate(ocupacion=Count('buses_presentes')).order_by('id')
                                

    # convertimos a lista de dicts para inyectar en el mapa
    geo = [
        {
            'id'       : t.id,
            'nombre'   : str(t),
            'municipio': t.municipio.nombre_municipio,
            'lat'      : t.ubicacion.y,
            'lng'      : t.ubicacion.x,
            'capacidad': t.capacidad,
            'ocupacion': t.ocupacion,
            # 'cupos_disponibles': t.capacidad - t.ocupacion,
        }
        for t in terminales
    ]
    return render(
        request,
        'terminales/dashboard.html',      # <- plantilla en canvas
        {
            'terminales'         : terminales,
            'terminales_geojson' : json.dumps(geo)
        }
    )

def terminal_dashboard(request, pk):
    terminal = get_object_or_404(Terminal, pk=pk)
    buses = Bus.objects.filter(terminal_actual=terminal)
    viajes_origen = Movimiento.objects.filter(origen=terminal).count()
    viajes_destino = Movimiento.objects.filter(destino=terminal).count()
    movimientos_salientes = Movimiento.objects.filter(origen=terminal).order_by('-hora_salida')

    context = {
        'terminal': terminal,
        'buses': buses,
        'viajes_origen': viajes_origen,
        'viajes_destino': viajes_destino,
        'movimientos_salientes': movimientos_salientes
    }
    return render(request, 'terminales/terminal_dashboard.html', context)



class CrearRutaForm(forms.Form):
    destino      = forms.ModelChoiceField(queryset=Terminal.objects.none())
    hora_salida  = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    def __init__(self, origen, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # excluimos el origen del queryset
        self.fields['destino'].queryset = Terminal.objects.exclude(pk=origen.pk)

def crear_ruta(request,origen, bus):
    # origen_id = request.GET.get('origen')
    # bus_id    = request.GET.get('bus')
    origen = Terminal.objects.get(pk=origen)
    bus    = Bus.objects.get(pk=bus)

    if request.method == 'POST':         # no confirmamos aquí, solo validamos
        form = CrearRutaForm(origen, request.POST)
    else:
        form = CrearRutaForm(origen)

    return render(
        request,
        'movimientos/crear_ruta.html',
        {'origen': origen, 'bus': bus, 'form': form}
    )

# Endpoint AJAX/HTMX
@require_POST
def validar_cupo_distancia(request):
    destino_id   = request.POST['destino']
    origen_id    = request.POST['origen']
    hora_salida  = timezone.datetime.fromisoformat(request.POST['hora_salida'])

    origen   = Terminal.objects.get(pk=origen_id)
    destino  = Terminal.objects.get(pk=destino_id)

    if not destino.tiene_cupo():
        return JsonResponse({'ok': False, 'error': 'El terminal destino está lleno.'})

    # Nueva función devuelve: distancia, duración, hora, y geometría
    datos = distancia_ruta_completa(origen.ubicacion, destino.ubicacion)


    hora_llegada = hora_salida + timezone.timedelta(hours=float(datos['duracion_horas']))

    return JsonResponse({
        'ok': True,
        'distancia_km': round(datos['distancia_km'], 2),
        'duracion_horas':formato_horas_hhmmss(datos['duracion_horas']),
        'hora_llegada': hora_llegada.strftime('%d/%m/%Y %H:%M'),
        'geometry': datos['geometry']  # GeoJSON para Leaflet
    })

def coordenadas_terminal(request, pk):
    terminal = get_object_or_404(Terminal, pk=pk)
    return JsonResponse({
        'lat': terminal.ubicacion.y,
        'lng': terminal.ubicacion.x
    })



@csrf_protect
def guardar_movimiento(request):
    if request.method == 'POST':
        origen_id     = request.POST['origen']
        destino_id    = request.POST['destino']
        bus_id        = request.POST['bus']
        hora_salida   = timezone.datetime.fromisoformat(request.POST['hora_salida'])
        hora_llegada  = timezone.datetime.strptime(request.POST['hora_llegada'], '%d/%m/%Y %H:%M')
        distancia_km  = request.POST['distancia_km']
        geometry      = json.loads(request.POST['geometry'])  # ✅ usar la geometría del frontend

        bus     = Bus.objects.get(pk=bus_id)
        origen  = Terminal.objects.get(pk=origen_id)
        destino = Terminal.objects.get(pk=destino_id)

        movimiento = Movimiento.objects.create(
            bus=bus,
            origen=origen,
            destino=destino,
            hora_salida=hora_salida,
            hora_llegada=hora_llegada,
            distancia_km=distancia_km,
            ruta_geojson=geometry  # ✅ ya no llamamos al API aquí
        )

        bus.mover_a(destino)

        return render(request, 'movimientos/detalle_movimiento_creado.html', {
            'movimiento': movimiento
        })

    return redirect('movimientos:terminales_dashboard')

def dashboard_buses(request):
    # Anotamos la cantidad de movimientos por cada bus
    buses = Bus.objects.annotate(num_viajes=Count('movimiento')) \
                       .select_related('terminal_actual') \
                       .order_by('-num_viajes', 'placa')

    return render(request, 'buses/dashboard.html', {'buses': buses})

def detalle_bus(request, pk):
    bus = get_object_or_404(Bus, pk=pk)
    movimientos = Movimiento.objects.filter(bus=bus).order_by('-hora_salida')
    
    return render(request, 'buses/detalle_bus.html', {
        'bus': bus,
        'movimientos': movimientos
    })

from django.shortcuts import get_object_or_404

def detalle_movimiento(request, pk):
    movimiento = get_object_or_404(Movimiento, pk=pk)
    return render(request, 'movimientos/detalle_movimiento.html', {
        'movimiento': movimiento
    })
