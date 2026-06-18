from django.db import models
from django.urls import reverse


class Cliente(models.Model):
    nombre = models.CharField(max_length=150, verbose_name="nombre")
    email = models.EmailField(unique=True, verbose_name="email")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="teléfono")
    empresa = models.CharField(max_length=150, blank=True, verbose_name="empresa")
    ciudad = models.CharField(
        max_length=100, blank=True, db_index=True, verbose_name="ciudad"
    )
    activo = models.BooleanField(default=True, verbose_name="activo")
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, verbose_name="fecha de creación"
    )

    class Meta:
        verbose_name = "cliente"
        verbose_name_plural = "clientes"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse("cliente_detail", kwargs={"pk": self.pk})


class Contacto(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="contactos",
        verbose_name="cliente",
    )
    nombre = models.CharField(max_length=150, verbose_name="nombre")
    cargo = models.CharField(max_length=100, blank=True, verbose_name="cargo")
    email = models.EmailField(blank=True, verbose_name="email")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="teléfono")

    class Meta:
        verbose_name = "contacto"
        verbose_name_plural = "contactos"
        ordering = ["cliente", "nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.cliente.nombre})"
