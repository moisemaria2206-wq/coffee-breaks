import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html

from .models import Brand, Categorie, Eveniment, Furnizor, Produs, Varianta

admin.site.site_title = "Coffee Breaks - administrare"            
admin.site.site_header = "Coffee Breaks Online - Administrare"    
admin.site.index_title = "Panou de administrare a magazinului"    
admin.site.site_url = "/"                                         

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ("nume", "culoare_afisata", "sigla", "ordine_afisare")
    search_fields = ("nume", "descriere")
    search_help_text = "Poți căuta după numele categoriei sau după descriere."

    @admin.display(description="Culoare")
    def culoare_afisata(self, obj):
        return format_html(
            '<span style="display:inline-block;width:14px;height:14px;'
            'border-radius:3px;vertical-align:middle;margin-right:6px;'
            'background:{};"></span>{}',
            obj.culoare,
            obj.culoare,
        )


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("nume", "tara_origine", "an_infiintare", "site_web")
    search_fields = ("nume", "tara_origine")
    search_help_text = "Poți căuta după numele brandului sau după țara de origine."


@admin.register(Furnizor)
class FurnizorAdmin(admin.ModelAdmin):
    list_display = ("nume", "email", "telefon", "oras")
    search_fields = ("nume", "email")
    search_help_text = "Poți căuta după numele furnizorului sau după email."


@admin.register(Eveniment)
class EvenimentAdmin(admin.ModelAdmin):
    list_display = ("nume", "data_inceput", "data_sfarsit", "locatie", "discount_procent")
    list_filter = ("data_inceput",)
    search_fields = ("nume", "locatie")
    search_help_text = "Poți căuta după numele evenimentului sau după locație."


class VariantaInline(admin.TabularInline):
    model = Varianta
    extra = 1


@admin.register(Produs)
class ProdusAdmin(admin.ModelAdmin):
    # ordinea coloanelor diferă de cea din model; tara_brand vine din relația cu Brand
    list_display = (
        "nume",
        "categorie",
        "pret_formatat",
        "tip_produs",
        "brand",
        "tara_brand",
        "disponibil",
    )
    list_select_related = ("categorie", "brand")
    list_filter = ("tip_produs", "categorie", "disponibil", "brand")
    search_fields = ("nume", "descriere")
    search_help_text = "Poți căuta după numele produsului sau după descriere."
    ordering = ("-pret_100g",)  # cele mai scumpe produse primele
    list_per_page = 5
    inlines = [VariantaInline]
    actions = ["marcheaza_disponibil", "marcheaza_indisponibil", "exporta_csv"]

    fieldsets = (
        ("Informații de bază", {
            "fields": ("nume", "categorie", "tip_produs", "pret_100g", "stoc", "disponibil", "data_adaugare"),
        }),
        ("Detalii suplimentare (opționale)", {
            "classes": ("collapse",),
            "fields": ("descriere", "imagine", "arome", "taguri", "brand", "furnizori", "evenimente"),
        }),
    )

    @admin.display(description="Preț / 100 g", ordering="pret_100g")
    def pret_formatat(self, obj):
        culoare = "#b03a2e" if obj.pret_100g >= 40 else "#1e8449"
        return format_html(
            '<b style="color:{};font-style:italic;">{} lei</b>',
            culoare,
            f"{obj.pret_100g:.2f}",
        )

    @admin.display(description="Țara brandului", ordering="brand__tara_origine")
    def tara_brand(self, obj):
        return obj.brand.tara_origine if obj.brand else "-"

    @admin.action(description="Marchează produsele selectate ca disponibile")
    def marcheaza_disponibil(self, request, queryset):
        nr = queryset.update(disponibil=True)
        self.message_user(request, f"{nr} produse marcate ca disponibile.")

    @admin.action(description="Marchează produsele selectate ca indisponibile")
    def marcheaza_indisponibil(self, request, queryset):
        nr = queryset.update(disponibil=False)
        self.message_user(request, f"{nr} produse marcate ca indisponibile.")

    @admin.action(description="Exportă produsele selectate în CSV")
    def exporta_csv(self, request, queryset):
        raspuns = HttpResponse(content_type="text/csv; charset=utf-8")
        raspuns["Content-Disposition"] = 'attachment; filename="produse.csv"'
        raspuns.write("\ufeff")  # ca Excel să citească corect diacriticele
        scriitor = csv.writer(raspuns)
        scriitor.writerow(["nume", "tip", "categorie", "pret_100g", "disponibil"])
        for p in queryset.select_related("categorie"):
            scriitor.writerow(
                [p.nume, p.get_tip_produs_display(), p.categorie.nume, p.pret_100g, p.disponibil]
            )
        return raspuns


@admin.register(Varianta)
class VariantaAdmin(admin.ModelAdmin):
    list_display = ("produs", "gramaj_g", "tip_ambalaj", "stoc")
    list_filter = ("tip_ambalaj",)
    search_fields = ("produs__nume", "tip_ambalaj")
    search_help_text = "Poți căuta după numele produsului sau după tipul ambalajului."