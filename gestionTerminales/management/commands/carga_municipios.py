from django.core.management.base import BaseCommand
from gestionTerminales.models import Municipio
import csv
from pathlib import Path

class Command(BaseCommand):
    help = "Carga municipios desde un archivo CSV"

    def handle(self, *args, **kwargs):
        ruta = Path(__file__).resolve().parent.parent.parent / "fixtures/municipios.csv"
        if not ruta.exists():
            self.stderr.write(self.style.ERROR("El archivo municipios.csv no existe"))
            return

        with ruta.open(newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            total = 0
            for row in reader:
                print(row)
                Municipio.objects.update_or_create(
                    cod_departamento=row["Código Departamento"],
                    cod_municipio=row["Código Municipio"],
                    defaults={
                        "nombre_departamento": row["Nombre Departamento"],
                        "nombre_municipio": row["Nombre Municipio"],
                    }
                )
                total += 1
        self.stdout.write(self.style.SUCCESS(f"{total} municipios procesados correctamente"))
