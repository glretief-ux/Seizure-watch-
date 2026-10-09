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

def _kg(title, text=""):
    return extract(title, text)["qty_kg"] if extract(title, text).get("relevant") else "not-relevant"

def test_english_three_decimals():
    assert abs(_kg("NDLEA nabs fugitive drug kingpin linked to 49.700kg heroin seizure", "Heroin worth millions was seized.") - 49.7) < 0.01
    assert abs(_kg("Police seize 9.549 kg heroin in Amritsar") - 9.549) < 0.001

def test_spanish_thousands_still_work():
    assert abs(_kg("Incautan 1.500 kilos de cocaina en el puerto de Guayaquil") - 1500) < 1

def test_running_totals_are_ignored():
    assert _kg("Colombia capturo a 21.940 criminales e incauto casi 100 toneladas de droga desde agosto") in (None, "not-relevant")
    assert _kg("Rs 14.47cr drugs seized in Mizoram in 4 days, six held", "Police seized 12 kg heroin and 3,000 kg of poppy. Since January police seized 12,746 kg.") in (None, 12.0, 3012.0)
    assert _kg("Turkiye seizes 35 tons of drugs as anti-drug operations intensify") in (None, "not-relevant")

def test_precursors_are_not_drug_weight():
    q = _kg("Aseguran en Lazaro Cardenas 27 toneladas de acido tartarico, precursor de metanfetaminas")
    assert q in (None, "not-relevant")
    assert abs(_kg("Police seize 300 kg of methamphetamine and 10 tonnes of chemical precursors") - 300) < 1

def test_k_pounds_and_first_mention():
    assert abs(_kg("Coast Guard seizes 7K pounds of cocaine near Puerto Rico") - 3175.1) < 1
    q = _kg("Cocaine seized at port", "Officers found 120 kg of cocaine in a container. In 2024 the port seized 40,255 kg of cocaine.")
    assert abs(q - 120) < 1

def test_implausible_single_seizure_dropped():
    assert _kg("Customs seize 60 tonnes of cannabis at border") in (None, "not-relevant")

def test_two_drugs_named_in_the_headline_count():
    r = extract("Police seize cocaine and cannabis in port raid", "Officers seized 40 kg of cocaine and 10 kg of cannabis.")
    assert set(r["drugs"].split("|")) == {"Cocaine", "Cannabis"}, r["drugs"]

# --- non-drug contraband categories ---------------------------------------

def test_precursor_chemical():
    r = extract("Customs seize 2 tonnes of acetic anhydride destined for a clandestine lab",
                "The chemical, a precursor used to manufacture illegal narcotics, was found in a shipping container.")
    assert r["relevant"] == 1
    assert r["category"] == "Precursor chemical"
    assert r["primary_drug"] == "Acetic anhydride"
    assert abs(r["qty_kg"] - 2000) < 1

def test_precursor_generic_fallback():
    r = extract("Police seize 50 kg of precursor chemicals in raid on clandestine laboratory", "")
    assert r["category"] == "Precursor chemical"
    assert r["primary_drug"] == "Unspecified precursor chemical"

def test_cites_timber():
    r = extract("Rangers seize illegally logged rosewood timber bound for China",
                "Wildlife officers seized 5 tonnes of rosewood, a CITES-protected timber species, hidden among general cargo.")
    assert r["relevant"] == 1
    assert r["category"] == "CITES protected timber"
    assert r["primary_drug"] == "Rosewood (Dalbergia)"
    assert abs(r["qty_kg"] - 5000) < 1

def test_stolen_vehicles():
    r = extract("Police recover 8 stolen cars in cross-border vehicle theft ring bust",
                "Officers say a criminal network is behind the vehicle theft and smuggling operation. Three suspects were arrested.")
    assert r["relevant"] == 1
    assert r["category"] == "Stolen vehicle"
    assert r["primary_drug"] == "Stolen car"
    assert r["qty_units"] == 8 and r["unit_type"] == "vehicles"
    assert r["arrests"] == 3 and r["organized"] == 1

def test_vehicle_noun_alone_is_not_enough():
    """A vehicle word with no theft/recovery cue must not be misread as a stolen-vehicle report."""
    assert extract("Local car dealership opens new showroom", "The dealership sells used cars and trucks.")["relevant"] == 0
    assert extract("Truck drivers protest fuel prices", "Hundreds of trucks blocked the highway.")["relevant"] == 0

def test_named_drug_beats_passing_drug_word_in_other_categories():
    """A precursor/timber story that happens to mention 'drugs' in passing must not be
    reclassified as a generic drug report - only a NAMED drug should win that category."""
    r = extract("Customs seize 40 kg of precursor chemicals used to manufacture illegal drugs", "")
    assert r["category"] == "Precursor chemical"
    r2 = extract("Rangers seize 4 tonnes of protected timber species logged illegally",
                 "Wildlife trafficking networks also move drugs through the same routes.")
    assert r2["category"] == "CITES protected timber"

def test_stolen_vehicle_quantity_does_not_leak_into_drug_events():
    """'2 trucks' describing the transport in a drug story must not be read as a vehicle count."""
    r = extract("Police seize 300 kg of cocaine hidden in 2 trucks at the border", "Two trucks were stopped and searched.")
    assert r["category"] == "Drug"
    assert abs(r["qty_kg"] - 300) < 1
    assert r["unit_type"] != "vehicles"

