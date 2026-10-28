from datetime import datetime
from urllib.parse import urlparse
from django.http import HttpResponse, Http404
from django.shortcuts import render
from collections import Counter

ZILE = ["Luni", "Marți", "Miercuri", "Joi", "Vineri", "Sâmbătă", "Duminică"]
LUNI = ["Ianuarie", "Februarie", "Martie", "Aprilie", "Mai", "Iunie",
        "Iulie", "August", "Septembrie", "Octombrie", "Noiembrie", "Decembrie"]

FORMAT_ZI = "%A, %-d %B %Y"
FORMAT_TIMP = "%H:%M:%S"

accesari = []
PROPRIETATI = ["id", "ip_client", "url", "pagina", "data", "lista_parametri"]


class Accesare:
    _urmatorul_id = 1

    def __init__(self, ip_client, url, parametri=None):
        self.id = Accesare._urmatorul_id
        Accesare._urmatorul_id += 1
        self.ip_client = ip_client
        self._url = url
        self.parametri = parametri if parametri is not None else {}
        self._data = datetime.now()

    def lista_parametri(self):
        return [(k, v if v != "" else None) for k, v in self.parametri.items()]

    def url(self):
        return self._url

    def pagina(self):
        return urlparse(self._url).path

    def data(self, format=FORMAT_ZI, tip=""):
        if tip == "zi":
            format = FORMAT_ZI
        elif tip == "timp":
            format = FORMAT_TIMP
        elif format == FORMAT_ZI:
            format = FORMAT_ZI + ", " + FORMAT_TIMP

        d = self._data
        format = (format
                  .replace("%-d", str(d.day)).replace("%#d", str(d.day))
                  .replace("%A", ZILE[d.weekday()])
                  .replace("%B", LUNI[d.month - 1]))
        return d.strftime(format)

    def __str__(self):
        return (
            f"id: {self.id}\n"
            f"ip_client: {self.ip_client}\n"
            f"url: {self.url()}\n"
            f"pagina: {self.pagina()}\n"
            f"data: {self.data()}\n"
            f"lista_parametri: {self.lista_parametri()}\n"
        )


def creeaza_accesare(request):
    acc = Accesare(
        ip_client=request.ip_client,
        url=request.build_absolute_uri(),
        parametri=request.GET.dict(),
    )
    accesari.append(acc)
    print(acc)
    return acc


def index(request):
    creeaza_accesare(request)
    return render(request, "ceaiuri_cafea/principala.html")


def info(request):
    acc = creeaza_accesare(request)
    tip = request.GET.get("data", "")
    return render(request, "ceaiuri_cafea/info.html", {"data": acc.data(tip=tip)})

def produse(request):
    creeaza_accesare(request)
    return render(request, "ceaiuri_cafea/in_lucru.html")


def contact(request):
    creeaza_accesare(request)
    return render(request, "ceaiuri_cafea/in_lucru.html")


def cos_virtual(request):
    creeaza_accesare(request)
    return render(request, "ceaiuri_cafea/in_lucru.html")


def accesare(request, id):
    creeaza_accesare(request)
    gasita = next((a for a in accesari if a.id == int(id)), None)
    if gasita is None:
        raise Http404(f"Nu exista accesarea cu id {id}")
    return render(request, "ceaiuri_cafea/accesare.html", {"acc": gasita})

def despre(request):
    creeaza_accesare(request)
    return render(request, "ceaiuri_cafea/despre.html")


def istoric(request):
    creeaza_accesare(request)
    return render(request, "ceaiuri_cafea/istoric.html")


def valoare(acc, nume):
    v = getattr(acc, nume)
    return v() if callable(v) else v


def log(request):
    creeaza_accesare(request)
    erori = []
    lista = list(accesari)

    # iduri (poate apărea de mai multe ori, cu virgule și dubluri)
    iduri_brut = request.GET.getlist("iduri")
    if iduri_brut:
        dubluri = request.GET.get("dubluri", "false").lower() == "true"
        iduri = []
        for grup in iduri_brut:
            for x in grup.split(","):
                x = x.strip()
                if not x.isdigit():
                    erori.append(f"Id invalid: '{x}'")
                    continue
                x = int(x)
                if dubluri or x not in iduri:
                    iduri.append(x)
        dupa_id = {a.id: a for a in accesari}
        lista = []
        for i in iduri:
            if i in dupa_id:
                lista.append(dupa_id[i])
            else:
                erori.append(f"Nu exista accesarea cu id {i}")

    # ultimele
    ultimele = request.GET.get("ultimele")
    if ultimele is not None:
        try:
            n = int(ultimele)
            if n < 0:
                raise ValueError
            if n > len(lista):
                erori.append(f"Exista doar {len(lista)} accesari fata de {n} accesari cerute")
            else:
                lista = lista[len(lista) - n:]
        except ValueError:
            erori.append("Parametrul 'ultimele' trebuie sa fie un numar intreg")

    # accesari=nr / detalii
    total = None
    detalii = None
    valori_accesari = request.GET.getlist("accesari")
    if "nr" in valori_accesari:
        total = len(accesari)
    if "detalii" in valori_accesari:
        detalii = [(a.id, a.data()) for a in lista]

    # tabel
    coloane = None
    randuri = None
    tabel_brut = request.GET.getlist("tabel")
    if tabel_brut:
        cerute = [x.strip() for g in tabel_brut for x in g.split(",") if x.strip()]
        if "tot" in cerute:
            coloane = PROPRIETATI
        else:
            coloane = [c for c in cerute if c in PROPRIETATI]
            for c in cerute:
                if c not in PROPRIETATI:
                    erori.append(f"Proprietate necunoscuta: '{c}'")
        randuri = [[valoare(a, c) for c in coloane] for a in lista]

    # pagina cea mai / cel mai puțin accesată (din toate accesările)
    contor = Counter(a.pagina() for a in accesari)
    cea_mai_accesata = max(contor, key=contor.get)
    cea_mai_putin = min(contor, key=contor.get)

    return render(request, "ceaiuri_cafea/log.html", {
        "selectate": lista,
        "erori": erori,
        "nr_total": total,
        "detalii": detalii,
        "coloane": coloane,
        "randuri": randuri,
        "parametri": list(request.GET.keys()),
        "mai_mult": cea_mai_accesata,
        "mai_putin": cea_mai_putin,
    })


def in_lucru(request):
    creeaza_accesare(request)
    return render(request, "ceaiuri_cafea/in_lucru.html")