import re

from django.contrib.gis.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(archived=False)


class SupplierManager(models.Manager):
    def identify(self, string):
        for supplier in Supplier.objects.all():
            if re.match(supplier.name, string, flags=re.I):
                return supplier
            if re.search(supplier.name, string, flags=re.I):
                return supplier
            for alias in supplier.supplieralias_set.all():
                if re.search(alias.regex, string, flags=re.I):
                    return supplier


class Supplier(models.Model):
    objects = SupplierManager()
    name = models.CharField(max_length=255, blank=False, null=False, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)


class SupplierAlias(models.Model):
    regex = models.CharField(max_length=255, blank=False, null=False)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

    def __str__(self):
        return self.regex

    class Meta:
        verbose_name_plural = "Supplier alias's"
        ordering = ("supplier",)


class Location(models.Model):
    supplier = models.ForeignKey(
        Supplier, null=True, related_name="locations", on_delete=models.CASCADE
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField(editable=False)

    point = models.PointField()
    country_code = models.CharField(max_length=3, blank=True)
    gisprecision = models.CharField(max_length=255, blank=True)

    attributes = models.JSONField(blank=True, null=True, default=dict)
    archived = models.BooleanField(default=False)

    objects = ActiveManager()
    objects_with_archived = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)

    def get_absolute_url(self):
        return reverse("location-detail", kwargs={"pk": self.id})

    def save(self, *args, **kwargs):
        slug_parts = []
        if self.name:
            slug_parts.append(self.name)

        if self.supplier:
            if self.supplier.name not in slug_parts:
                slug_parts.append(self.supplier.name)
        self.slug = slugify(" ".join(slug_parts)[:50])
        super().save(*args, **kwargs)

    def archive(self):
        """Archive this location"""
        self.archived = True
        self.save(update_fields=["archived"])
