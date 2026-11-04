from django.conf import settings
from django.db.models import Count
from .models import Categorie


def date_firma(request):
    return {"firma": settings.FIRMA}


def categorii_meniu(request):
    cats = Categorie.objects.annotate(n=Count("produse")).filter(n__gt=0)
    return {"categorii_meniu": cats}