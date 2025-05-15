from django.contrib.gis.db import models as gis_models
from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

class Municipio(models.Model):
    cod_departamento = models.CharField(max_length=10)
    nombre_departamento = models.CharField(max_length=100)
    cod_municipio = models.CharField(max_length=10)
    nombre_municipio = models.CharField(max_length=100)

    class Meta:
        unique_together = ('cod_departamento', 'cod_municipio')  # 👈 esto es clave

    def __str__(self):
        return f"{self.nombre_municipio} ({self.nombre_departamento})"

class Terminal(gis_models.Model):
    # nombre        = models.CharField(max_length=50, unique=False)
    municipio     = models.ForeignKey(Municipio, on_delete=models.PROTECT)
    ubicacion     = gis_models.PointField(srid=4326)
    capacidad     = models.PositiveSmallIntegerField()

    # atajo para la ocupación en vivo
    def ocupacion_actual(self):
        return self.buses_presentes.count()

    def cupos_disponibles(self):
        return self.capacidad - self.ocupacion_actual()

    def tiene_cupo(self):
        return self.ocupacion_actual() < self.capacidad

    def __str__(self):
        return f"Terminal - {self.municipio} Cupos libres - ({self.cupos_disponibles()})"
    
class Bus(models.Model):
    placa               = models.CharField(max_length=8, unique=True)
    activo              = models.BooleanField(default=True)
    # FK “suave” – null cuando el bus está en carretera
    terminal_actual     = models.ForeignKey(
        Terminal,
        null=True, blank=True,
        related_name='buses_presentes',
        on_delete=models.PROTECT
    )

    def mover_a(self, nuevo_terminal):
        """Utilidad para actualizar la ubicación dentro de una transacción"""
        if nuevo_terminal and not nuevo_terminal.tiene_cupo():
            raise ValidationError(f'El terminal {nuevo_terminal} está lleno.')
        self.terminal_actual = nuevo_terminal
        self.save(update_fields=['terminal_actual'])
    
    def __str__(self):
        return f"Bus - Placa {self.placa}"

class Movimiento(models.Model):
    bus          = models.ForeignKey(Bus, on_delete=models.PROTECT)
    origen       = models.ForeignKey(Terminal, related_name='salidas', on_delete=models.PROTECT)
    destino      = models.ForeignKey(Terminal, related_name='llegadas', on_delete=models.PROTECT)
    hora_salida  = models.DateTimeField()
    hora_llegada = models.DateTimeField()
    distancia_km = models.DecimalField(max_digits=6, decimal_places=2)
    ruta_geojson = models.JSONField(null=True, blank=True)

    @property
    def duracion_estimada(self):
        if self.hora_llegada and self.hora_salida:
            delta = self.hora_llegada - self.hora_salida
            horas, resto = divmod(delta.total_seconds(), 3600)
            minutos, segundos = divmod(resto, 60)
            return f"{int(horas):02d}:{int(minutos):02d}:{int(segundos):02d}"
        return "No disponible"

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(origen=models.F('destino')),
                name='origen_distinto_de_destino'
            )
        ]