def test_arms_and_ammunition():
    r = extract("Police seize 15 rifles and 2,000 rounds of ammunition hidden in container",
                "Officers say the weapons were destined for an armed criminal network. Three suspects were arrested.")
    assert r["relevant"] == 1
    assert r["category"] == "Arms and ammunition"
    assert r["primary_drug"] == "Firearms"
    assert r["qty_units"] == 2000 and r["unit_type"] == "rounds"
    assert r["arrests"] == 3 and r["organized"] == 1

def test_arms_generic_fallback():
    r = extract("Customs seize large weapons cache destined for armed militia",
                "Officers recovered 40 firearms hidden in a shipping container declared as machinery.")
    assert r["category"] == "Arms and ammunition"

def test_gun_control_and_arms_race_are_not_seizures():
    """Political/diplomatic uses of 'arms' and 'gun' must not be misread as a contraband seizure."""
    assert extract("Lawmakers debate gun control legislation after mass shooting", "")["relevant"] == 0
    assert extract("Arms race between two nations escalates, experts warn", "")["relevant"] == 0
    assert extract("Local gun store robbed overnight, no arrests made", "")["relevant"] == 0
    assert extract("Government signs arms deal with ally nation", "")["relevant"] == 0

def test_firearms_quantity_does_not_leak_into_drug_events():
    """A pistol mentioned in passing in a drug story must not be read as the story's own quantity."""
    r = extract("Police seize 300 kg of cocaine and 3 pistols found at the scene",
                "Officers recovered the drugs and weapons together.")
    assert r["category"] == "Drug"
    assert abs(r["qty_kg"] - 300) < 1
    assert r["unit_type"] != "firearms"

if __name__ == "__main__":
    bad = 0
    for k, v in list(globals().items()):
        if k.startswith("test_"):
            try:
                v(); print("ok  ", k)
            except AssertionError:
                import traceback; bad += 1; print("FAIL", k); traceback.print_exc()
    sys.exit(1 if bad else 0)


# ---- CITES elephant ivory and other protected fauna -------------------------------------------
def test_cites_elephant_ivory():
    r = extract("Customs seize 2 tonnes of elephant ivory hidden in container bound for Vietnam",
                "Officers seized 2 tonnes of raw ivory shipped from Kenya to Vietnam, concealed among general cargo.")
    assert r["relevant"] == 1
    assert r["category"] == "CITES elephant ivory"
    assert r["primary_drug"] == "Elephant ivory"
    assert abs(r["qty_kg"] - 2000) < 1


def test_ivory_tusk_count_is_kept_as_units():
    r = extract("Police seize 14 elephant tusks in raid", "Police seized 14 tusks and arrested two men.")
    assert r["category"] == "CITES elephant ivory" and r["qty_units"] == 14 and r["unit_type"] == "tusks"


def test_ivory_coast_is_not_ivory():
    r = extract("Customs seize 500 kg of cocaine at Abidjan port in Ivory Coast",
                "Cote d'Ivoire customs seized 500 kg of cocaine.")
    assert r["category"] == "Drug"
    r2 = extract("Ivory Coast police seize stolen vehicles", "Police in Cote d'Ivoire recovered 12 stolen cars.")
    assert r2.get("category") != "CITES elephant ivory"


def test_tusk_surname_is_not_ivory():
    r = extract("Tusk says police seized documents in raid", "Prime Minister Tusk said police seized documents.")
    assert r["relevant"] == 0


def test_cites_fauna_named_species():
    r = extract("Customs seize 300 kg of pangolin scales hidden in frozen fish",
                "Customs officers seized 300 kg of pangolin scales at the port, shipped from Nigeria to Vietnam.")
    assert r["category"] == "CITES protected fauna"
    assert r["primary_drug"] == "Pangolin"
    assert abs(r["qty_kg"] - 300) < 1


def test_cites_fauna_live_animals_count():
    r = extract("Airport officers seize 80 live tortoises in suitcases",
                "Officers seized 80 tortoises hidden in luggage on a flight from Madagascar.")
    assert r["category"] == "CITES protected fauna" and r["qty_units"] == 80 and r["unit_type"] == "animals"


def test_cites_fauna_generic_and_protected_species():
    r = extract("Police seize protected animals in wildlife trafficking raid",
                "Police seized 40 kg of animal parts in a wildlife trafficking raid.")
    assert r["category"] == "CITES protected fauna"


def test_wildlife_units_do_not_leak_into_drug_events():
    r = extract("Police seize 10 kg of cocaine hidden in 3 pieces of luggage",
                "Officers seized 10 kg of cocaine in 3 pieces of luggage carried by two birds of passage travellers.")
    assert r["category"] == "Drug" and r["qty_kg"] == 10 and r["unit_type"] is None


def test_timber_still_timber_when_ivory_not_present():
    r = extract("Rangers seize illegally logged rosewood timber bound for China",
                "Wildlife officers seized 5 tonnes of rosewood, a CITES-protected timber species, hidden among general cargo.")
    assert r["category"] == "CITES protected timber"


def test_alligator_in_drug_raid_stays_drug():
    r = extract("Federal agents seize 110 lbs of drugs, baby alligator and a gun at stash house",
                "Agents seized 110 lbs of drugs and an alligator at an apartment.")
    assert r["category"] == "Drug"
