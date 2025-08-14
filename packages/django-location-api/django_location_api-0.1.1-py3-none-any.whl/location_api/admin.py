from django.contrib import admin

from location_api.models import Location, Supplier, SupplierAlias


class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "supplier", "modified")
    list_filter = ("supplier",)
    search_fields = ["name"]
    date_hierarchy = "modified"


class SupplierAliasInline(admin.TabularInline):
    model = SupplierAlias


class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ["name"]
    inlines = [SupplierAliasInline]


class SupplierAliasAdmin(admin.ModelAdmin):
    list_display = ("regex", "supplier")
    list_filter = ("supplier",)


admin.site.register(Location, LocationAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(SupplierAlias, SupplierAliasAdmin)
