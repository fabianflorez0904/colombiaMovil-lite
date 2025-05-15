from datetime import timedelta
import requests
import requests, decimal
from decouple import config


def distancia_ruta_completa(pt_a, pt_b):
    url = 'https://api.openrouteservice.org/v2/directions/driving-car/geojson'
    headers = {'Authorization': config(ORS_API_KEY)}
    body = {
        "coordinates": [
            [pt_a.x, pt_a.y],
            [pt_b.x, pt_b.y]
        ]
    }
    try:
        r = requests.post(url, json=body, headers=headers, timeout=10)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("ERROR LLAMANDO A ORS:", e)
        raise Exception("El servicio de rutas no está disponible en este momento. Inténtalo más tarde.")

    ruta = r.json()['features'][0]
    distancia_km = decimal.Decimal(ruta['properties']['summary']['distance']) / 1000
    duracion_h   = decimal.Decimal(ruta['properties']['summary']['duration']) / 3600

    return {
        'distancia_km': distancia_km,
        'duracion_horas': duracion_h,
        'geometry': ruta['geometry']
    }



def formato_horas_hhmmss(horas_decimales):
    total_segundos = int(float(horas_decimales) * 3600)
    td = timedelta(seconds=total_segundos)
    return str(td)
