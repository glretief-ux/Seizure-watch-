import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from swatch.extract import extract, parse_num

def test_parse_num():
    assert parse_num("1,200") == 1200
    assert parse_num("2,5") == 2.5
    assert parse_num("1.234,56") == 1234.56
    assert parse_num("0.500") == 0.5
    assert parse_num("1.5") == 1.5

def test_container_cocaine():
    r = extract("Customs seize 2.3 tonnes of cocaine hidden among bananas at Rotterdam port",
                "The container departed from Guayaquil, Ecuador and was bound for Belgium. Four suspects were arrested. "
                "Investigators believe a criminal network is behind the shipment.")
    assert r["relevant"] == 1
    assert r["primary_drug"] == "Cocaine"
    assert abs(r["qty_kg"] - 2300) < 1
    assert r["in_container"] == 1 and r["transport"] == "Sea - container"
    assert "Legitimate cargo (food/produce)" in r["concealment"]
    assert r["origin"] == "Ecuador" and r["destination"] == "Belgium"
    assert r["seizure_place"] == "Rotterdam" and r["seizure_country"] == "Netherlands"
    assert r["arrests"] == 4 and r["organized"] == 1
    assert r["corridor"] == "Ecuador -> Belgium"

def test_spanish():
    r = extract("Incautan 1,5 toneladas de cocaína en el puerto de Guayaquil",
                "La droga estaba oculta en un contenedor de bananos con destino a Rusia. Fueron detenidas tres personas.")
    assert r["relevant"] == 1 and r["primary_drug"] == "Cocaine"
    assert abs(r["qty_kg"] - 1500) < 1
    assert r["seizure_country"] == "Ecuador" and r["destination"] == "Russia"
    assert r["arrests"] == 3

def test_french():
    r = extract("Saisie de 800 kg de cocaïne au port du Havre",
                "La drogue était cachée dans un conteneur de bananes en provenance de Colombie. Deux personnes ont été interpellées.")
    assert r["relevant"] == 1 and r["seizure_country"] == "France" and r["origin"] == "Colombia"
    assert r["arrests"] == 2

def test_body_air():
    r = extract("Passenger arrested at airport after swallowing 90 pellets of heroin",
                "The man arrived on a flight from Karachi and was detained at Heathrow. Officers seized the pellets.")
    assert r["primary_drug"] == "Heroin/Opium"
    assert r["transport"] == "Air - passenger" and r["origin"] == "Pakistan" and r["seizure_country"] == "United Kingdom"

def test_pills_and_units():
    r = extract("Police seize 1.5 million captagon pills bound for Saudi Arabia",
                "The pills were hidden inside a false compartment of a truck at the Jordan border crossing coming from Syria.")
    assert r["primary_drug"] == "NSA" and r["qty_units"] == 1_500_000 and r["unit_type"] == "pills"
    assert r["destination"] == "Saudi Arabia" and r["origin"] == "Syria"
    assert "Vehicle compartment" in r["concealment"]

def test_cigarettes():
    r = extract("Customs seized 8 million cigarettes in a container declared as furniture",
                "The container arrived at Felixstowe from Dubai.")
    assert r["primary_drug"] == "Cigarettes" and r["qty_units"] == 8_000_000
    assert r["origin"] == "United Arab Emirates" and r["seizure_country"] == "United Kingdom"

def test_transit_and_from_to():
    r = extract("Meth haul: 300 kg seized",
                "Officers seized 300 kg of methamphetamine shipped from Mexico via Panama to Australia. Arrested two men.")
    assert r["origin"] == "Mexico" and r["destination"] == "Australia" and r["transit"] == "Panama"

def test_irrelevant():
    assert extract("Cannabis stocks rally as legalization bill advances", "Shares rose on the stock market")["relevant"] == 0
    assert extract("Local bakery wins award", "Great bread")["relevant"] == 0

def test_insider():
    r = extract("Two port workers arrested after 400 kg of cocaine recovered from container in Antwerp",
                "Port workers were arrested; an extraction crew is suspected.")
    assert r["insider"] == 1

if __name__ == "__main__":
    bad = 0
    for k, v in list(globals().items()):
        if k.startswith("test_"):
            try:
                v(); print("ok  ", k)
            except AssertionError:
                import traceback; bad += 1; print("FAIL", k); traceback.print_exc()
    sys.exit(1 if bad else 0)
