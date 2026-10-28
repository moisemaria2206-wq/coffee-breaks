from django.db import models
from django.db.models import F, Q
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

class Categorie(models.Model):
    nume = models.CharField(
        max_length=50,
        unique=True,
        error_messages={
            "unique": "Există deja o categorie cu acest nume.",
            "max_length": "Numele categoriei poate avea cel mult 50 de caractere.",
        },
    )
    descriere = models.TextField(null=True, blank=True)
    culoare = models.CharField(
        max_length=7,
        default="#6f4e37",
        help_text="Culoare în format hex (ex: #6f4e37), folosită la stilizarea categoriei.",
    )
    sigla = models.CharField(
        max_length=100,
        help_text="Calea unei imagini sau numele unui icon FontAwesome.",
    )
    ordine_afisare = models.PositiveIntegerField(
        default=0,
        help_text="Categoriile cu număr mai mic apar primele în site.",
    )

    class Meta:
        verbose_name_plural = "Categorii"
        ordering = ["ordine_afisare", "nume"]
        indexes = [models.Index(fields=["nume"])]
        constraints = [
            models.CheckConstraint(
                condition=Q(culoare__startswith="#"),
                name="categorie_culoare_hex",
            ),
        ]

    def __str__(self):
        return self.nume


class Brand(models.Model):
    nume = models.CharField(
        max_length=60,
        unique=True,
        error_messages={"unique": "Acest brand există deja."},
    )
    tara_origine = models.CharField(max_length=60, null=True, blank=True)
    an_infiintare = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Anul în care a fost înființat brandul (între 1700 și 2100).",
    )
    site_web = models.URLField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Branduri"
        ordering = ["nume"]
        indexes = [models.Index(fields=["tara_origine"])]
        constraints = [
            models.CheckConstraint(
                condition=Q(an_infiintare__isnull=True)
                | Q(an_infiintare__gte=1700, an_infiintare__lte=2100),
                name="brand_an_valid",
            ),
        ]

    def __str__(self):
        return self.nume
    
class Furnizor(models.Model):
    nume = models.CharField(
        max_length=80,
        error_messages={"max_length": "Numele furnizorului poate avea cel mult 80 de caractere."},
    )
    email = models.EmailField(
        unique=True,
        error_messages={
            "unique": "Există deja un furnizor cu acest email.",
            "invalid": "Introdu o adresă de email validă.",
        },
    )
    telefon = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Număr de contact al furnizorului, cu prefix (ex: +40 721 000 000).",
    )
    oras = models.CharField(max_length=60, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Furnizori"
        ordering = ["nume"]
        indexes = [models.Index(fields=["oras"])]

    def __str__(self):
        return self.nume


class Eveniment(models.Model):
    nume = models.CharField(
        max_length=80,
        unique=True,
        error_messages={"unique": "Există deja un eveniment cu acest nume."},
    )
    data_inceput = models.DateField()
    data_sfarsit = models.DateField()
    locatie = models.CharField(max_length=100, null=True, blank=True)
    discount_procent = models.FloatField(
        default=0,
        blank=True,
        help_text="Reducerea aplicată produselor din eveniment, între 0 și 100. Lasă gol pentru fără reducere.",
    )

    class Meta:
        verbose_name_plural = "Evenimente"
        ordering = ["-data_inceput"]
        indexes = [models.Index(fields=["data_inceput"])]
        constraints = [
            models.CheckConstraint(
                condition=Q(data_sfarsit__gte=F("data_inceput")),
                name="eveniment_date_valide",
            ),
            models.CheckConstraint(
                condition=Q(discount_procent__gte=0, discount_procent__lte=100),
                name="eveniment_discount_valid",
            ),
        ]

    def __str__(self):
        return self.nume
    

class Produs(models.Model):
    TIPURI = [
        ("ceai", "Ceai"),
        ("cafea", "Cafea"),
        ("accesoriu", "Accesoriu"),
    ]

    nume = models.CharField(
        max_length=80,
        unique=True,
        error_messages={
            "unique": "Există deja un produs cu acest nume.",
            "max_length": "Numele produsului poate avea cel mult 80 de caractere.",
        },
    )
    descriere = models.TextField(null=True, blank=True)
    pret_100g = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Prețul pentru 100 g de produs, în lei. Pentru accesorii, prețul bucății.",
    )
    tip_produs = models.CharField(max_length=10, choices=TIPURI, default="ceai")
    disponibil = models.BooleanField(default=True)
    data_adaugare = models.DateTimeField(default=timezone.now)
    imagine = models.ImageField(upload_to="produse/", null=True, blank=True)
    arome = ArrayField(
        models.CharField(max_length=30),
        default=list,
        blank=True,
        help_text="Aromele produsului, separate prin virgulă (ex: vanilie, caramel, scorțișoară).",
    )
    categorie = models.ForeignKey(
        Categorie, on_delete=models.PROTECT, related_name="produse"
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name="produse"
    )
    furnizori = models.ManyToManyField(Furnizor, blank=True, related_name="produse")
    evenimente = models.ManyToManyField(Eveniment, blank=True, related_name="produse")

    class Meta:
        verbose_name_plural = "Produse"
        ordering = ["nume"]
        indexes = [
            models.Index(fields=["tip_produs"]),
            models.Index(fields=["pret_100g"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(pret_100g__gt=0),
                name="produs_pret_pozitiv",
            ),
        ]

    def __str__(self):
        return self.nume


class Varianta(models.Model):
    AMBALAJE = [
        ("punga", "Pungă"),
        ("cutie", "Cutie"),
        ("doza", "Doză"),
    ]

    produs = models.ForeignKey(
        Produs, on_delete=models.CASCADE, related_name="variante"
    )
    gramaj_g = models.PositiveIntegerField(
        help_text="Gramajul variantei, în grame (ex: 100, 250, 500)."
    )
    tip_ambalaj = models.CharField(max_length=10, choices=AMBALAJE, default="punga")
    stoc = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Variantă"
        verbose_name_plural = "Variante"
        ordering = ["produs", "gramaj_g"]
        constraints = [
            models.UniqueConstraint(
                fields=["produs", "gramaj_g"], name="varianta_unica_per_produs"
            ),
            models.CheckConstraint(
                condition=Q(gramaj_g__gt=0),
                name="varianta_gramaj_pozitiv",
            ),
        ]

    def __str__(self):
        return f"{self.produs} - {self.gramaj_g} g"