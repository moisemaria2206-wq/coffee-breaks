from django.contrib import admin
from .models import Categorie, Brand, Furnizor, Eveniment, Produs, Varianta


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ("nume", "culoare", "sigla", "ordine_afisare")
    search_fields = ("nume",)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("nume", "tara_origine", "an_infiintare", "site_web")
    list_filter = ("tara_origine",)
    search_fields = ("nume",)


@admin.register(Furnizor)
class FurnizorAdmin(admin.ModelAdmin):
    list_display = ("nume", "email", "telefon", "oras")
    list_filter = ("oras",)
    search_fields = ("nume", "email")


@admin.register(Eveniment)
class EvenimentAdmin(admin.ModelAdmin):
    list_display = ("nume", "data_inceput", "data_sfarsit", "locatie", "discount_procent")
    list_filter = ("data_inceput",)
    search_fields = ("nume",)


class VariantaInline(admin.TabularInline):
    model = Varianta
    extra = 1


@admin.register(Produs)
class ProdusAdmin(admin.ModelAdmin):
    list_display = ("nume", "tip_produs", "categorie", "brand", "pret_100g", "disponibil")
    list_filter = ("tip_produs", "categorie", "disponibil")
    search_fields = ("nume",)
    inlines = [VariantaInline]


@admin.register(Varianta)
class VariantaAdmin(admin.ModelAdmin):
    list_display = ("produs", "gramaj_g", "tip_ambalaj", "stoc")
    list_filter = ("tip_ambalaj",)