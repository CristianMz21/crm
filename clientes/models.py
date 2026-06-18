"""Contact management models.

``Cliente`` represents a company or person in the owner's book of
business.  ``Contacto`` is a person at a client.  ``Etiqueta`` is
a reusable tag applied to clients via M2M.
"""

from core.managers import SoftDeleteManager
from core.models import AuditModel, SoftDeleteModel, TimeStampedModel
from django.db import models
from django.urls import reverse


class Cliente(TimeStampedModel, SoftDeleteModel, AuditModel):
    """A company or person in the CRM."""

    nombre = models.CharField(max_length=150, verbose_name="nombre")
    email = models.EmailField(unique=True, verbose_name="email")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="teléfono")
    empresa = models.CharField(max_length=150, blank=True, verbose_name="empresa")
    ciudad = models.CharField(max_length=100, blank=True, db_index=True, verbose_name="ciudad")
    pais = models.CharField(max_length=80, blank=True, default="", verbose_name="país")
    sitio_web = models.URLField(blank=True, verbose_name="sitio web")
    notas = models.TextField(blank=True, verbose_name="notas")

    etiquetas = models.ManyToManyField(
        "Etiqueta",
        related_name="clientes",
        blank=True,
        verbose_name="etiquetas",
    )

    objects = SoftDeleteManager()
    objects_all = models.Manager()

    class Meta:
        verbose_name = "cliente"
        verbose_name_plural = "clientes"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse("cliente_detail", kwargs={"pk": self.pk})


class Contacto(TimeStampedModel, SoftDeleteModel, AuditModel):
    """A person associated with a ``Cliente``."""

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
    notas = models.TextField(blank=True, verbose_name="notas")

    objects = SoftDeleteManager()
    objects_all = models.Manager()

    class Meta:
        verbose_name = "contacto"
        verbose_name_plural = "contactos"
        ordering = ["cliente", "nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.cliente.nombre})"


class Etiqueta(TimeStampedModel):
    """A reusable tag applied to clients via M2M."""

    nombre = models.CharField(max_length=50, unique=True, verbose_name="nombre")
    color = models.CharField(max_length=7, blank=True, default="", verbose_name="color")
    descripcion = models.CharField(max_length=200, blank=True, verbose_name="descripción")

    class Meta:
        verbose_name = "etiqueta"
        verbose_name_plural = "etiquetas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
