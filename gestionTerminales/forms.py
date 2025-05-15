# apps/movimientos/forms.py
from django import forms
from django.utils import timezone
from .models import Terminal, Bus      # importa donde tengas tus apps

class NuevoMovimientoForm(forms.Form):
    origen        = forms.ModelChoiceField(
        queryset=Terminal.objects.all(),
        label='Terminal de origen'
    )
    bus           = forms.ModelChoiceField(
        queryset=Bus.objects.none(),
        label='Bus disponible'
    )
    destino       = forms.ModelChoiceField(
        queryset=Terminal.objects.all(),
        label='Terminal de destino'
    )
    hora_salida   = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        initial=timezone.localtime
    )

    # —————— filtrado dinámico del bus según el terminal origen ——————
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        origen_id = self.data.get('origen') or self.initial.get('origen')
        if origen_id:
            self.fields['bus'].queryset = Bus.objects.filter(
                terminal_actual_id=origen_id, activo=True
            )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('origen') == cleaned.get('destino'):
            self.add_error('destino', 'El destino no puede ser igual al origen.')
        return cleaned
