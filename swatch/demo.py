# -*- coding: utf-8 -*-
"""
Synthetic sample articles so you can see the whole platform working without internet.
Everything here is invented (fictional outlets, example.com links). It is written to *look like*
news wire copy so the same extractor runs on it as on real articles.
Built-in story planted in the last week: a spike on Ecuador -> Belgium cocaine containers,
a brand-new Peru -> Poland corridor, and two insider-type cases.
"""
import random
import datetime as dt

OUTLETS = ["Demo Daily", "Sample Herald", "Example Post", "Mock Courier", "Test Gazette"]


def _q(kg):
    return f"{kg / 1000:.1f} tonnes" if kg >= 1000 else f"{kg} kg"


def _n(n):
    return {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six"}.get(n, str(n))


COKE = [("Ecuador", "Belgium", "Antwerp", "bananas"), ("Ecuador", "Netherlands", "Rotterdam", "frozen fish"),
        ("Colombia", "Spain", "Algeciras", "coffee"), ("Brazil", "Germany", "Hamburg", "sugar"),
        ("Peru", "Italy", "Gioia Tauro", "timber"), ("Panama", "United Kingdom", "Felixstowe", "pineapples"),
        ("Ecuador", "France", "Le Havre", "bananas"), ("Colombia", "Portugal", "Sines", "fruit juice")]


def coke_container(rng, kg=None, route=None):
    o, d, port, cargo = route or rng.choice(COKE)
    kg = kg or rng.choice([120, 250, 400, 640, 780, 1200, 1900, 2300, 3100])
    n = rng.randint(0, 5)
    extra = " Investigators suspect a criminal network is behind the shipment." if rng.random() < .35 else ""
    arr = f" {_n(n)} suspects were arrested." if n else ""
    title = f"Customs seize {_q(kg)} of cocaine hidden in {cargo} shipment at {port}"
    text = (f"Customs officers at the port of {port} seized {_q(kg)} of cocaine concealed among {cargo} in a container "
            f"that departed from {o} and was bound for {d}. The container was selected after a risk analysis.{arr}{extra}")
    return title, text


def air_pax(rng):
    o = rng.choice(["Ethiopia", "Pakistan", "Colombia", "Brazil", "Nigeria"])
    airport, _ = rng.choice([("Heathrow", "UK"), ("Schiphol", "NL"), ("Sydney", "AU")])
    drug = {"Ethiopia": "heroin", "Pakistan": "heroin", "Colombia": "cocaine", "Brazil": "cocaine", "Nigeria": "methamphetamine"}[o]
    pellets = rng.randint(40, 120)
    title = f"Passenger arrested at {airport} after swallowing {pellets} pellets of {drug}"
    text = (f"A man arriving on a flight from {o} was detained at {airport} after officers found he had swallowed "
            f"{pellets} pellets of {drug}. Officers seized the pellets, weighing {rng.randint(1, 2)} kg.")
    return title, text


def road_cannabis(rng):
    ctry, o, unit = rng.choice([("Spain", "Morocco", "border crossing"), ("Italy", "Albania", "border crossing"),
                                ("France", "Spain", "border crossing"), ("Netherlands", "Belgium", "highway checkpoint")])
    kg = rng.choice([180, 340, 520, 900, 1450, 2600])
    title = f"Police seize {_q(kg)} of cannabis hidden in a truck in {ctry}"
    text = (f"Police in {ctry} seized {_q(kg)} of cannabis found in a false compartment of a truck at a {unit}. "
            f"The truck was coming from {o}. Two men were arrested.")
    return title, text


def post_nsa(rng):
    o, d, place = rng.choice([("Netherlands", "Australia", "Sydney"), ("Netherlands", "United Kingdom", "Heathrow"),
                              ("Canada", "United States", "Los Angeles")])
    pills = rng.choice([20000, 45000, 120000, 300000])
    title = f"Border officers intercept {pills:,} MDMA tablets sent by post to {d}"
    text = (f"Border officers at {place} intercepted parcels containing {pills:,} tablets of MDMA sent by post from {o}. "
            f"The parcels were bound for {d}.")
    return title, text


def meth_sea(rng):
    kg = rng.choice([90, 180, 350, 720])
    title = f"Navy intercepts fishing vessel carrying {kg} kg of methamphetamine"
    text = (f"The navy intercepted a fishing vessel near Indonesia carrying {kg} kg of methamphetamine that "
            f"originated in Myanmar, hidden under the hull compartments. Three crew members were arrested.")
    return title, text


def cigarettes(rng):
    m = rng.choice([2, 4, 8, 12])
    o, place = rng.choice([("Dubai", "Felixstowe"), ("China", "Hamburg"), ("Dubai", "Rotterdam")])
    title = f"Customs seize {m} million cigarettes in container declared as furniture at {place}"
    text = f"Customs seized {m} million cigarettes in a container declared as furniture. The container arrived at {place} from {o}."
    return title, text


def captagon(rng):
    m = rng.choice([1, 2, 3])
    title = f"Police seize {m} million captagon pills bound for Saudi Arabia"
    text = (f"Police seized {m} million captagon pills bound for Saudi Arabia hidden inside a false compartment of a "
            f"truck at the Jordan border crossing. The truck was coming from Syria. Two men were arrested.")
    return title, text


def es_container(rng):
    o, port, cargo = rng.choice([("Ecuador", "Algeciras", "bananos"), ("Colombia", "Algeciras", "café"),
                                 ("Peru", "Algeciras", "azúcar")])
    kg = rng.choice([300, 800, 1500, 2200])
    title = f"Incautan {kg:,} kilos de cocaína en el puerto de {port}".replace(",", ".")
    text = (f"La Guardia Civil incautó {kg} kilos de cocaína ocultos en un contenedor de {cargo} procedente de {o} "
            f"en el puerto de {port}. Fueron detenidas tres personas.")
    return title, text


def fr_container(rng):
    o = rng.choice(["Colombie", "Equateur"])
    kg = rng.choice([250, 600, 1100])
    title = f"Saisie de {kg} kg de cocaïne au port du Havre"
    text = (f"Les douaniers ont saisi {kg} kg de cocaïne dissimulés dans un conteneur de bananes en provenance de "
            f"{o} au port du Havre. Deux personnes ont été interpellées.")
    return title, text


def insider(rng, port):
    kg = rng.choice([300, 450, 900])
    title = f"Two port workers arrested after {kg} kg of cocaine recovered from container in {port}"
    text = (f"Two port workers were arrested after {kg} kg of cocaine was recovered from a container at the port of "
            f"{port}. Investigators suspect an extraction crew of insiders collected the drugs before customs checks.")
    return title, text


LANG = {es_container: "es", fr_container: "fr"}
BACKGROUND = [(coke_container, 36), (air_pax, 14), (road_cannabis, 12), (post_nsa, 8), (meth_sea, 5), (cigarettes, 8),
              (captagon, 5), (es_container, 7), (fr_container, 5)]


def demo_articles(today=None, seed=7):
    today = today or dt.date.today()
    rng = random.Random(seed)
    items, uid = [], [0]

    def add(day_offset, gen, lang="en", dup=True, **kw):
        title, text = gen(rng, **kw)
        pub = (today - dt.timedelta(days=day_offset)).isoformat()
        uid[0] += 1
        items.append({"url": f"https://example.com/demo/{uid[0]}", "title": title, "text": text, "published": pub,
                      "source": rng.choice(OUTLETS), "lang": lang, "source_country": None, "text_mode": "full"})
        if dup and rng.random() < .12:      # same seizure reported by a second outlet
            uid[0] += 1
            items.append({"url": f"https://example.com/demo/{uid[0]}", "title": "Drug bust: " + title, "text": text,
                          "published": pub, "source": rng.choice(OUTLETS), "lang": lang, "source_country": None,
                          "text_mode": "full"})

    weights = [g for g, w in BACKGROUND for _ in range(w)]
    for day in range(14, 80):
        for _ in range(rng.choice([0, 1, 1, 2, 2, 3])):
            g = rng.choice(weights)
            add(day, g, LANG.get(g, "en"))
    for day in range(0, 14):                      # normal activity in the last two weeks too
        for _ in range(rng.choice([0, 1, 1, 2])):
            g = rng.choice([x for x in weights if x is not coke_container])
            add(day, g, LANG.get(g, "en"))
    # planted signal 1: Ecuador -> Belgium cocaine spike, last 6 days
    for i, kg in enumerate([410, 850, 1300, 2100, 640, 1750, 930, 2600]):
        add(i % 6, coke_container, route=("Ecuador", "Belgium", "Antwerp", "bananas"), kg=kg, dup=False)
    # planted signal 2: brand-new corridor Peru -> Poland
    for i, kg in enumerate([520, 1100, 760]):
        add(2 + 3 * i, coke_container, route=("Peru", "Poland", "Gdansk", "steel"), kg=kg, dup=False)
    # planted signal 3: insider cases
    add(1, insider, port="Antwerp", dup=False)
    add(4, insider, port="Rotterdam", dup=False)
    # one invented report in each newly supported language (made-up facts)
    for i, (lang, t, x) in enumerate([
        ("ar", "ضبط 2.5 طن من الكوكايين في ميناء جدة قادمة من كولومبيا", "ضبطت الجمارك شحنة كوكايين مخبأة بين شحنة موز داخل حاوية."),
        ("tr", "Mersin Limanı'nda konteynerde 1,2 ton kokain ele geçirildi", "Ekvador'dan gelen konteynerde muz sevkiyatı arasına gizlenmiş kokain bulundu."),
        ("ru", "В порту Гамбурга изъяли 1,5 тонны кокаина из Эквадора", "Таможенники обнаружили кокаин среди бананов в контейнере."),
        ("zh", "海关在深圳港查获3.2吨可卡因，来自厄瓜多尔", "海关人员在一批香蕉集装箱中发现藏匿的可卡因。"),
        ("hi", "मुंबई एयरपोर्ट पर 5 किलो कोकीन जब्त, दो गिरफ्तार", "कस्टम अधिकारियों ने सूटकेस में छिपाई गई कोकीन बरामद की।"),
    ]):
        uid[0] += 1
        items.append({"url": f"https://example.com/demo/{lang}{i}", "title": t, "text": x, "published": (today - dt.timedelta(days=i)).isoformat(),
                      "source": "Demo Daily", "lang": lang, "source_country": None, "text_mode": "full"})
    # a few unrelated / irrelevant headlines to prove the filter works
    for i, (t, x) in enumerate([("Cannabis stocks rally as legalization bill advances", "Shares rose on the stock market."),
                                ("Local bakery wins national award", "The bakery was praised for its bread.")]):
        uid[0] += 1
        items.append({"url": f"https://example.com/demo/x{i}", "title": t, "text": x,
                      "published": today.isoformat(), "source": "Demo Daily", "lang": "en",
                      "source_country": None, "text_mode": "full"})
    return items
