# -*- coding: utf-8 -*-
"""
Everything the extractor "knows" lives in this file: drug words, seizure verbs,
concealment methods, transport words, countries and ports.
Languages covered: English, Spanish, French, Portuguese.
Edit freely - add a word, re-run, done.

All matching is done on accent-stripped, lower-case text, so write patterns
without worrying about accents.
"""
import re
import unicodedata


def strip_accents(s):
    s = s.replace("\u0131", "i")                     # Turkish dotless i
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


# Arabic-Indic, Persian and Devanagari digits -> 0-9 ; Arabic decimal / thousands marks
_DIGITS = str.maketrans("\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669"
                        "\u06f0\u06f1\u06f2\u06f3\u06f4\u06f5\u06f6\u06f7\u06f8\u06f9"
                        "\u0966\u0967\u0968\u0969\u096a\u096b\u096c\u096d\u096e\u096f\u066b\u066c",
                        "0123456789" "0123456789" "0123456789" ".,")


def norm(s):
    return strip_accents((s or "").replace("\u2019", "'").translate(_DIGITS)).lower()


def slug(s):
    """Letters and digits of any script, single spaces (used to compare headlines)."""
    t = norm(s)
    return re.sub(r"\s+", " ", "".join(" " if unicodedata.category(c)[0] in "PSZC" else c for c in t)).strip()


def rx(*parts):
    return re.compile("|".join(strip_accents(p) for p in parts), re.I)


# --------------------------------------------------------------------------
# DRUG CATEGORIES  (aligned with the six tabs of the UNODC-WCO open-source file)
# --------------------------------------------------------------------------
DRUG_PATTERNS = {
    "Cocaine": rx(r"cocaine", r"cocaina", r"coca\s+(?:paste|leaf|leaves)", r"hojas?\s+de\s+coca",
                  r"\bcrack\b", r"pasta\s+base"),
    "Cannabis": rx(r"cannabis", r"marijuana", r"marihuana", r"\bhash(?:ish)?\b", r"\bskunk\b",
                   r"\bweed\b", r"hachis", r"haschisch", r"maconha", r"haxixe", r"\bkush\b", r"\bganja\b"),
    "Heroin/Opium": rx(r"heroin", r"heroina", r"opium", r"opio\b", r"morphine", r"\bpoppy\b",
                       r"amapola", r"pavot", r"\bopio\b"),
    "Methamphetamine": rx(r"methamphetamine", r"\bmeth\b", r"crystal\s+meth", r"metanfetamina",
                          r"\bshabu\b", r"\byaba\b"),
    # NSA = synthetic / new-substance bucket (assumption - edit to suit your definition)
    "NSA": rx(r"captagon", r"fenetylline", r"fentanyl", r"fentanil", r"\bmdma\b", r"ecstasy", r"extasis",
              r"(?<!meth)amphetamine", r"anfetamina", r"ketamine", r"tramadol",
              r"synthetic\s+(?:cannabinoid|drug|opioid)s?", r"drogas?\s+sinteticas?",
              r"drogues?\s+de\s+synthese", r"\bspice\b", r"nitazene", r"\blsd\b", r"psychoactive",
              r"mephedrone", r"cathinone", r"\bnps\b", r"pregabalin", r"oxycodone"),
    "Cigarettes": rx(r"cigarettes?", r"cigarrillos?", r"cigarros?", r"contraband\s+tobacco",
                     r"illicit\s+tobacco", r"tabaco", r"\btabac\b", r"\bshisha\b"),
}
GENERIC_DRUG = rx(r"narcotics?", r"(?:illegal|illicit)\s+drugs?", r"\bdrugs?\b", r"\bdrogas?\b",
                  r"stupefiants?", r"estupefacientes", r"narcoticos")
ANY_DRUG = re.compile("|".join(p.pattern for p in list(DRUG_PATTERNS.values()) + [GENERIC_DRUG]), re.I)

SEIZURE = rx(r"seiz", r"confiscat", r"intercept", r"\bbust(?:ed)?\b", r"\bhaul\b", r"impound",
             r"recovered", r"uncover", r"foil", r"thwart", r"smuggl", r"\bnetted\b", r"\bstash\b",
             r"discovered", r"found\s+(?:hidden|concealed)", r"incaut", r"decomis", r"aprehen",
             r"asegur", r"desarticul", r"frustr", r"saisi", r"demantel", r"apreen", r"detect",
             r"trafficking", r"trafico\s+de\s+drogas", r"tentative\s+de\s+trafic")
EXCLUDE = rx(r"\bstock\s+market\b", r"dispensar", r"legali[sz]", r"netflix", r"\bmovie\b", r"\bfilm\b",
             r"\bepisode\b", r"video\s+game", r"\bseason\s+\d",
             r"car\s+(?:dealership|insurance|show|auction|rental|wash)\b", r"\bused\s+cars?\b",
             r"\btoy\s+cars?\b", r"model\s+car", r"\bfsc[- ]certifi", r"sustainable\s+forestry",
             r"forest\s+stewardship\s+council",
             r"\bgun\s+control\b", r"\barms\s+race\b", r"\barms\s+deal\b", r"\barms\s+embargo\b",
             r"\btoy\s+guns?\b", r"\bnerf\b", r"gun\s+(?:show|range|store|shop)\b",
             r"second\s+amendment", r"gun\s+rights")

# --------------------------------------------------------------------------
# CONCEALMENT METHODS
# --------------------------------------------------------------------------
CONCEALMENT = {
    "Legitimate cargo (food/produce)": rx(
        r"banana", r"bananes?", r"bananos?", r"platanos?", r"pineapples?", r"\bpinas?\b", r"\bfruits?\b", r"\bfruta",
        r"coffee", r"\bcafe\b", r"cocoa", r"cacao", r"\bsugar\b", r"azucar", r"\bsucre\b", r"frozen",
        r"congelad", r"congele", r"seafood", r"\bfish\b", r"pescado", r"poisson", r"\bmeat\b",
        r"\bcarne\b", r"juice", r"\bjugo\b", r"\bflour\b", r"\brice\b", r"arroz", r"vegetables?",
        r"sacks?\s+of", r"\bcanned\b", r"\btinned\b", r"palm\s+oil", r"citrus", r"\bmango", r"avocado",
        r"aguacate", r"\bsoy\b", r"fresh\s+produce"),
    "Legitimate cargo (industrial/goods)": rx(
        r"timber", r"\bwood(?:en)?\b", r"madera", r"\bbois\b", r"furniture", r"muebles", r"meubles",
        r"\btiles?\b", r"ceramic", r"\bsteel\b", r"acero", r"machinery", r"maquinaria", r"\bscrap\b",
        r"chatarra", r"chemicals?", r"textiles?", r"clothing", r"garments", r"\bropa\b", r"plastic",
        r"auto\s?parts", r"spare\s+parts", r"\btyres?\b", r"\btires\b", r"cement", r"\bcoal\b",
        r"charcoal", r"carbon\b", r"fertili[sz]er", r"paper\s+rolls", r"pallets?\s+of", r"marble",
        r"marmol", r"granite", r"\bglass\b", r"\btoys\b", r"electronics", r"appliances", r"aluminium",
        r"aluminum", r"\bcopper\b", r"cosmetics", r"declared\s+as", r"mislabell?ed", r"cover\s+load",
        r"coverload", r"carga\s+de\s+cobertura"),
    "Container structure / false compartment": rx(
        r"container\s+(?:wall|walls|door|doors|roof|floor)", r"refrigeration\s+(?:unit|machinery|system)",
        r"reefer\s+(?:unit|engine)", r"modified\s+container", r"false\s+(?:wall|ceiling)"),
    "Vehicle compartment": rx(
        r"spare\s+(?:tyre|tire|wheel)", r"fuel\s+tank", r"\bchassis\b", r"engine\s+(?:block|compartment)",
        r"dashboard", r"door\s+panels?", r"neumatico\s+de\s+repuesto", r"tanque\s+de\s+combustible",
        r"(?:car|truck|lorry|van|vehicle|trailer|bus|coach|camion|vehiculo).{0,40}(?:compartment|compartimiento)"),
    "Body concealment": rx(
        r"swallow(?:ed|ing)", r"ingest(?:ed|ion)", r"pellets", r"body[- ]?pack", r"body\s+stuff",
        r"internal(?:ly)?\s+concealed", r"in\s+(?:his|her|their)\s+(?:stomach|body|intestines)",
        r"tragad", r"ingerid", r"ovulos?", r"\bavale"),
    "Postal / parcel": rx(
        r"parcels?", r"postal", r"\bmail\b", r"courier", r"express\s+(?:delivery|mail|consignment|parcel|shipment)",
        r"encomienda", r"\bcolis\b", r"correo", r"courrier", r"post\s+office"),
    "Luggage / passenger goods": rx(
        r"suitcases?", r"luggage", r"baggage", r"checked\s+bags?", r"handbag", r"backpack", r"maleta",
        r"equipaje", r"valise", r"bagage", r"mochila"),
    "Impregnation / liquid / disguised": rx(
        r"impregnat", r"dissolved", r"liquid\s+(?:cocaine|form)", r"in\s+liquid\s+form", r"disguised\s+as",
        r"camouflaged", r"masquerad", r"shaped\s+like", r"\bcoated\b", r"\bmou?lded\b", r"disimulad",
        r"disfrazad", r"deguise", r"dissimule"),
    "Vessel hull / underwater": rx(
        r"\bhull\b", r"sea\s+chest", r"underwater", r"torpedo", r"submers", r"narco[- ]?sub",
        r"under\s+the\s+waterline", r"\brudder\b", r"limpet"),
}
# generic "hidden compartment" wording - resolved to vehicle / container by context
GENERIC_COMPARTMENT = rx(
    r"(?:false|hidden|concealed|secret|specially?\s+(?:built|modified))\s+(?:compartment|panel|bottom|floor)s?",
    r"doble\s+fondo", r"falso\s+fondo", r"compartimiento\s+oculto", r"double\s+fond", r"compartiment\s+(?:cache|amenage)",
    r"\bcaleta")
VEHICLE_WORDS = rx(r"\bcar\b", r"truck", r"lorry", r"\bvan\b", r"vehicle", r"trailer", r"\bbus\b", r"coach",
                   r"camion", r"vehiculo", r"vehicule", r"tractor", r"pickup")

LEGIT_CATEGORIES = {"Legitimate cargo (food/produce)", "Legitimate cargo (industrial/goods)"}
ADVANCED_CATEGORIES = {"Container structure / false compartment", "Vehicle compartment",
                       "Hidden compartment (unspecified)", "Impregnation / liquid / disguised",
                       "Vessel hull / underwater"}

# --------------------------------------------------------------------------
# OTHER CONTRABAND CATEGORIES (non-drug) - Stolen vehicles, precursor
# chemicals, hazardous chemicals, CITES-protected timber, elephant ivory and other protected fauna. Each follows the same shape as
# DRUG_PATTERNS above: {item name shown in the dashboard: regex}, plus a
# GENERIC_* catch-all for unnamed mentions, mirroring GENERIC_DRUG.
# --------------------------------------------------------------------------
STOLEN_VEHICLE_PATTERNS = {
    "Stolen car": rx(r"\bcars?\b", r"\bsedans?\b", r"\bsuvs?\b", r"automobiles?", r"turismo", r"\bautos?\b"),
    "Stolen truck/heavy vehicle": rx(r"trucks?", r"lorr(?:y|ies)", r"\bvans?\b", r"trailers?",
                                      r"heavy\s+(?:equipment|machinery|plant)",
                                      r"construction\s+(?:vehicle|equipment)", r"camion(?:es|etas?)?"),
    "Stolen motorcycle": rx(r"motorcycles?", r"motorbikes?", r"\bscooters?\b", r"\bmoto\b", r"motocicleta",
                             r"motocyclette"),
}
GENERIC_STOLEN_VEHICLE = rx(r"stolen\s+vehicles?", r"vehiculos?\s+robados?", r"vehicules?\s+voles?",
                            r"veiculos?\s+roubados?", r"\bcar\s+theft\b", r"\bvehicle\s+theft\b")
VEHICLE_THEFT_CUE = rx(r"\bstol(?:en|e)\b", r"\btheft\b", r"\brobb?ed\b", r"hijack(?:ed|ing)?",
                       r"carjack(?:ed|ing)?", r"robad", r"\brobo\s+de\s+veh", r"vole[es]?\s+de\s+vehic",
                       r"roub(?:ado|o)\s+de\s+veic", r"recovered\s+stolen", r"cloned\s+(?:car|vehicle)",
                       r"ringing", r"vin\s+(?:tamper|altered|cloned)", r"chop\s+shop")

PRECURSOR_PATTERNS = {
    "Acetic anhydride": rx(r"acetic\s+anhydride", r"anhidrido\s+acetico", r"anhydride\s+acetique"),
    "Ephedrine/Pseudoephedrine": rx(r"ephedrine", r"pseudoephedrine", r"efedrina", r"pseudoefedrina",
                                    r"ephedrine", r"ephedrina"),
    "P2P/BMK/PMK": rx(r"\bp2p\b", r"\bbmk\b", r"\bpmk\b", r"phenylacetone", r"\bapaan\b"),
    "Potassium permanganate": rx(r"potassium\s+permanganate", r"permanganato\s+de\s+potasio",
                                 r"permanganate\s+de\s+potassium"),
    "Sodium cyanide": rx(r"sodium\s+cyanide", r"cianuro\s+de\s+sodio", r"cyanure\s+de\s+sodium"),
    "Red phosphorus": rx(r"red\s+phosphorus", r"fosforo\s+rojo", r"phosphore\s+rouge"),
    "Acetone/solvents": rx(r"\bacetone\b", r"\bacetona\b", r"\btoluene\b", r"\btolueno\b",
                           r"methyl\s+ethyl\s+ketone", r"\bmek\b"),
}
GENERIC_PRECURSOR = rx(r"precursor\s+chemicals?", r"quimicos?\s+precursores?", r"precurseurs?\s+chimiques?",
                       r"drug[- ]making\s+chemicals?", r"clandestine\s+lab(?:oratory)?",
                       r"laboratorio\s+clandestino", r"laboratoire\s+clandestin")

# Hazardous chemicals: chemicals seized for reasons OTHER than drug-making (an
# extension of the precursor category) - ozone-depleting refrigerants smuggled
# against the Montreal Protocol, banned or counterfeit pesticides, mercury
# (illegal gold mining, Minamata Convention), explosive precursors, and
# hazardous / toxic waste (Basel Convention). "Mercury" is also a planet, a car
# brand and a surname, so it only counts next to a quantity or smuggling word.
CHEMICAL_PATTERNS = {
    "Ozone-depleting refrigerants": rx(r"\bhfcs?\b", r"\bcfcs?\b", r"\bhcfcs?\b", r"hydrofluorocarbons?",
                                       r"chlorofluorocarbons?", r"ozone[- ]depleting", r"refrigerant\s+gas(?:es)?",
                                       r"refrigerants?", r"\bfreon\b", r"\br-?22\b", r"\br-?134a\b", r"\br-?404a\b",
                                       r"gases?\s+refrigerantes?", r"gaz\s+refrigerants?", r"gases?\s+refrigerantes?"),
    "Pesticides/agrochemicals": rx(r"pesticides?", r"insecticides?", r"herbicides?", r"fungicides?",
                                   r"agrochemicals?", r"agro-?chemicals?", r"plaguicidas?", r"agroquimicos?",
                                   r"agrotoxicos?", r"pesticidas?", r"produits?\s+phytosanitaires?",
                                   r"\bparaquat\b", r"\bglyphosate\b", r"chlorpyrifos"),
    "Mercury": rx(r"(?:liquid|elemental|illegal|smuggled|contraband)\s+mercury",
                  r"mercury\s+(?:smuggl\w*|seiz\w*|traffick\w*|shipment|consignment|flasks?|bottles?|used\s+in\s+(?:gold|mining))",
                  r"(?:kg|kilos?|kilograms?|kilogrammes?|tonnes?|tons?|litres?|liters?|flasks?|bottles?)\s+of\s+mercury",
                  r"mercurio\s+(?:ilegal|de\s+contrabando|liquido)", r"(?:kg|kilos?|toneladas?|litros?)\s+de\s+mercurio",
                  r"\bazogue\b", r"(?:kg|kilos?|tonnes?|litres?)\s+de\s+mercure", r"mercure\s+(?:illegal|de\s+contrebande)"),
    "Explosive precursors": rx(r"ammonium\s+nitrate", r"nitrato\s+de\s+amonio", r"nitrate\s+d.ammonium",
                               r"nitrato\s+de\s+amonio", r"potassium\s+chlorate", r"clorato\s+de\s+potasio",
                               r"chlorate\s+de\s+potassium", r"explosive\s+precursors?", r"precursores?\s+de\s+explosivos",
                               r"precurseurs?\s+d.explosifs?", r"hydrogen\s+peroxide", r"\burea\s+nitrate"),
    "Hazardous/toxic waste": rx(r"hazardous\s+waste", r"toxic\s+waste", r"chemical\s+waste", r"e-?waste",
                                r"electronic\s+waste", r"residuos\s+(?:peligrosos|toxicos)", r"desechos\s+toxicos",
                                r"dechets\s+(?:dangereux|toxiques)", r"residuos\s+perigosos", r"lixo\s+toxico",
                                r"basel\s+convention"),
    "Industrial/toxic chemicals": rx(r"sulph?uric\s+acid", r"hydrochloric\s+acid", r"\bcyanide\b(?!\s+de\s+sodium)",
                                     r"\bchlorine\s+gas", r"\bphosgene\b", r"caustic\s+soda", r"sodium\s+hydroxide",
                                     r"acido\s+sulfurico", r"acido\s+clorhidrico", r"acide\s+sulfurique"),
}
GENERIC_CHEMICAL = rx(r"hazardous\s+chemicals?", r"toxic\s+chemicals?", r"dangerous\s+chemicals?",
                      r"illegal\s+chemicals?", r"illicit\s+chemicals?", r"banned\s+chemicals?",
                      r"smuggled\s+chemicals?", r"chemicals?\s+(?:seized|smuggling|smuggled|intercepted|confiscated)",
                      r"(?:seized|seize|seizes|seizure\s+of|intercepted|confiscated)\s+(?:\S+\s+){0,4}chemicals?",
                      r"chemical\s+(?:smuggling|substances?\s+seized)", r"productos?\s+quimicos?\s+(?:peligrosos|ilegales|toxicos)",
                      r"(?:incautan|decomisan|aseguran)\s+(?:\S+\s+){0,4}(?:productos\s+)?quimicos",
                      r"substances?\s+chimiques?\s+(?:dangereuses|illegales|toxiques)", r"saisie\s+de\s+(?:produits\s+)?chimiques",
                      r"produtos?\s+quimicos?\s+(?:perigosos|ilegais|toxicos)", r"apreensao\s+de\s+produtos\s+quimicos")

# CITES-listed tree species traded as timber (Appendix I/II). Rosewoods and Pterocarpus
# dominate seizures; edit freely as listings change at each CITES CoP.
TIMBER_PATTERNS = {
    "Rosewood (Dalbergia)": rx(r"rosewood", r"dalbergia", r"palisandro", r"palissandre", r"bois\s+de\s+rose",
                               r"pau-?rosa", r"红木", r"紅木", r"酸枝", r"黄花梨", r"黃花梨", r"\bgo\s+trac\b", r"\bgo\s+cam\s+lai\b"),
    "Kosso (Pterocarpus erinaceus)": rx(r"\bkosso\b", r"pterocarpus\s+erinaceus", r"african\s+rosewood",
                                        r"\bvene\b", r"bois\s+de\s+vene", r"\bbarwood\b"),
    "Red sandalwood (Pterocarpus santalinus)": rx(r"red\s+sanders?", r"red\s+sandal(?:wood)?", r"pterocarpus\s+santalinus",
                                                  r"\blal\s+chandan\b", r"\brakta\s+chandan\b", r"लाल\s+चंदन",
                                                  r"रक्त\s+चंदन", r"小叶紫檀", r"小葉紫檀"),
    "Mukula": rx(r"\bmukula\b"),
    "Ebony": rx(r"\bebony\b", r"\bebano\b", r"\bebene\b"),
    "Agarwood": rx(r"agarwood", r"\boud\b", r"aquilaria"),
    "Ramin": rx(r"\bramin\b"),
    "Afrormosia": rx(r"afrormosia", r"assamela"),
    "Mahogany": rx(r"mahogany", r"\bcaoba\b", r"\bacajou\b", r"\bkhaya\b", r"swietenia"),
    "Spanish cedar (Cedrela)": rx(r"\bcedrela\b", r"spanish\s+cedar", r"cedro\s+(?:rosado|amargo|espanol|vermelho)"),
    "Afzelia (doussie)": rx(r"\bafzelia\b", r"\bdoussie\b", r"pod\s+mahogany", r"\blingue\b"),
    "Lignum vitae (Guaiacum)": rx(r"lignum\s+vitae", r"\bguaiacum\b", r"\bguayacan\b"),
}
# Only CITES / protected wording counts: ordinary illegal logging or lumber is not CITES wood.
GENERIC_TIMBER = rx(r"cites[- ](?:protected|listed)\s+(?:timber|wood|trees?|logs?|species\s+of\s+(?:wood|timber))",
                    r"protected\s+(?:timber|wood|tree\s+species|hardwood)", r"cites\s+(?:timber|wood|logs?)",
                    r"(?:timber|wood|logs?)\s+(?:protected|listed)\s+(?:under|by)\s+cites",
                    r"madera\s+protegida", r"especies?\s+maderables?\s+protegidas?", r"bois\s+protege",
                    r"essences?\s+protegees?", r"madeira\s+protegida",
                    r"endangered\s+(?:timber|wood|tree)s?",
                    r"wildlife\s+trafficking.{0,30}(?:timber|wood|log)")

ARMS_PATTERNS = {
    "Firearms": rx(r"firearms?", r"\bpistols?\b", r"\brevolvers?\b", r"handguns?", r"\brifles?\b",
                   r"shotguns?", r"assault\s+rifles?", r"machine\s+guns?", r"\bsubmachine\b",
                   r"armas\s+de\s+fuego", r"\bpistolas?\b", r"\brevolveres?\b", r"\bfusiles?\b",
                   r"armes\s+a\s+feu", r"\bfusils?\b", r"\bpistolets?\b"),
    "Ammunition": rx(r"ammunitions?", r"\bcartridges?\b", r"\brounds?\s+of\s+ammunition\b",
                     r"\bbullets?\b", r"municiones?", r"\bcartuchos?\b", r"munitions?",
                     r"\bcartouches?\b", r"municao", r"municoes"),
    "Explosives/grenades": rx(r"\bexplosives?\b", r"\bgrenades?\b", r"\bdetonators?\b",
                              r"\bdynamite\b", r"\bc-?4\b", r"\btnt\b", r"explosivos?",
                              r"granadas?", r"explosifs?", r"grenades?"),
}
GENERIC_ARMS = rx(r"illegal\s+(?:weapons?|arms)", r"illicit\s+(?:weapons?|arms)", r"cache\s+of\s+weapons?",
                  r"weapons?\s+cache", r"\barms\s+trafficking\b", r"\barms\s+smuggling\b",
                  r"armas\s+ilegales", r"trafico\s+de\s+armas", r"armes\s+illegales",
                  r"trafic\s+d.armes")
# CITES wildlife (fauna). Two categories, shown together under "CITES" in the
# dashboard: elephant ivory, and all other protected animals. Patterns are
# deliberately specific - bare words such as "tiger", "shark", "tusk" or
# "ivory" also mean sports teams, loan sharks, a politician's surname or the
# country Ivory Coast / Cote d'Ivoire, so they only count in a wildlife context.
IVORY_PATTERNS = {
    "Elephant ivory": rx(r"\bivory\b(?!\s+coast)(?!\s+tower)", r"elephant\s+tusks?", r"\btusks\b",
                         r"\bmarfil\b", r"(?<!d')(?<!d )\bivoire\b", r"\bmarfim\b", r"mammoth\s+ivory",
                         r"\bnga\s+voi\b"),                       # Vietnamese (ngà voi = elephant tusk / ivory)
}
FAUNA_PATTERNS = {
    "Rhino horn": rx(r"rhino(?:ceros)?\s+horns?", r"cuerno\s+de\s+rinoceronte", r"corne\s+de\s+rhinoceros",
                     r"chifre\s+de\s+rinoceronte"),
    "Pangolin": rx(r"pangolins?", r"pangolines", r"pangolim", r"pangolins"),
    "Big cat parts": rx(r"(?:tiger|leopard|lion|jaguar|snow\s+leopard|cheetah)\s+(?:skins?|pelts?|bones?|claws?|"
                        r"teeth|fangs?|parts?|cubs?|paste|carcass\w*)", r"big\s+cat\s+(?:skins?|parts?|bones?)",
                        r"piel(?:es)?\s+de\s+(?:tigre|leopardo|jaguar)", r"peau\s+de\s+(?:tigre|leopard)"),
    "Reptiles and turtles": rx(r"tortoises?", r"\bturtles?\b", r"terrapins?", r"\bpythons?\b", r"reptiles?",
                               r"\bsnakes?\b", r"\blizards?\b", r"\bgeckos?\b", r"chameleons?", r"crocodiles?",
                               r"alligators?", r"caimans?", r"iguanas?", r"tortugas?", r"tartarugas?", r"tortues?",
                               r"serpientes?", r"cobras?\b"),
    "Birds": rx(r"parrots?", r"cockatoos?", r"macaws?", r"songbirds?", r"exotic\s+birds?", r"protected\s+birds?",
                r"wild\s+birds?", r"birds?\s+of\s+prey", r"hornbills?", r"\bloros?\b", r"guacamayos?",
                r"\bperroquets?\b", r"papagaios?"),
    "Primates": rx(r"\bmonkeys?\b", r"orang-?utans?", r"chimpanzees?", r"gorillas?", r"lemurs?", r"gibbons?",
                   r"slow\s+lorises?", r"\bprimates?\b", r"\bmonos?\b", r"macacos?", r"singes?"),
    "Sharks, rays and marine species": rx(r"shark\s+(?:fins?|meat|carcass\w*|products?|parts?|cartilage)",
                                          r"fins?\s+of\s+sharks?", r"\bsea\s*horses?", r"caballitos?\s+de\s+mar",
                                          r"totoaba", r"swim\s*bladders?", r"manta\s+rays?", r"gill\s+plates?",
                                          r"queen\s+conch", r"giant\s+clams?", r"aletas?\s+de\s+tiburon",
                                          r"ailerons?\s+de\s+requin"),
    "Glass eels": rx(r"glass\s+eels?", r"eel\s+(?:trafficking|smuggling|fry|larvae)", r"\bangulas\b",
                     r"\bcivelles?\b", r"\benguias?\s+(?:vivas|juveniles)", r"\bmeixao\b"),
    "Bear parts": rx(r"bear\s+(?:bile|paws?|gall\s*bladders?|claws?|parts?|skins?)", r"bile\s+bears?"),
    "Bushmeat": rx(r"bush\s*meat", r"wild\s*meat", r"carne\s+de\s+monte", r"viande\s+de\s+brousse"),
}
GENERIC_FAUNA = rx(r"wildlife\s+(?:trafficking|traffickers?|smuggling|crime|trade|products?|parts?)",
                   r"illegal\s+wildlife", r"endangered\s+(?:animals?|species|wildlife|fauna)",
                   r"protected\s+(?:animals?|wildlife|species|fauna)", r"exotic\s+(?:animals?|pets?)",
                   r"cites[- ](?:listed|protected|appendix)", r"\bpoach(?:ed|ing|ers?)\b",
                   r"trafico\s+de\s+(?:fauna|especies|animales)", r"fauna\s+silvestre", r"especies\s+protegidas",
                   r"especies\s+amenazadas", r"faune\s+sauvage", r"especes\s+protegees", r"trafic\s+d'animaux",
                   r"animais\s+silvestres", r"trafico\s+de\s+animais", r"fauna\s+selvagem")

ANY_PRECURSOR = re.compile("|".join(p.pattern for p in list(PRECURSOR_PATTERNS.values()) + [GENERIC_PRECURSOR]), re.I)
ANY_CHEMICAL = re.compile("|".join(p.pattern for p in list(CHEMICAL_PATTERNS.values()) + [GENERIC_CHEMICAL]), re.I)
ANY_TIMBER = re.compile("|".join(p.pattern for p in list(TIMBER_PATTERNS.values()) + [GENERIC_TIMBER]), re.I)
ANY_ARMS = re.compile("|".join(p.pattern for p in list(ARMS_PATTERNS.values()) + [GENERIC_ARMS]), re.I)
ANY_STOLEN_VEHICLE = re.compile(
    "|".join(p.pattern for p in list(STOLEN_VEHICLE_PATTERNS.values()) + [GENERIC_STOLEN_VEHICLE]), re.I)
# Used by collect.py's prefilter() as the cheap headline gate - everything
# that isn't a drug mention but should still be downloaded for full-text
# extraction. Stolen vehicles are deliberately NOT included here: a vehicle
# noun alone is far too common, so collect.py additionally requires
# VEHICLE_THEFT_CUE to co-occur (see prefilter()).
ANY_IVORY = re.compile("|".join(p.pattern for p in IVORY_PATTERNS.values()), re.I)
ANY_FAUNA = re.compile("|".join(p.pattern for p in list(FAUNA_PATTERNS.values()) + [GENERIC_FAUNA]), re.I)
ANY_CONTRABAND = re.compile("|".join([ANY_DRUG.pattern, ANY_PRECURSOR.pattern, ANY_CHEMICAL.pattern, ANY_TIMBER.pattern,
                                      ANY_ARMS.pattern, ANY_IVORY.pattern, ANY_FAUNA.pattern]), re.I)

# --------------------------------------------------------------------------
# TRANSPORT
# --------------------------------------------------------------------------
CONTAINER = rx(r"containers?", r"contenedor", r"conteneur", r"conteiner", r"\bteus?\b", r"reefer")
TRANSPORT = {
    "Sea - container/cargo": rx(r"cargo\s+(?:ship|vessel)", r"container\s+ship", r"freighter", r"\bport\b",
                                r"seaport", r"puerto", r"\bporto\b", r"maritime", r"maritim", r"buque",
                                r"navire", r"navio", r"shipping", r"\bterminal\b", r"\bdock"),
    "Sea - vessel/small craft": rx(r"fishing\s+(?:boat|vessel|trawler)", r"yacht", r"sail(?:boat|ing)", r"speedboat",
                                   r"go[- ]?fast", r"semi[- ]?submersible", r"narco[- ]?sub", r"\bdhow\b", r"\bskiff\b",
                                   r"trawler", r"lancha", r"velero", r"pesquero", r"bateau", r"voilier",
                                   r"\bboat\b", r"\bvessel\b", r"\bship\b"),
    "Air": rx(r"airport", r"aeropuerto", r"aeroport", r"aeroporto", r"\bflight", r"\bvuelo", r"airline",
              r"aircraft", r"\bplane\b", r"air\s+cargo", r"airfreight", r"runway"),
    "Road": rx(r"\btruck", r"lorry", r"camion", r"border\s+crossing", r"checkpoint", r"highway", r"motorway",
               r"\bvan\b", r"trailer", r"\bbus\b", r"coach", r"\broad\b", r"carretera", r"autoroute",
               r"frontera", r"frontiere", r"vehicle", r"vehiculo", r"vehicule", r"tractor", r"\bcar\b"),
    "Rail": rx(r"\btrain\b", r"railway", r"rail\s+(?:freight|wagon|car)", r"wagon", r"ferrocarril", r"\btren\b",
               r"chemin\s+de\s+fer"),
}

# --------------------------------------------------------------------------
# INFRASTRUCTURE (finer-grained physical-location tags; an event can match several)
# Feeds the dashboard's Infrastructure checkbox filter, independent of TRANSPORT.
# --------------------------------------------------------------------------
INFRASTRUCTURE = {
    "airport": rx(r"airport", r"aeropuerto", r"aeroport", r"aeroporto", r"\brunway"),
    "air_terminal": rx(r"air\s+cargo\s+terminal", r"cargo\s+terminal", r"terminal\s+(?:\d+|building).{0,20}airport",
                       r"airport.{0,20}terminal"),
    "air": rx(r"\bflight", r"\bvuelo", r"\bairline", r"\baircraft", r"\bplane\b", r"air\s+cargo", r"airfreight",
             r"air\s+freight"),
    "port": rx(r"\bport\b", r"\bports\b", r"seaport", r"\bpuerto\b", r"\bporto\b", r"\bdock\b", r"\bdocks\b",
              r"\bquay\b", r"\bwharf\b"),
    "harbor": rx(r"harbou?r"),
    "ship_terminal": rx(r"container\s+terminal", r"shipping\s+terminal", r"\bberth\b",
                        r"terminal\s+(?:\d+|building).{0,20}(?:port|dock|container|sea)"),
    "sea": rx(r"\bsea\b", r"maritime", r"maritim", r"\bvessel\b", r"\bship\b", r"\bboat\b", r"cargo\s+ship",
             r"container\s+ship", r"freighter", r"\bbuque\b", r"\bnavire\b", r"\bnavio\b"),
    "border_crossing": rx(r"border\s+crossing", r"\bcheckpoint\b", r"\bfrontera\b", r"frontiere", r"land\s+border",
                          r"border\s+post"),
}

# --------------------------------------------------------------------------
# OTHER INDICATOR PHRASES
# --------------------------------------------------------------------------
ORGANIZED = rx(r"cartel", r"criminal\s+(?:network|organi[sz]ation|group|gang|syndicate|ring)",
               r"organi[sz]ed\s+crime", r"trafficking\s+(?:network|ring|organi[sz]ation)", r"drug\s+(?:ring|gang)",
               r"mafia", r"narcotrafic", r"organizacion\s+criminal", r"red\s+criminal", r"banda\s+criminal",
               r"organisation\s+criminelle", r"reseau\s+criminel", r"'?ndrangheta", r"camorra", r"transnational")
INSIDER = rx(r"(?:port|dock|terminal|customs|airport|airline|baggage|cargo|shipping|harbou?r)\s+"
             r"(?:workers?|employees?|officials?|officers?|staff|agents?|handlers?|inspectors?|guards?)"
             r"\s+(?:\w+\s+){0,4}?(?:arrested|detained|charged|suspected|involved|accused|bribed|corrupt)",
             r"\binsiders?\b", r"corrupt\s+(?:customs|official|officer|port)", r"rip[- ]?on", r"rip[- ]?off",
             r"extraction\s+(?:team|crew|gang)", r"\bcollusion\b", r"\bbribe", r"complicit",
             r"funcionarios?\s+(?:aduaner|portuari)\w*", r"douaniers?\s+(?:corrompus|arretes|interpelles)")
CONTROLLED_DELIVERY = rx(r"controlled\s+(?:delivery|operation)", r"entrega\s+(?:vigilada|controlada)",
                         r"livraison\s+(?:controlee|surveillee)")

# --------------------------------------------------------------------------
# ROUTE CUES (look at the ~60 characters *before* a place name)
# --------------------------------------------------------------------------
_TAIL = (r"\s*(?:the\s+|el\s+|la\s+|le\s+|l')?"
         r"(?:(?:port|puerto|porto|city|airport|aeropuerto|aeroport|ciudad|ville)\s+(?:of|de|du|da)\s+)?$")


def _cue(body):
    return re.compile("(?:" + strip_accents(body) + ")" + _TAIL, re.I)


ORIGIN_CUE = _cue(r"\bfrom|originat(?:ed|ing|es)?\s+(?:in|from|at)|departed(?:\s+from)?|\bleft|sailed\s+from|"
                  r"shipped\s+from|loaded\s+(?:in|at)|coming\s+from|arriv(?:ed|ing)\s+from|procedent\w*\s+de|"
                  r"proveniente\s+de|desde|saliendo\s+de|zarp\w+\s+de|en\s+provenance\s+de|depuis|au\s+depart\s+de|"
                  r"parti\s+de|originaire\s+de|oriundo\s+de|partiu\s+de|vindo\s+de|sourced\s+from|"
                  r"smuggled\s+from|trafficked\s+from|flew\s+from|flight\s+from|inbound\s+from|imported\s+from")
DEST_CUE = _cue(r"bound\s+for|destined\s+(?:for|to)|headed\s+(?:to|for)|heading\s+(?:to|for)|en\s+route\s+(?:to|for)|"
                r"en\s+route\s+vers|destination(?:\s+(?:was|is|being))?|(?:shipped|sent|delivered|smuggled|trafficked|"
                r"exported|consigned|dispatched|going|travell?ing|flew|flying|scheduled)\s+to|con\s+destino\s+a|"
                r"rumbo\s+a|hacia|a\s+destination\s+de|en\s+direction\s+de|com\s+destino\s+a|destinado\s+a|"
                r"outbound\s+to|onward\s+to|final\s+destination(?:\s+of)?")
TRANSIT_CUE = _cue(r"\bvia|\bthrough|transit(?:ed|ing)?(?:\s+(?:through|via|in))?|transship\w*\s+(?:in|via|through|at)|"
                   r"stopover\s+in|layover\s+in|transbord\w+\s+en|a\s+traves\s+de|escala\s+en|"
                   r"en\s+transito\s+(?:por|en)|transitant\s+par|routed\s+through|passing\s+through")
TO_CUE = _cue(r"\bto|\ba|\bvers|\bpara")

# --------------------------------------------------------------------------
# GAZETTEER: countries  (canonical | alias | alias ...)
# --------------------------------------------------------------------------
_COUNTRIES = """
Afghanistan|afganistan
Albania|albanie
Algeria|argelia|algerie|argelia
Angola
Argentina|argentine
Armenia
Australia|australie
Austria|autriche|austria
Azerbaijan
Bahamas
Bahrain|bahrein
Bangladesh
Belarus
Belgium|belgica|belgique|belgie
Benin|benin
Bolivia|bolivie|bolivia
Bosnia and Herzegovina|bosnia|bosnie
Brazil|brasil|bresil
Bulgaria|bulgarie|bulgaria
Burkina Faso
Cambodia|camboya|cambodge
Cameroon|camerun|cameroun
Canada
Cape Verde|cabo verde|cap-vert
Chile
China|chine
Colombia|colombie
Congo|dr congo|drc|democratic republic of the congo|republique democratique du congo|rdc
Costa Rica
Croatia|croacia|croatie
Cuba
Curacao
Cyprus|chipre|chypre
Czech Republic|czechia|republica checa|tchequie
Denmark|dinamarca|danemark
Dominican Republic|republica dominicana|republique dominicaine
Ecuador|equateur
Egypt|egipto|egypte|egito
El Salvador
Equatorial Guinea|guinea ecuatorial|guinee equatoriale
Estonia
Ethiopia|etiopia|ethiopie
Finland
France|francia|franca
French Guiana|guayana francesa|guyane
Gambia
Germany|alemania|allemagne|alemanha|deutschland
Ghana
Greece|grecia|grece
Guadeloupe
Guatemala
Guinea|guinee
Guinea-Bissau|guinee-bissau
Guyana
Haiti
Honduras
Hong Kong
Hungary|hungria|hongrie
Iceland|islandia
India|inde|india
Indonesia|indonesie
Iran
Iraq|irak
Ireland|irlanda|irlande
Israel
Italy|italia|italie|italia
Ivory Coast|cote d'ivoire|costa de marfil
Jamaica|jamaique
Japan|japon|japao
Jordan|jordania|jordanie
Kazakhstan
Kenya|kenia
Kosovo
Kuwait
Kyrgyzstan
Laos
Latvia|letonia|lettonie
Lebanon|libano|liban
Liberia
Libya|libia|libye
Lithuania|lituania|lituanie
Luxembourg
Madagascar
Malaysia|malasia|malaisie
Maldives
Mali
Malta|malte
Martinique
Mauritania|mauritanie
Mauritius
Mexico|mexique
Moldova
Mongolia
Montenegro
Morocco|marruecos|maroc|marrocos
Mozambique
Myanmar|burma|birmania|birmanie
Namibia
Nepal
Netherlands|holland|the netherlands|paises bajos|holanda|pays-bas
New Zealand|nueva zelanda|nouvelle-zelande
Nicaragua
Niger
Nigeria
North Macedonia
Norway|noruega|norvege
Oman
Pakistan
Panama
Papua New Guinea
Paraguay
Peru|perou
Philippines|filipinas
Poland|polonia|pologne|polonia
Portugal
Puerto Rico
Qatar|catar
Romania|rumania|roumanie|romenia
Russia|rusia|russie|russia
Rwanda
Saudi Arabia|arabia saudita|arabia saudi|arabie saoudite
Senegal
Serbia|serbie
Sierra Leone
Singapore|singapur|singapour
Slovakia|eslovaquia|slovaquie
Slovenia|eslovenia|slovenie
Somalia|somalie
South Africa|sudafrica|afrique du sud|africa do sul
South Korea|corea del sur|coree du sud
Spain|espana|espagne|espanha
Sri Lanka
Sudan|soudan
Suriname|surinam
Sweden|suecia|suede
Switzerland|suiza|suisse
Syria|siria|syrie
Taiwan
Tajikistan
Tanzania|tanzanie
Thailand|tailandia|thailande|tailandia
Togo
Trinidad and Tobago|trinidad y tobago|trinite-et-tobago
Tunisia|tunez|tunisie
Turkey|turkiye|turquia|turquie
Turkmenistan
Uganda|ouganda
Ukraine|ucrania
United Arab Emirates|uae|emiratos arabes unidos|emirats arabes unis|emirados arabes unidos
United Kingdom|uk|britain|great britain|england|scotland|wales|northern ireland|reino unido|royaume-uni
United States|usa|u.s.|u.s.a.|estados unidos|eeuu|etats-unis
Uruguay
Uzbekistan
Venezuela
Vietnam|viet nam
Yemen
Zambia|zambie
Zimbabwe
"""

COUNTRY_ALIAS = {}
for _line in _COUNTRIES.strip().splitlines():
    _parts = [p.strip() for p in _line.split("|") if p.strip()]
    for _a in _parts:
        COUNTRY_ALIAS[norm(_a)] = _parts[0]

# --------------------------------------------------------------------------
# GAZETTEER: ports / airports / cities  (display, country, [aliases])
# --------------------------------------------------------------------------
_PLACES = [
    ("Rotterdam", "Netherlands", ["rotterdam", "schiphol"]),
    ("Antwerp", "Belgium", ["antwerp", "amberes", "anvers", "antwerpen", "zeebrugge"]),
    ("Hamburg", "Germany", ["hamburg", "hamburgo", "bremerhaven"]),
    ("Algeciras", "Spain", ["algeciras", "port of valencia", "puerto de valencia", "valenciaport", "port of barcelona",
                            "puerto de barcelona", "vigo", "bilbao", "tenerife", "las palmas", "barajas"]),
    ("Sines / Lisbon", "Portugal", ["sines", "lisbon", "lisboa", "leixoes"]),
    ("Gioia Tauro", "Italy", ["gioia tauro", "genoa", "genova", "la spezia", "livorno", "naples", "napoli", "trieste",
                              "salerno"]),
    ("Le Havre", "France", ["le havre", "el havre", "havre", "marseille", "marsella", "dunkirk", "dunkerque", "roissy",
                            "charles de gaulle"]),
    ("Felixstowe", "United Kingdom", ["felixstowe", "port of southampton", "tilbury", "london gateway", "port of dover",
                                      "port of liverpool", "heathrow", "gatwick"]),
    ("Guayaquil", "Ecuador", ["guayaquil", "esmeraldas", "posorja"]),
    ("Buenaventura", "Colombia", ["buenaventura", "santa marta", "barranquilla"]),
    ("Santos", "Brazil", ["port of santos", "porto de santos", "puerto de santos", "santos port", "paranagua",
                          "itajai", "rio grande"]),
    ("Callao", "Peru", ["callao", "paita"]),
    ("Lazaro Cardenas", "Mexico", ["lazaro cardenas", "veracruz", "puerto de manzanillo"]),
    ("Colon / Balboa", "Panama", ["balboa", "puerto de colon", "port of colon"]),
    ("Puerto Cortes", "Honduras", ["puerto cortes"]),
    ("Puerto Limon", "Costa Rica", ["puerto limon", "port of limon", "moin"]),
    ("Port of Spain", "Trinidad and Tobago", ["port of spain", "puerto espana"]),
    ("Mombasa", "Kenya", ["mombasa"]),
    ("Dar es Salaam", "Tanzania", ["dar es salaam"]),
    ("Tema", "Ghana", ["tema", "takoradi"]),
    ("Lome", "Togo", ["lome"]),
    ("Cotonou", "Benin", ["cotonou"]),
    ("Abidjan", "Ivory Coast", ["abidjan"]),
    ("Dakar", "Senegal", ["dakar"]),
    ("Durban", "South Africa", ["durban", "cape town"]),
    ("Lagos", "Nigeria", ["lagos", "apapa"]),
    ("Jebel Ali", "United Arab Emirates", ["jebel ali", "dubai", "sharjah", "abu dhabi"]),
    ("Karachi", "Pakistan", ["karachi"]),
    ("Nhava Sheva / Mundra", "India", ["nhava sheva", "mundra", "chennai", "kolkata", "mumbai"]),
    ("Colombo", "Sri Lanka", ["colombo"]),
    ("Port Klang", "Malaysia", ["port klang"]),
    ("Sydney", "Australia", ["sydney", "melbourne", "brisbane"]),
    ("Tauranga", "New Zealand", ["tauranga", "auckland"]),
    ("Port Everglades", "United States", ["port everglades", "port of miami", "miami international airport",
                                          "long beach", "los angeles", "savannah", "philadelphia", "newark",
                                          "laredo", "nogales", "san diego"]),
    ("Gdansk / Gdynia", "Poland", ["gdansk", "gdynia"]),
    ("Constanta", "Romania", ["constanta"]),
    ("Piraeus", "Greece", ["piraeus", "thessaloniki"]),
    ("Koper", "Slovenia", ["koper"]),
    ("Rijeka", "Croatia", ["rijeka"]),
    ("Varna / Burgas", "Bulgaria", ["varna", "burgas"]),
    ("Tanger Med", "Morocco", ["tanger med", "tangier"]),
    ("Port Said", "Egypt", ["port said", "alexandria", "damietta"]),
    ("Aqaba", "Jordan", ["aqaba"]),
    ("Beirut", "Lebanon", ["beirut", "beyrouth"]),
    ("Latakia", "Syria", ["latakia"]),
    ("Mersin", "Turkey", ["mersin", "izmir", "istanbul"]),
    ("Bandar Abbas", "Iran", ["bandar abbas"]),
    ("Jakarta", "Indonesia", ["jakarta", "tanjung priok"]),
    ("Manila", "Philippines", ["manila"]),
    ("Laem Chabang", "Thailand", ["laem chabang", "bangkok"]),
    ("Ho Chi Minh City", "Vietnam", ["ho chi minh", "sai gon", "saigon"]),
    ("Shanghai", "China", ["shanghai", "shenzhen", "ningbo", "guangzhou"]),
    ("Busan", "South Korea", ["busan"]),
    ("Kingston", "Jamaica", ["kingston"]),
    ("Caucedo", "Dominican Republic", ["caucedo", "haina"]),
    ("Paramaribo", "Suriname", ["paramaribo"]),
    ("Montevideo", "Uruguay", ["montevideo"]),
    ("Buenos Aires", "Argentina", ["buenos aires"]),
    ("Valparaiso / Iquique", "Chile", ["valparaiso", "iquique", "arica"]),
    ("Vancouver", "Canada", ["vancouver", "montreal", "halifax"]),
    ("Gothenburg", "Sweden", ["gothenburg", "goteborg", "helsingborg"]),
    ("Freeport", "Bahamas", ["freeport"]),
]
# --- extra places: airports, big cities, states and provinces (display, country, [aliases])
_PLACES += [
    ('OR Tambo / Johannesburg', 'South Africa', ['or tambo', 'o.r. tambo', 'oliver tambo', 'johannesburg', 'joburg', 'kempton park', 'pretoria', 'gauteng']),
    ('Cape Town', 'South Africa', ['cape town']),
    ('Accra', 'Ghana', ['accra', 'kotoka']),
    ('Kumasi', 'Ghana', ['kumasi']),
    ('Abuja', 'Nigeria', ['abuja']),
    ('Kano', 'Nigeria', ['kano']),
    ('Port Harcourt', 'Nigeria', ['port harcourt']),
    ('Ogun', 'Nigeria', ['ogun', 'ogun state']),
    ('Nairobi', 'Kenya', ['nairobi', 'jomo kenyatta']),
    ('Addis Ababa', 'Ethiopia', ['addis ababa', 'bole international']),
    ('Kigali', 'Rwanda', ['kigali']),
    ('Kampala / Entebbe', 'Uganda', ['kampala', 'entebbe']),
    ('Casablanca', 'Morocco', ['casablanca']),
    ('Cairo', 'Egypt', ['cairo']),
    ('Freetown', 'Sierra Leone', ['freetown']),
    ('Conakry', 'Guinea', ['conakry']),
    ('Luanda', 'Angola', ['luanda']),
    ('Maputo', 'Mozambique', ['maputo']),
    ('Lusaka', 'Zambia', ['lusaka']),
    ('Harare', 'Zimbabwe', ['harare']),
    ('Windhoek', 'Namibia', ['windhoek']),
    ('Tunis', 'Tunisia', ['tunis']),
    ('Algiers', 'Algeria', ['algiers', 'alger']),
    ('Bamako', 'Mali', ['bamako']),
    ('Niamey', 'Niger', ['niamey']),
    ('Ouagadougou', 'Burkina Faso', ['ouagadougou']),
    ('Douala', 'Cameroon', ['douala']),
    ('Kinshasa', 'Congo', ['kinshasa']),
    ('Antananarivo', 'Madagascar', ['antananarivo']),
    ('Port Louis', 'Mauritius', ['port louis']),
    ('Khartoum', 'Sudan', ['khartoum']),
    ('Mogadishu', 'Somalia', ['mogadishu']),
    ('Doha', 'Qatar', ['doha', 'hamad international']),
    ('Dubai', 'United Arab Emirates', ['dubai']),
    ('Abu Dhabi', 'United Arab Emirates', ['abu dhabi']),
    ('Riyadh', 'Saudi Arabia', ['riyadh']),
    ('Jeddah', 'Saudi Arabia', ['jeddah']),
    ('Tehran', 'Iran', ['tehran']),
    ('Baghdad', 'Iraq', ['baghdad']),
    ('Amman', 'Jordan', ['amman']),
    ('Tel Aviv', 'Israel', ['tel aviv', 'ben gurion']),
    ('Istanbul', 'Turkey', ['istanbul']),
    ('Ankara', 'Turkey', ['ankara']),
    ('Kabul', 'Afghanistan', ['kabul', 'kandahar', 'herat']),
    ('Islamabad', 'Pakistan', ['islamabad']),
    ('Lahore', 'Pakistan', ['lahore']),
    ('Peshawar', 'Pakistan', ['peshawar']),
    ('Quetta', 'Pakistan', ['quetta', 'balochistan']),
    ('Delhi', 'India', ['delhi', 'new delhi', 'igi airport', 'indira gandhi international']),
    ('Mumbai', 'India', ['mumbai']),
    ('Kolkata', 'India', ['kolkata']),
    ('Chennai', 'India', ['chennai']),
    ('Bengaluru', 'India', ['bengaluru', 'bangalore']),
    ('Hyderabad', 'India', ['hyderabad']),
    ('Amritsar', 'India', ['amritsar', 'tarn taran', 'gurdaspur', 'ferozepur', 'fazilka', 'faridkot']),
    ('Ludhiana', 'India', ['ludhiana']),
    ('Jalandhar', 'India', ['jalandhar']),
    ('Sri Ganganagar', 'India', ['sri ganganagar', 'ganganagar']),
    ('Mizoram', 'India', ['mizoram', 'aizawl', 'champhai']),
    ('Manipur', 'India', ['manipur', 'imphal']),
    ('Assam', 'India', ['assam', 'guwahati', 'cachar']),
    ('Meghalaya', 'India', ['meghalaya']),
    ('Nagaland', 'India', ['nagaland']),
    ('Tripura', 'India', ['tripura']),
    ('Gujarat', 'India', ['gujarat', 'kutch']),
    ('Rajasthan', 'India', ['rajasthan']),
    ('Haryana', 'India', ['haryana']),
    ('Uttar Pradesh', 'India', ['uttar pradesh']),
    ('Kerala', 'India', ['kerala', 'kochi', 'palakkad']),
    ('Karnataka', 'India', ['karnataka']),
    ('Tamil Nadu', 'India', ['tamil nadu']),
    ('Maharashtra', 'India', ['maharashtra']),
    ('Odisha', 'India', ['odisha', 'orissa']),
    ('Bihar', 'India', ['bihar']),
    ('West Bengal', 'India', ['west bengal']),
    ('Jammu and Kashmir', 'India', ['jammu', 'kashmir', 'j&k']),
    ('Himachal Pradesh', 'India', ['himachal pradesh']),
    ('Uttarakhand', 'India', ['uttarakhand']),
    ('Madhya Pradesh', 'India', ['madhya pradesh']),
    ('Kathmandu', 'Nepal', ['kathmandu']),
    ('Dhaka', 'Bangladesh', ['dhaka']),
    ('Bangkok', 'Thailand', ['bangkok', 'suvarnabhumi']),
    ('Kuala Lumpur', 'Malaysia', ['kuala lumpur', 'klia']),
    ('Yangon', 'Myanmar', ['yangon']),
    ('Shan State', 'Myanmar', ['shan state']),
    ('Hanoi', 'Vietnam', ['hanoi', 'ha noi']),
    ('Phnom Penh', 'Cambodia', ['phnom penh']),
    ('Vientiane', 'Laos', ['vientiane']),
    ('Cebu', 'Philippines', ['cebu']),
    ('Davao', 'Philippines', ['davao']),
    ('Zamboanga', 'Philippines', ['zamboanga']),
    ('Mindanao', 'Philippines', ['mindanao']),
    ('Western Visayas', 'Philippines', ['western visayas', 'iloilo', 'panay', 'negros occidental', 'bacolod']),
    ('Central Visayas', 'Philippines', ['central visayas', 'bohol']),
    ('Eastern Visayas', 'Philippines', ['eastern visayas', 'leyte', 'samar', 'tacloban']),
    ('Luzon', 'Philippines', ['luzon', 'cagayan valley', 'isabela province']),
    ('Palawan', 'Philippines', ['palawan', 'puerto princesa']),
    ('Tokyo', 'Japan', ['tokyo', 'narita']),
    ('Osaka', 'Japan', ['osaka']),
    ('Seoul', 'South Korea', ['seoul', 'incheon']),
    ('Beijing', 'China', ['beijing']),
    ('Guangzhou', 'China', ['guangzhou']),
    ('Taipei', 'Taiwan', ['taipei']),
    ('Hong Kong airport', 'Hong Kong', ['chek lap kok', 'hong kong international airport', 'hong kong airport']),
    ('Dunkirk', 'France', ['dunkirk', 'dunkerque']),
    ('Paris', 'France', ['paris', 'orly']),
    ('Lyon', 'France', ['lyon']),
    ('Amsterdam', 'Netherlands', ['amsterdam']),
    ('Brussels', 'Belgium', ['brussels', 'bruxelles']),
    ('Frankfurt', 'Germany', ['frankfurt']),
    ('Munich', 'Germany', ['munich', 'munchen']),
    ('Berlin', 'Germany', ['berlin']),
    ('Madrid', 'Spain', ['madrid']),
    ('Barcelona', 'Spain', ['barcelona']),
    ('Malaga', 'Spain', ['malaga']),
    ('Rome', 'Italy', ['rome', 'fiumicino']),
    ('Milan', 'Italy', ['milan', 'malpensa']),
    ('Vienna', 'Austria', ['vienna']),
    ('Zurich', 'Switzerland', ['zurich']),
    ('Prague', 'Czech Republic', ['prague']),
    ('Warsaw', 'Poland', ['warsaw']),
    ('Athens', 'Greece', ['athens']),
    ('Sofia', 'Bulgaria', ['sofia']),
    ('Bucharest', 'Romania', ['bucharest']),
    ('Belgrade', 'Serbia', ['belgrade']),
    ('Budapest', 'Hungary', ['budapest']),
    ('Moscow', 'Russia', ['moscow']),
    ('Kyiv', 'Ukraine', ['kyiv', 'kiev']),
    ('Copenhagen', 'Denmark', ['copenhagen']),
    ('Stockholm', 'Sweden', ['stockholm']),
    ('Oslo', 'Norway', ['oslo']),
    ('Helsinki', 'Finland', ['helsinki']),
    ('London', 'United Kingdom', ['london', 'stansted', 'luton']),
    ('Manchester', 'United Kingdom', ['manchester']),
    ('Birmingham', 'United Kingdom', ['birmingham']),
    ('Liverpool', 'United Kingdom', ['liverpool']),
    ('Glasgow', 'United Kingdom', ['glasgow']),
    ('Edinburgh', 'United Kingdom', ['edinburgh']),
    ('Belfast', 'United Kingdom', ['belfast', 'craigavon', 'northern ireland']),
    ('Cardiff', 'United Kingdom', ['cardiff']),
    ('Scotland', 'United Kingdom', ['scotland']),
    ('Wales', 'United Kingdom', ['wales']),
    ('Dublin', 'Ireland', ['dublin']),
    ('Cork', 'Ireland', ['cork']),
    ('Galway', 'Ireland', ['galway']),
    ('Alabama', 'United States', ['alabama']),
    ('Alaska', 'United States', ['alaska']),
    ('Arizona', 'United States', ['arizona']),
    ('Arkansas', 'United States', ['arkansas']),
    ('California', 'United States', ['california']),
    ('Colorado', 'United States', ['colorado']),
    ('Connecticut', 'United States', ['connecticut']),
    ('Delaware', 'United States', ['delaware']),
    ('Florida', 'United States', ['florida']),
    ('Hawaii', 'United States', ['hawaii']),
    ('Idaho', 'United States', ['idaho']),
    ('Illinois', 'United States', ['illinois']),
    ('Indiana', 'United States', ['indiana']),
    ('Iowa', 'United States', ['iowa']),
    ('Kansas', 'United States', ['kansas']),
    ('Kentucky', 'United States', ['kentucky']),
    ('Louisiana', 'United States', ['louisiana']),
    ('Maine', 'United States', ['maine']),
    ('Maryland', 'United States', ['maryland']),
    ('Massachusetts', 'United States', ['massachusetts']),
    ('Michigan', 'United States', ['michigan']),
    ('Minnesota', 'United States', ['minnesota']),
    ('Mississippi', 'United States', ['mississippi']),
    ('Missouri', 'United States', ['missouri']),
    ('Montana', 'United States', ['montana']),
    ('Nebraska', 'United States', ['nebraska']),
    ('Nevada', 'United States', ['nevada']),
    ('New Hampshire', 'United States', ['new hampshire']),
    ('New Jersey', 'United States', ['new jersey']),
    ('New Mexico', 'United States', ['new mexico']),
    ('New York', 'United States', ['new york']),
    ('North Carolina', 'United States', ['north carolina']),
    ('North Dakota', 'United States', ['north dakota']),
    ('Ohio', 'United States', ['ohio']),
    ('Oklahoma', 'United States', ['oklahoma']),
    ('Oregon', 'United States', ['oregon']),
    ('Pennsylvania', 'United States', ['pennsylvania']),
    ('Rhode Island', 'United States', ['rhode island']),
    ('South Carolina', 'United States', ['south carolina']),
    ('South Dakota', 'United States', ['south dakota']),
    ('Tennessee', 'United States', ['tennessee']),
    ('Texas', 'United States', ['texas']),
    ('Utah', 'United States', ['utah']),
    ('Vermont', 'United States', ['vermont']),
    ('Virginia', 'United States', ['virginia']),
    ('Washington', 'United States', ['washington state', 'washington']),
    ('West Virginia', 'United States', ['west virginia']),
    ('Wisconsin', 'United States', ['wisconsin']),
    ('Wyoming', 'United States', ['wyoming']),
    ('Chicago', 'United States', ['chicago']),
    ('Houston', 'United States', ['houston']),
    ('Dallas', 'United States', ['dallas']),
    ('Atlanta', 'United States', ['atlanta']),
    ('Seattle', 'United States', ['seattle']),
    ('Boston', 'United States', ['boston']),
    ('Detroit', 'United States', ['detroit']),
    ('Phoenix', 'United States', ['phoenix']),
    ('Denver', 'United States', ['denver']),
    ('Las Vegas', 'United States', ['las vegas']),
    ('San Francisco', 'United States', ['san francisco']),
    ('Miami', 'United States', ['miami']),
    ('Baltimore', 'United States', ['baltimore']),
    ('Fresno', 'United States', ['fresno']),
    ('Bakersfield', 'United States', ['bakersfield', 'visalia']),
    ('Sacramento', 'United States', ['sacramento']),
    ('Tucson', 'United States', ['tucson']),
    ('El Paso', 'United States', ['el paso']),
    ('British Columbia', 'Canada', ['british columbia']),
    ('Ontario', 'Canada', ['ontario']),
    ('Alberta', 'Canada', ['alberta', 'lloydminster']),
    ('Quebec', 'Canada', ['quebec']),
    ('Manitoba', 'Canada', ['manitoba']),
    ('Saskatchewan', 'Canada', ['saskatchewan']),
    ('Nova Scotia', 'Canada', ['nova scotia']),
    ('Toronto', 'Canada', ['toronto']),
    ('Calgary', 'Canada', ['calgary']),
    ('Edmonton', 'Canada', ['edmonton']),
    ('Ottawa', 'Canada', ['ottawa']),
    ('Winnipeg', 'Canada', ['winnipeg']),
    ('New South Wales', 'Australia', ['new south wales', 'nsw']),
    ('Queensland', 'Australia', ['queensland']),
    ('Western Australia', 'Australia', ['western australia']),
    ('South Australia', 'Australia', ['south australia']),
    ('Tasmania', 'Australia', ['tasmania']),
    ('Perth', 'Australia', ['perth']),
    ('Adelaide', 'Australia', ['adelaide']),
    ('Canberra', 'Australia', ['canberra']),
    ('Darwin', 'Australia', ['darwin']),
    ('Wellington', 'New Zealand', ['wellington']),
    ('Mexico City', 'Mexico', ['mexico city', 'ciudad de mexico', 'cdmx']),
    ('Michoacan', 'Mexico', ['michoacan']),
    ('Guerrero', 'Mexico', ['guerrero']),
    ('Sinaloa', 'Mexico', ['sinaloa', 'culiacan']),
    ('Sonora', 'Mexico', ['sonora']),
    ('Jalisco', 'Mexico', ['jalisco', 'guadalajara']),
    ('Chihuahua', 'Mexico', ['chihuahua']),
    ('Tijuana', 'Mexico', ['tijuana', 'baja california']),
    ('Tamaulipas', 'Mexico', ['tamaulipas']),
    ('Monterrey', 'Mexico', ['monterrey', 'nuevo leon']),
    ('Oaxaca', 'Mexico', ['oaxaca']),
    ('Chiapas', 'Mexico', ['chiapas']),
    ('Manzanillo', 'Mexico', ['manzanillo']),
    ('Guatemala City', 'Guatemala', ['guatemala city', 'ciudad de guatemala']),
    ('Tegucigalpa', 'Honduras', ['tegucigalpa']),
    ('San Salvador', 'El Salvador', ['san salvador']),
    ('Managua', 'Nicaragua', ['managua']),
    ('Tocumen', 'Panama', ['tocumen']),
    ('Bogota', 'Colombia', ['bogota']),
    ('Medellin', 'Colombia', ['medellin']),
    ('Cartagena', 'Colombia', ['cartagena']),
    ('Quito', 'Ecuador', ['quito']),
    ('Manta', 'Ecuador', ['manta', 'manabi']),
    ('Lima', 'Peru', ['lima']),
    ('Sao Paulo', 'Brazil', ['sao paulo', 'guarulhos']),
    ('Rio de Janeiro', 'Brazil', ['rio de janeiro']),
    ('Brasilia', 'Brazil', ['brasilia']),
    ('Fortaleza', 'Brazil', ['fortaleza']),
    ('Recife', 'Brazil', ['recife']),
    ('Caracas', 'Venezuela', ['caracas']),
    ('La Paz', 'Bolivia', ['la paz']),
    ('Asuncion', 'Paraguay', ['asuncion']),
    ('Santiago', 'Chile', ['santiago de chile']),
    ('Havana', 'Cuba', ['havana', 'la habana']),
    ('Santo Domingo', 'Dominican Republic', ['santo domingo']),
    ('Port-au-Prince', 'Haiti', ['port-au-prince', 'port au prince']),
    ('Nassau', 'Bahamas', ['nassau']),
    ('San Juan', 'Puerto Rico', ['san juan']),
]
# --- more ports and airports (display, country, [aliases])
_PLACES_MORE = [
    ('Posorja', 'Ecuador', ['posorja']),
    ('Esmeraldas', 'Ecuador', ['esmeraldas']),
    ('Puerto Bolivar', 'Ecuador', ['puerto bolivar']),
    ('Santa Marta', 'Colombia', ['santa marta']),
    ('Barranquilla', 'Colombia', ['barranquilla']),
    ('Tumaco', 'Colombia', ['tumaco']),
    ('Paita', 'Peru', ['paita']),
    ('Chancay', 'Peru', ['chancay']),
    ('Paranagua', 'Brazil', ['paranagua']),
    ('Itajai', 'Brazil', ['itajai']),
    ('Rio Grande', 'Brazil', ['rio grande']),
    ('Suape', 'Brazil', ['suape']),
    ('Pecem', 'Brazil', ['pecem']),
    ('Rosario', 'Argentina', ['rosario']),
    ('Cristobal', 'Panama', ['cristobal']),
    ('Bocas del Toro', 'Panama', ['bocas del toro']),
    ('Puerto Quetzal', 'Guatemala', ['puerto quetzal']),
    ('Santo Tomas de Castilla', 'Guatemala', ['santo tomas de castilla']),
    ('Puerto Moin', 'Costa Rica', ['puerto moin', 'limon-moin']),
    ('Haina', 'Dominican Republic', ['haina']),
    ('Point Lisas', 'Trinidad and Tobago', ['point lisas']),
    ('Willemstad', 'Curacao', ['willemstad']),
    ('Veracruz', 'Mexico', ['veracruz']),
    ('Altamira', 'Mexico', ['altamira']),
    ('Ensenada', 'Mexico', ['ensenada']),
    ('Los Angeles', 'United States', ['los angeles', 'port of los angeles']),
    ('Long Beach', 'United States', ['long beach']),
    ('Oakland', 'United States', ['oakland']),
    ('Savannah', 'United States', ['savannah']),
    ('Charleston', 'United States', ['charleston']),
    ('Norfolk', 'United States', ['norfolk']),
    ('Newark', 'United States', ['newark', 'port newark']),
    ('Philadelphia', 'United States', ['philadelphia']),
    ('JFK airport', 'United States', ['jfk']),
    ('LAX airport', 'United States', ['lax']),
    ('Marseille-Fos', 'France', ['marseille', 'marseilles', 'marseille-fos', 'fos-sur-mer', 'marsella']),
    ('Bremerhaven', 'Germany', ['bremerhaven']),
    ('Zeebrugge', 'Belgium', ['zeebrugge']),
    ('Valencia', 'Spain', ['valenciaport', 'port of valencia', 'puerto de valencia']),
    ('Vigo', 'Spain', ['vigo']),
    ('Bilbao', 'Spain', ['bilbao']),
    ('Las Palmas', 'Spain', ['las palmas']),
    ('Tenerife', 'Spain', ['tenerife']),
    ('Genoa', 'Italy', ['genoa', 'genova']),
    ('La Spezia', 'Italy', ['la spezia']),
    ('Livorno', 'Italy', ['livorno']),
    ('Naples', 'Italy', ['naples', 'napoli']),
    ('Trieste', 'Italy', ['trieste']),
    ('Salerno', 'Italy', ['salerno']),
    ('Southampton', 'United Kingdom', ['southampton', 'port of southampton']),
    ('London Gateway', 'United Kingdom', ['london gateway', 'tilbury']),
    ('Dover', 'United Kingdom', ['dover', 'port of dover']),
    ('Klaipeda', 'Lithuania', ['klaipeda']),
    ('Riga', 'Latvia', ['riga']),
    ('Tallinn', 'Estonia', ['tallinn']),
    ('Leixoes', 'Portugal', ['leixoes']),
    ('Heathrow airport', 'United Kingdom', ['heathrow']),
    ('Gatwick airport', 'United Kingdom', ['gatwick']),
    ('Schiphol airport', 'Netherlands', ['schiphol']),
    ('Charles de Gaulle airport', 'France', ['charles de gaulle', 'roissy', 'cdg']),
    ('Barajas airport', 'Spain', ['barajas']),
    ('Monrovia', 'Liberia', ['monrovia']),
    ('Banjul', 'Gambia', ['banjul']),
    ('Nouakchott', 'Mauritania', ['nouakchott']),
    ('Bissau', 'Guinea-Bissau', ['bissau']),
    ('Takoradi', 'Ghana', ['takoradi']),
    ('Pointe-Noire', 'Congo', ['pointe-noire', 'pointe noire']),
    ('Walvis Bay', 'Namibia', ['walvis bay']),
    ('Beira', 'Mozambique', ['beira']),
    ('Nacala', 'Mozambique', ['nacala']),
    ('Khor Fakkan', 'United Arab Emirates', ['khor fakkan']),
    ('Sharjah', 'United Arab Emirates', ['sharjah']),
    ('Salalah', 'Oman', ['salalah']),
    ('Sohar', 'Oman', ['sohar']),
    ('Dammam', 'Saudi Arabia', ['dammam']),
    ('Izmir', 'Turkey', ['izmir']),
    ('Ambarli', 'Turkey', ['ambarli']),
    ('Haifa', 'Israel', ['haifa']),
    ('Ashdod', 'Israel', ['ashdod']),
    ('Umm Qasr', 'Iraq', ['umm qasr', 'basra']),
    ('Chittagong', 'Bangladesh', ['chittagong', 'chattogram']),
    ('Tanjung Pelepas', 'Malaysia', ['tanjung pelepas']),
    ('Surabaya', 'Indonesia', ['surabaya']),
    ('Haiphong', 'Vietnam', ['haiphong', 'hai phong']),
    ('Ningbo', 'China', ['ningbo']),
    ('Shenzhen', 'China', ['shenzhen', 'yantian', 'shekou', '深圳', '深圳港']),
    ('Qingdao', 'China', ['qingdao', '青岛', '青島']),
    ('Tianjin', 'China', ['tianjin', '天津']),
    ('Yokohama', 'Japan', ['yokohama']),
    ('Kaohsiung', 'Taiwan', ['kaohsiung', '高雄']),
    ('Kandla', 'India', ['kandla']),
    ('Tuticorin', 'India', ['tuticorin']),
    ('Visakhapatnam', 'India', ['visakhapatnam']),
    ('Gwadar', 'Pakistan', ['gwadar']),
    ('Melbourne', 'Australia', ['melbourne']),
    ('Brisbane', 'Australia', ['brisbane']),
    ('Fremantle', 'Australia', ['fremantle']),
    ('Auckland', 'New Zealand', ['auckland']),
]
_PLACES += _PLACES_MORE
PLACE_ALIAS = {}
for _disp, _ctry, _als in _PLACES:
    for _a in _als:
        PLACE_ALIAS[norm(_a)] = (_disp, _ctry)


# --------------------------------------------------------------------------
# MORE LANGUAGES: Arabic, Turkish, Russian, Chinese (simplified and traditional), Hindi
# --------------------------------------------------------------------------
def _bs(x):
    return re.sub(r"\\+", r"\\", x)               # tidy doubled backslashes in the word lists


def _ext(rxobj, *parts):
    """Same pattern plus more alternatives."""
    return re.compile(rxobj.pattern + "|" + "|".join(strip_accents(_bs(p)) for p in parts), re.I)


# (the word lists below were written for Arabic, Turkish, Russian, Chinese and Hindi)
"""Words for Arabic, Turkish, Russian, Chinese (simplified + traditional) and Hindi.
Every string is passed through lexicon.strip_accents / norm, so accents, Arabic vowel marks, hamza forms and
Devanagari nukta are normalised on both sides."""

# ---- drug words (regex parts, appended to the existing category patterns)
DRUG_EXTRA = {
    "Cocaine": [
        "كوكايين", "كوكاين", "kokain", "кокаин", "可卡因", "古柯碱", "古柯堿", "古柯鹼", "कोकीन", "कोकेन"],
    "Cannabis": [
        "حشيش", "ماريجوانا", "ماريجوانه", "بانجو", "القنب", "esrar", "kenevir", "hashis", "марихуан", "гашиш", "каннабис",
        "конопл", "анаша", "大麻", "गांजा", "चरस", "मारिजुआना", "हशीश", r"(?<![\u0900-\u097f])भांग(?![\u0900-\u097f])"],
    "Heroin/Opium": [
        "هيروين", "افيون", "أفيون", "eroin", "afyon", "героин", "опий", "опиат", "海洛因", "海洛英", "鸦片", "鴉片", "阿片",
        "हेरोइन", "हीरोइन", "अफीम", "स्मैक", "ब्राउन शुगर", "डोडा चूरा"],
    "Methamphetamine": [
        "ميثامفيتامين", "ميثامفيتامين", "الشابو", "metamfetamin", "метамфетамин", "冰毒", "甲基苯丙胺", "甲基安非他命",
        "मेथामफेटामाइन", "मेथएम्फेटामाइन", r"(?<![\u0900-\u097f])मेथ(?![\u0900-\u097f])"],
    "NSA": [
        "كبتاجون", "كابتاجون", "كبتاغون", "كابتاغون", "ترامادول", "امفيتامين", "أمفيتامين", "اكستاسي", "كيتامين", "فنتانيل",
        "مخدرات تخليقية", "حبوب مخدرة", "اقراص مخدرة", "أقراص مخدرة",
        "kaptagon", "ekstazi", "sentetik uyusturucu", "uyusturucu hap", "bonzai", "amfetamin", "ketamin", "fentanil",
        "(?<!мет)амфетамин", "мефедрон", r"синтетическ\w+\s+наркотик", "спайс", "экстази", "кетамин", "фентанил",
        "трамадол", "каптагон", "психотропн",
        "摇头丸", "搖頭丸", "k粉", "氯胺酮", "芬太尼", "卡西酮", "新型毒品", "合成毒品", "曲马多", "曲馬多", "依托咪酯",
        "太空油", "(?<!甲基)安非他命", "(?<!甲基)苯丙胺",
        "ट्रामाडोल", "कैप्टागन", "एक्स्टसी", "सिंथेटिक ड्रग", "नशीली गोलियां", "नशीली गोलियाँ", "नशीले कैप्सूल", "एमडीएमए",
        "मेफेड्रोन", "फेंटेनिल", "केटामाइन"],
    "Cigarettes": [
        "سجائر", "تبغ", "kacak sigara", "sigara kacakciligi", "сигарет", "табачн", "香烟", "香菸", "卷烟", "捲菸", "私烟",
        "烟草", "菸草", "सिगरेट", "तंबाकू"],
}
GENERIC_EXTRA = ["مخدرات", "مواد مخدرة", "المخدر", "uyusturucu", "narkotik", "наркотик", "наркотическ", "психотропн",
                 "毒品", "ड्रग्स", "नशीला पदार्थ", "नशीले पदार्थ", "मादक पदार्थ", "नारकोटिक्स"]
SEIZURE_EXTRA = [
    "ضبط", "احباط", "احبط", "مصادر", "تهريب", "القبض على",
    "ele gecir", "el konul", "yakalan", "kacakcilik",
    "изъял", "изъят", "конфиск", "задержа", "пресек", "контрабанд", "обнаружил",
    "缴获", "繳獲", "查获", "查獲", "截获", "截獲", "破获", "破獲", "缉获", "緝獲", "起获", "檢獲", "检获", "查扣", "扣押", "走私",
    "जब्त", "बरामद", "पकडा", "पकडे", "तस्करी", "भंडाफोड",
    # Vietnamese (seized, confiscated, caught red-handed, smuggling, illegal transport, busted, found, exhibits)
    r"\bbat\s+giu\b", r"\btich\s+thu\b", r"\bthu\s+giu\b", r"\bbat\s+qua\s+tang\b", r"\bbuon\s+lau\b",
    r"\bvan\s+chuyen\s+trai\s+phep\b", r"\btriet\s+pha\b", r"\bphat\s+hien\b", r"\btang\s+vat\b",
]
CONTAINER_EXTRA = ["حاوية", "حاويات", "konteyner", "контейнер", "集装箱", "集裝箱", "货柜", "貨櫃", "कंटेनर"]
PORT_WORDS = [r"ميناء", r"(?<![a-z])liman", r"морск\w+\s+порт", r"(?<![а-я])порт", r"港口", r"(?<!香)港", r"बंदरगाह"]
AIR_WORDS = ["مطار", "havalimani", "havaalani", "аэропорт", "机场", "機場", "एयरपोर्ट", "हवाई अड्डा"]
ROAD_WORDS = ["شاحنة", "شاحنات", r"tir\b", "kamyon", "грузовик", "фур[аы]", "卡车", "貨車", "货车", "ट्रक"]

# ---- weight units: (regex part, kg factor)
UNITS_EXTRA = [
    ("كيلوغرام", 1), ("كيلوجرام", 1), ("كغ", 1), ("كجم", 1), ("أطنان", 1000), ("اطنان", 1000), ("طن", 1000),
    (r"килограмм\w*", 1), ("кг", 1), (r"тонн\w*", 1000),
    ("公斤", 1), ("千克", 1), ("公吨", 1000), ("吨", 1000), ("噸", 1000),
    ("किलोग्राम", 1), ("किलो", 1), ("किग्रा", 1), ("टन", 1000), ("क्विंटल", 100),
    ("kilogam", 1), ("ki-lo-gam", 1), ("ki lo gam", 1), ("tan", 1000),   # Vietnamese: ki-lô-gam, tấn (tonne)
]

# ---- countries: English name | Arabic | Turkish | Russian stem | Chinese simplified | Chinese traditional | Hindi
# (blank field = none). Russian stems get case endings automatically.
COUNTRIES = r"""
Afghanistan|أفغانستان|afganistan|афганистан|阿富汗||अफगानिस्तान
Albania|ألبانيا|arnavutluk|албани|阿尔巴尼亚|阿爾巴尼亞|अल्बानिया
Algeria|الجزائر|cezayir|алжир|阿尔及利亚|阿爾及利亞|अल्जीरिया
Angola|أنغولا|angola|ангол|安哥拉||अंगोला
Argentina|الأرجنتين|arjantin|аргентин|阿根廷||अर्जेंटीना
Australia|أستراليا|avustralya|австрали|澳大利亚|澳洲|ऑस्ट्रेलिया
Austria|النمسا|avusturya|австри|奥地利|奧地利|ऑस्ट्रिया
Bahrain|البحرين|bahreyn|бахрейн|巴林||बहरीन
Bangladesh|بنغلاديش|banglades|бангладеш|孟加拉国|孟加拉|बांग्लादेश
Belgium|بلجيكا|belcika|бельги|比利时|比利時|बेल्जियम
Bolivia|بوليفيا|bolivya|боливи|玻利维亚|玻利維亞|बोलीविया
Brazil|البرازيل|brezilya|бразили|巴西||ब्राज़ील
Bulgaria|بلغاريا|bulgaristan|болгари|保加利亚|保加利亞|बुल्गारिया
Cambodia|كمبوديا|kambocya|камбодж|柬埔寨||कंबोडिया
Cameroon|الكاميرون|kamerun|камерун|喀麦隆|喀麥隆|कैमरून
Canada|كندا|kanada|канад|加拿大||कनाडा
Chile|تشيلي|sili|чили|智利||चिली
China|الصين|cin|китай|中国|中國|चीन
Colombia|كولومبيا|kolombiya|колумби|哥伦比亚|哥倫比亞|कोलंबिया
Costa Rica|كوستاريكا|kosta rika|коста-рик|哥斯达黎加|哥斯大黎加|कोस्टा रिका
Croatia|كرواتيا|hirvatistan|хорвати|克罗地亚|克羅地亞|क्रोएशिया
Cuba|كوبا|kuba|куб|古巴||क्यूबा
Cyprus|قبرص|kibris|кипр|塞浦路斯||साइप्रस
Czech Republic|التشيك|cekya|чехи|捷克||चेक गणराज्य
Denmark|الدنمارك|danimarka|дани|丹麦|丹麥|डेनमार्क
Dominican Republic|الدومينيكان|dominik cumhuriyeti|доминикан|多米尼加||डोमिनिकन गणराज्य
Ecuador|الإكوادور|ekvador|эквадор|厄瓜多尔|厄瓜多爾|इक्वाडोर
Egypt|مصر|misir|египет|埃及||मिस्र
El Salvador|السلفادور|el salvador|сальвадор|萨尔瓦多|薩爾瓦多|अल साल्वाडोर
Finland|فنلندا|finlandiya|финлянди|芬兰|芬蘭|फिनलैंड
France|فرنسا|fransa|франци|法国|法國|फ्रांस
Germany|ألمانيا|almanya|германи|德国|德國|जर्मनी
Ghana|غانا|gana|гана|加纳|加納|घाना
Greece|اليونان|yunanistan|греци|希腊|希臘|ग्रीस
Guatemala|غواتيمالا|guatemala|гватемал|危地马拉|瓜地馬拉|ग्वाटेमाला
Guinea|غينيا|gine|гвине|几内亚|幾內亞|गिनी
Haiti|هايتي|haiti|гаити|海地||हैती
Honduras|هندوراس|honduras|гондурас|洪都拉斯||होंडुरास
Hong Kong|هونغ كونغ|hong kong|гонконг|香港||हांगकांग
Hungary|المجر|macaristan|венгри|匈牙利||हंगरी
India|الهند|hindistan|инди|印度||भारत
Indonesia|إندونيسيا|endonezya|индонези|印度尼西亚|印尼|इंडोनेशिया
Iran|إيران|iran|иран|伊朗||ईरान
Iraq|العراق|irak|ирак|伊拉克||इराक
Ireland|أيرلندا|irlanda|ирланди|爱尔兰|愛爾蘭|आयरलैंड
Israel|إسرائيل|israil|израил|以色列||इज़राइल
Italy|إيطاليا|italya|итали|意大利||इटली
Ivory Coast|ساحل العاج|fildisi sahili|кот-д'ивуар|科特迪瓦||आइवरी कोस्ट
Jamaica|جامايكا|jamaika|ямайк|牙买加|牙買加|जमैका
Japan|اليابان|japonya|япони|日本||जापान
Jordan|الأردن|urdun|иордани|约旦|約旦|जॉर्डन
Kazakhstan|كازاخستان|kazakistan|казахстан|哈萨克斯坦|哈薩克|कजाकिस्तान
Kenya|كينيا|kenya|кени|肯尼亚|肯亞|केन्या
Kuwait|الكويت|kuveyt|кувейт|科威特||कुवैत
Kyrgyzstan|قرغيزستان|kirgizistan|киргиз|吉尔吉斯斯坦|吉爾吉斯|किर्गिस्तान
Laos|لاوس|laos|лаос|老挝|寮國|लाओस
Lebanon|لبنان|lubnan|ливан|黎巴嫩||लेबनान
Libya|ليبيا|libya|ливи|利比亚|利比亞|लीबिया
Malaysia|ماليزيا|malezya|малайзи|马来西亚|馬來西亞|मलेशिया
Mali||mali|мали|马里|馬利|माली
Mexico|المكسيك|meksika|мексик|墨西哥||मेक्सिको
Morocco|المغرب|fas|марокко|摩洛哥||मोरक्को
Mozambique|موزمبيق|mozambik|мозамбик|莫桑比克||मोज़ाम्बिक
Myanmar|ميانمار|myanmar|мьянм|缅甸|緬甸|म्यांमार
Nepal|نيبال|nepal|непал|尼泊尔|尼泊爾|नेपाल
Netherlands|هولندا|hollanda|нидерланд|荷兰|荷蘭|नीदरलैंड
New Zealand|نيوزيلندا|yeni zelanda|новой зеланди|新西兰|紐西蘭|न्यूज़ीलैंड
Nicaragua|نيكاراغوا|nikaragua|никарагуа|尼加拉瓜||निकारागुआ
Nigeria|نيجيريا|nijerya|нигери|尼日利亚|奈及利亞|नाइजीरिया
Norway|النرويج|norvec|норвеги|挪威||नॉर्वे
Oman|سلطنة عمان|umman|оман|阿曼||ओमान
Pakistan|باكستان|pakistan|пакистан|巴基斯坦||पाकिस्तान
Panama|بنما|panama|панам|巴拿马|巴拿馬|पनामा
Paraguay|باراغواي|paraguay|парагва|巴拉圭||पैराग्वे
Peru|بيرو|peru|перу|秘鲁|秘魯|पेरू
Philippines|الفلبين|filipinler|филиппин|菲律宾|菲律賓|फिलीपींस
Poland|بولندا|polonya|польш|波兰|波蘭|पोलैंड
Portugal|البرتغال|portekiz|португали|葡萄牙||पुर्तगाल
Qatar|قطر|katar|катар|卡塔尔|卡塔爾|कतर
Romania|رومانيا|romanya|румыни|罗马尼亚|羅馬尼亞|रोमानिया
Russia|روسيا|rusya|росси|俄罗斯|俄羅斯|रूस
Saudi Arabia|السعودية|suudi arabistan|саудовск|沙特||सऊदी अरब
Senegal|السنغال|senegal|сенегал|塞内加尔|塞內加爾|सेनेगल
Serbia|صربيا|sirbistan|серби|塞尔维亚|塞爾維亞|सर्बिया
Singapore|سنغافورة|singapur|сингапур|新加坡||सिंगापुर
South Africa|جنوب أفريقيا|guney afrika|южн\w+ африк|南非||दक्षिण अफ्रीका
South Korea|كوريا الجنوبية|guney kore|южн\w+ коре|韩国|南韓|दक्षिण कोरिया
Spain|إسبانيا|ispanya|испани|西班牙||स्पेन
Sri Lanka|سريلانكا|sri lanka|шри-ланк|斯里兰卡|斯里蘭卡|श्रीलंका
Sudan|السودان|sudan|судан|苏丹|蘇丹|सूडान
Sweden|السويد|isvec|швеци|瑞典||स्वीडन
Switzerland|سويسرا|isvicre|швейцари|瑞士||स्विट्ज़रलैंड
Syria|سوريا|suriye|сири|叙利亚|敘利亞|सीरिया
Taiwan|تايوان|tayvan|тайван|台湾|台灣|ताइवान
Tajikistan|طاجيكستان|tacikistan|таджикистан|塔吉克斯坦||ताजिकिस्तान
Tanzania|تنزانيا|tanzanya|танзани|坦桑尼亚|坦尚尼亞|तंजानिया
Thailand|تايلاند|tayland|таиланд|泰国|泰國|थाईलैंड
Tunisia|تونس|tunus|тунис|突尼斯||ट्यूनीशिया
Turkey|تركيا|turkiye|турци|土耳其||तुर्की
Turkmenistan|تركمانستان|turkmenistan|туркменистан|土库曼斯坦|土庫曼|तुर्कमेनिस्तान
Uganda|أوغندا|uganda|уганд|乌干达|烏干達|युगांडा
Ukraine|أوكرانيا|ukrayna|украин|乌克兰|烏克蘭|यूक्रेन
United Arab Emirates|الإمارات|birlesik arap emirlikleri|оаэ|阿联酋|阿聯酋|संयुक्त अरब अमीरात
United Kingdom|بريطانيا|ingiltere|великобритани|英国|英國|ब्रिटेन
United States|الولايات المتحدة|amerika birlesik devletleri|сша|美国|美國|अमेरिका
Uruguay|أوروغواي|uruguay|уругва|乌拉圭|烏拉圭|उरुग्वे
Uzbekistan|أوزبكستان|ozbekistan|узбекистан|乌兹别克斯坦|烏茲別克|उज़्बेकिस्तान
Venezuela|فنزويلا|venezuela|венесуэл|委内瑞拉|委內瑞拉|वेनेज़ुएला
Vietnam|فيتنام|vietnam|вьетнам|越南||वियतनाम
Yemen|اليمن|yemen|йемен|也门|葉門|यमन
Zambia|زامبيا|zambiya|замби|赞比亚|尚比亞|ज़ाम्बिया
Zimbabwe|زيمبابوي|zimbabve|зимбабве|津巴布韦|辛巴威|जिम्बाब्वे
"""
# extra names for the same country (each line: English name | alias | alias ...)
COUNTRY_MORE = r"""
Hong Kong|هونج كونج|香港特区
Ivory Coast|كوت ديفوار|côte d'ivoire
Iraq|العراق
Myanmar|بورما
United Kingdom|المملكة المتحدة|uk|britanya|соединенн\w+ королевств
United States|أمريكا|abd|америк|соединенные штаты
United Arab Emirates|بأبوظبي|bae|эмират
Dominican Republic|جمهورية الدومينيكان
South Africa|جنوب افريقيا
Czech Republic|جمهورية التشيك|cekya cumhuriyeti|чехия
Taiwan|臺灣
Turkey|türkiye|turkey
Guinea|غينيا كوناكري
Guinea-Bissau|غينيا بيساو|gine bisau|гвине-бисау|几内亚比绍|幾內亞比索
Equatorial Guinea|غينيا الاستوائية|ekvator ginesi|экваториальн\w+ гвине|赤道几内亚|赤道幾內亞
China|Trung Quốc
Hong Kong|Hồng Kông
Taiwan|Đài Loan
Thailand|Thái Lan
Laos|Lào
Cambodia|Campuchia
Japan|Nhật Bản
South Korea|Hàn Quốc
India|Ấn Độ
South Africa|Nam Phi
United States|Hoa Kỳ
United Kingdom|Vương quốc Anh
France|Pháp
Germany|Đức
Netherlands|Hà Lan
Spain|Tây Ban Nha
Portugal|Bồ Đào Nha
Poland|Ba Lan
Turkey|Thổ Nhĩ Kỳ
Egypt|Ai Cập
Ivory Coast|Bờ Biển Ngà
"""

# ---- places (ports, airports, hubs) in other scripts: (display name as used in the gazetteer, country, [aliases])
PLACES = [
    ("Dubai", "United Arab Emirates", ["dubai", "دبي", "дубай", "迪拜", "杜拜", "दुबई"]),
    ("Abu Dhabi", "United Arab Emirates", ["ابو ظبي", "أبوظبي", "абу-даби", "阿布扎比", "अबू धाबी"]),
    ("Istanbul", "Turkey", ["istanbul", "اسطنبول", "إسطنبول", "стамбул", "伊斯坦布尔", "伊斯坦堡", "इस्तांबुल"]),
    ("Doha", "Qatar", ["doha", "الدوحة", "доха", "多哈", "दोहा"]),
    ("Cairo", "Egypt", ["القاهرة", "каир", "开罗", "開羅", "काहिरा"]),
    ("Riyadh", "Saudi Arabia", ["الرياض", "эр-рияд", "利雅得", "रियाद"]),
    ("Jeddah", "Saudi Arabia", ["جدة", "джидда", "吉达", "जेद्दा"]),
    ("Beirut", "Lebanon", ["بيروت", "бейрут", "贝鲁特", "貝魯特", "बेरूत"]),
    ("Baghdad", "Iraq", ["بغداد", "багдад", "巴格达", "巴格達", "बगदाद"]),
    ("Tehran", "Iran", ["طهران", "тегеран", "德黑兰", "德黑蘭", "तेहरान"]),
    ("Karachi", "Pakistan", ["كراتشي", "карачи", "卡拉奇", "कराची"]),
    ("Delhi", "India", ["دلهي", "دلهى", "дели", "德里", "新德里", "दिल्ली"]),
    ("Mumbai", "India", ["مومباي", "мумбаи", "孟买", "孟買", "मुंबई", "मुम्बई"]),
    ("Moscow", "Russia", ["موسكو", "москв", "莫斯科", "मास्को"]),
    ("Beijing", "China", ["بكين", "пекин", "北京", "बीजिंग"]),
    ("Shanghai", "China", ["شنغهاي", "шанхай", "上海", "शंघाई"]),
    ("Guangzhou", "China", ["غوانغتشو", "гуанчжоу", "广州", "廣州", "ग्वांगझू"]),
    ("Kabul", "Afghanistan", ["كابول", "кабул", "喀布尔", "喀布爾", "काबुल"]),
    ("Ankara", "Turkey", ["انقرة", "анкара", "安卡拉", "अंकारा"]),
    ("Aqaba", "Jordan", ["العقبة", "акаба", "亚喀巴", "亞喀巴"]),
    ("Latakia", "Syria", ["اللاذقية", "латакия", "拉塔基亚", "拉塔基亞"]),
    ("Mersin", "Turkey", ["mersin", "мерсин", "梅尔辛"]),
    ("Tel Aviv", "Israel", ["تل ابيب", "тель-авив", "特拉维夫", "特拉維夫"]),
    ("Bangkok", "Thailand", ["بانكوك", "бангкок", "曼谷", "बैंकॉक"]),
    ("Hong Kong airport", "Hong Kong", ["مطار هونغ كونغ", "аэропорт гонконга", "香港国际机场", "香港國際機場", "赤鱲角"]),
    ("Hamburg", "Germany", ["hamburg", "гамбург", "汉堡", "漢堡", "हैम्बर्ग", "هامبورغ"]),
    ("Rotterdam", "Netherlands", ["rotterdam", "роттердам", "鹿特丹", "روتردام"]),
    ("Antwerp", "Belgium", ["antwerp", "антверпен", "安特卫普", "安特衛普", "أنتويرب"]),
    ("Saint Petersburg", "Russia", ["saint petersburg", "st petersburg", "st. petersburg", "санкт-петербург", "петербург", "圣彼得堡", "聖彼得堡"]),
    ("Novorossiysk", "Russia", ["novorossiysk", "новороссийск", "新罗西斯克"]),
    ("Vladivostok", "Russia", ["vladivostok", "владивосток", "符拉迪沃斯托克", "海参崴"]),
    ("Odesa", "Ukraine", ["odesa", "odessa", "одесс", "敖德萨", "敖德薩"]),
    ("Sheremetyevo airport", "Russia", ["sheremetyevo", "шереметьев", "谢列梅捷沃"]),
    ("Domodedovo airport", "Russia", ["domodedovo", "домодедов"]),
    ("Almaty", "Kazakhstan", ["almaty", "алмат", "阿拉木图"]),
    ("Tashkent", "Uzbekistan", ["tashkent", "ташкент", "塔什干"]),
    # Vietnamese ports and airports (written without accents, as the text is normalised)
    ("Cat Lai", "Vietnam", ["cat lai"]),
    ("Cai Mep", "Vietnam", ["cai mep"]),
    ("Da Nang", "Vietnam", ["da nang", "danang"]),
    ("Noi Bai airport", "Vietnam", ["noi bai"]),
    ("Tan Son Nhat airport", "Vietnam", ["tan son nhat"]),
]


for _k, _parts in DRUG_EXTRA.items():
    DRUG_PATTERNS[_k] = _ext(DRUG_PATTERNS[_k], *_parts)
GENERIC_DRUG = _ext(GENERIC_DRUG, *GENERIC_EXTRA)
CONCEAL_EXTRA = {
    "Legitimate cargo (food/produce)": [
        "موز", "فواكه", "فاكهة", "قهوة", "خضروات", "لحوم", "أرز", "muz", "meyve", "kahve", "sebze", "pirinc", "(?<![a-z])balik",
        "банан", "фрукт", "кофе", "овощ", "мороженн", "香蕉", "水果", "咖啡", "冷冻", "冷凍", "蔬菜", "大米", "केला", "फल", "कॉफी", "मछली", "सब्जी", "चावल"],
    "Legitimate cargo (industrial/goods)": [
        "خشب", "أثاث", "اثاث", "آلات", "ملابس", "ألعاب", "إلكترونيات", "خردة", "kereste", "mobilya", "makine", "tekstil", "hurda", "oyuncak",
        "elektronik", "древесин", "мебел", "оборудован", "станк", "одежд", "игрушк", "металлолом", "木材", "家具", "机械", "機械", "服装",
        "玩具", "废金属", "廢金屬", "फर्नीचर", "मशीन", "खिलौने", "लकडी", "कपडे"],
    "Body concealment": ["ابتلاع", "كبسولات", "yutmus", "проглоти", "吞食", "निगल"],
    "Luggage / passenger goods": ["حقيبة", "حقائب", "امتعة", "أمتعة", "bavul", "valiz", "чемодан", "багаж", "行李", "手提箱", "सूटकेस"],
    "Postal / parcel": ["طرد", "طرود", "(?<![a-z])kargo", "(?<![a-z])posta", "посылк", "почтов", "包裹", "邮包", "郵包", "पार्सल"],
    "Container structure / false compartment": ["جدار الحاوية", "قاع مزدوج", "çift taban", "cift taban", "двойн\\w+ дн", "夹层", "夾層", "暗格"],
}
for _k, _parts in CONCEAL_EXTRA.items():
    CONCEALMENT[_k] = _ext(CONCEALMENT[_k], *_parts)
SEIZURE = _ext(SEIZURE, *SEIZURE_EXTRA)
CONTAINER = _ext(CONTAINER, *CONTAINER_EXTRA)
TRANSPORT["Sea - container/cargo"] = _ext(TRANSPORT["Sea - container/cargo"], *PORT_WORDS)
TRANSPORT["Air"] = _ext(TRANSPORT["Air"], *AIR_WORDS)
TRANSPORT["Road"] = _ext(TRANSPORT["Road"], *ROAD_WORDS)
ANY_DRUG = re.compile("|".join(p.pattern for p in list(DRUG_PATTERNS.values()) + [GENERIC_DRUG]), re.I)

# ---- chemicals in Arabic, Turkish, Russian, Chinese, Hindi and Vietnamese
CHEMICAL_EXTRA = {
    "Ozone-depleting refrigerants": [
        "غاز التبريد", "غازات التبريد", "فريون", "مستنفدة للأوزون", "مستنفدة لطبقة الأوزون",
        "soğutucu gaz", "freon", "ozon tabakasını incelten",
        "хладагент", "фреон", "озоноразрушающ",
        "制冷剂", "製冷劑", "冷媒", "氟利昂", "氟氯烃", "氟氯烴", "氢氟碳化物", "氫氟碳化物", "消耗臭氧层", "消耗臭氧層",
        "रेफ्रिजरेंट", "फ्रीऑन", "ओजोन क्षयकारी",
        r"\bgas\s+lạnh\b", "môi chất lạnh", "chất làm lạnh", "suy giảm tầng ô-dôn", "suy giảm tầng ozon"],
    "Pesticides/agrochemicals": [
        "مبيدات", "مبيد حشري", "مبيدات حشرية", "مبيدات زراعية",
        "tarım ilacı", "tarım ilaçları", "pestisit", "böcek ilacı",
        "пестицид", "ядохимикат", "гербицид",
        "农药", "農藥", "杀虫剂", "殺蟲劑", "除草剂", "除草劑",
        "कीटनाशक", "खरपतवारनाशी",
        "thuốc bảo vệ thực vật", "thuốc trừ sâu", "thuốc diệt cỏ"],
    # Hindi पारा also means "temperature" in weather news, so Hindi mercury is left out
    "Mercury": [
        "زئبق", "الزئبق", "cıva", "ртут", "水银", "水銀", "金属汞", "汞", "thủy ngân", "thuỷ ngân"],
    "Explosive precursors": [
        "نترات الأمونيوم", "نترات الامونيوم", "amonyum nitrat", r"аммиачн\w*\s+селитр", "нитрат аммония",
        "硝酸铵", "硝酸銨", "अमोनियम नाइट्रेट", "amoni nitrat", "nitrat amoni"],
    "Hazardous/toxic waste": [
        "نفايات خطرة", "نفايات سامة", "tehlikeli atık", "zehirli atık", r"опасн\w+\s+отход", r"токсичн\w+\s+отход",
        "危险废物", "危險廢物", "洋垃圾", "固体废物", "固體廢物", "खतरनाक कचरा", "ई-कचरा", "chất thải nguy hại"],
    "Industrial/toxic chemicals": [
        "حمض الكبريتيك", "sülfürik asit", r"серн\w+\s+кислот", "硫酸(?![铵銨])", "氰化物",
        "सल्फ्यूरिक एसिड", "axit sunfuric"],
}
GENERIC_CHEMICAL_EXTRA = [
    "مواد كيميائية", "مواد كيماوية", "كيماويات", "كيميائيات",
    "kimyasal madde", "kimyasal",
    r"химическ\w+\s+веществ", "химикат",
    "化学品", "化學品", "化工原料",
    "रसायन", "केमिकल",
    "hóa chất", "hoá chất"]
# drug-making chemicals stay "Precursor chemical" in every language
GENERIC_PRECURSOR_EXTRA = [
    "سلائف كيميائية", "السلائف", "مواد أولية لتصنيع المخدرات", "uyuşturucu öncül", "öncül kimyasal",
    "прекурсор", "易制毒化学品", "易制毒化學品", "制毒原料", "製毒原料", "प्रीकर्सर", "tiền chất"]
for _k, _parts in CHEMICAL_EXTRA.items():
    CHEMICAL_PATTERNS[_k] = _ext(CHEMICAL_PATTERNS[_k], *_parts)
GENERIC_CHEMICAL = _ext(GENERIC_CHEMICAL, *GENERIC_CHEMICAL_EXTRA)
GENERIC_PRECURSOR = _ext(GENERIC_PRECURSOR, *GENERIC_PRECURSOR_EXTRA)

# Rebuild the combined headline gate AFTER every language has been added. It is first built near the top of
# this file from the English-only lists, which silently dropped Arabic, Russian and Chinese headlines (and
# most Hindi and Turkish ones) before download.
ANY_PRECURSOR = re.compile("|".join(p.pattern for p in list(PRECURSOR_PATTERNS.values()) + [GENERIC_PRECURSOR]), re.I)
ANY_CHEMICAL = re.compile("|".join(p.pattern for p in list(CHEMICAL_PATTERNS.values()) + [GENERIC_CHEMICAL]), re.I)
ANY_CONTRABAND = re.compile("|".join([ANY_DRUG.pattern, ANY_PRECURSOR.pattern, ANY_CHEMICAL.pattern, ANY_TIMBER.pattern,
                                      ANY_ARMS.pattern, ANY_IVORY.pattern, ANY_FAUNA.pattern]), re.I)


# "from X", "to X", "via X" in the new languages
def _cue_ext(old, extra):
    return _cue(old.pattern[3:-(len(_TAIL) + 1)] + "|" + extra)


ORIGIN_CUE = _cue_ext(ORIGIN_CUE, r"قادم[ةا]?\s+من|واردة\s+من|(?<![\u0600-\u06ff])من|(?<![\u0430-\u044f])из(?:-за)?|"
                                  r"прибывш\w+\s+из|вывезенн\w+\s+из|来自|來自|从|從|自")
DEST_CUE = _cue_ext(DEST_CUE, r"متجه[ةا]?\s+(?:إلى|الى)|في\s+طريقها\s+(?:إلى|الى)|المرسل[ةا]\s+(?:إلى|الى)|"
                              r"в\s+направлении|направлявш\w+\s+в|следовавш\w+\s+в|для\s+отправки\s+в|предназначавш\w+\s+для|"
                              r"运往|運往|前往|发往|發往|运抵|運抵|销往|銷往")
TRANSIT_CUE = _cue_ext(TRANSIT_CUE, r"(?<![\u0600-\u06ff])عبر|(?<![\u0430-\u044f])через|途经|途經|经由|經由|经过|經過|转运|轉運|取道")
TO_CUE = _cue_ext(TO_CUE, r"(?<![\u0600-\u06ff])(?:إلى|الى)|(?<![\u0430-\u044f])в|到|至")
# Vietnamese: "từ X" (from), "sang X" / "đến X" (to), "qua X" (via)
ORIGIN_CUE = _cue_ext(ORIGIN_CUE, r"(?<![a-z])tu(?![a-z])|xuat\s+phat\s+tu|nhap\s+(?:lau\s+)?tu")
DEST_CUE = _cue_ext(DEST_CUE, r"(?<![a-z])sang(?![a-z])|(?<![a-z])\u0111en(?![a-z])|xuat\s+sang|van\s+chuyen\s+sang")
TRANSIT_CUE = _cue_ext(TRANSIT_CUE, r"(?<![a-z])qua(?![a-z])|thong\s+qua|trung\s+chuyen\s+(?:qua|tai)")
TO_CUE = _cue_ext(TO_CUE, r"(?<![a-z])(?:sang|\u0111en)(?![a-z])")
# suffixes that come AFTER the country: Turkish 'dan / 'e, Hindi "se" (from) / "tak" (to)
POST_ORIGIN = re.compile(r"^(?:'(?:dan|den|tan|ten)(?![a-z])|\s*से(?![\u0900-\u097f]))")
POST_DEST = re.compile(r"^(?:'(?:ya|ye|na|ne|a|e)(?![a-z])|\s*(?:तक|के\s+लिए)(?![\u0900-\u097f]))")

# countries in other languages (Russian names need case endings, so they are matched as stems)
_RU_STEMS = []            # (stem regex, English name)


def _add_country(eng, alias):
    alias = _bs(alias).strip()
    if not alias:
        return
    if re.search(r"[\u0400-\u04ff]", alias):
        _RU_STEMS.append((norm(alias).replace("\\w+", "[\u0430-\u044f]+"), eng))
    else:
        COUNTRY_ALIAS[norm(alias)] = eng


for _line in COUNTRIES.strip().splitlines():
    _f = [x.strip() for x in _line.split("|")]
    for _a in _f[1:]:
        _add_country(_f[0], _a)
for _line in COUNTRY_MORE.strip().splitlines():
    _f = [x.strip() for x in _line.split("|")]
    for _a in _f[1:]:
        _add_country(_f[0], _a)
# ---- states, provinces and big cities that local news names instead of the country (country-level pin).
# Ambiguous names are left out on purpose: Para / Natal / Salvador (common words or another country),
# Van / Batman / Ordu, Punjab and Hyderabad in English (India or Pakistan), Georgia.
REGIONS = [
    # Brazil
    ("Alagoas", "Brazil", ["alagoas"]), ("Manaus", "Brazil", ["manaus"]),
    ("Bahia", "Brazil", ["bahia"]), ("Ceara", "Brazil", ["ceara", "fortaleza"]),
    ("Espirito Santo", "Brazil", ["espirito santo", "vila velha"]), ("Goias", "Brazil", ["goias", "goiania"]),
    ("Maranhao", "Brazil", ["maranhao", "sao luis"]), ("Mato Grosso", "Brazil", ["mato grosso", "cuiaba"]),
    ("Mato Grosso do Sul", "Brazil", ["mato grosso do sul", "campo grande", "ponta pora", "corumba", "dourados"]),
    ("Minas Gerais", "Brazil", ["minas gerais", "belo horizonte", "uberlandia", "juiz de fora"]),
    ("Paraiba", "Brazil", ["paraiba", "joao pessoa"]), ("Parana", "Brazil", ["parana", "curitiba", "foz do iguacu", "londrina", "maringa"]),
    ("Pernambuco", "Brazil", ["pernambuco", "recife"]), ("Piaui", "Brazil", ["piaui", "teresina"]),
    ("Rio Grande do Norte", "Brazil", ["rio grande do norte"]), ("Rio Grande do Sul", "Brazil", ["rio grande do sul", "porto alegre", "caxias do sul"]),
    ("Rondonia", "Brazil", ["rondonia", "porto velho"]), ("Roraima", "Brazil", ["roraima"]),
    ("Santa Catarina", "Brazil", ["santa catarina", "florianopolis", "itajai", "joinville", "navegantes"]),
    ("Sergipe", "Brazil", ["sergipe", "aracaju"]), ("Tocantins", "Brazil", ["tocantins"]),
    ("Sao Paulo state", "Brazil", ["campinas", "guarulhos", "ribeirao preto", "sorocaba", "sao jose dos campos"]),
    # India (English and Hindi)
    ("Madhya Pradesh", "India", ["madhya pradesh", "bhopal", "indore", "jabalpur", "gwalior", "मध्य प्रदेश", "मध्यप्रदेश", "भोपाल", "इंदौर", "जबलपुर", "ग्वालियर"]),
    ("Uttar Pradesh", "India", ["lucknow", "kanpur", "varanasi", "agra", "meerut", "gorakhpur", "prayagraj", "ghaziabad", "noida",
                                "उत्तर प्रदेश", "यूपी", "लखनऊ", "कानपुर", "वाराणसी", "आगरा", "मेरठ", "गोरखपुर", "प्रयागराज", "गाजियाबाद", "नोएडा"]),
    ("Rajasthan", "India", ["rajasthan", "jaipur", "jodhpur", "udaipur", "bikaner", "barmer", "राजस्थान", "जयपुर", "जोधपुर", "उदयपुर", "बीकानेर", "बाड़मेर"]),
    ("Bihar", "India", ["bihar", "patna", "बिहार", "पटना"]),
    ("Jharkhand", "India", ["jharkhand", "ranchi", "dhanbad", "झारखंड", "रांची", "धनबाद"]),
    ("Chhattisgarh", "India", ["chhattisgarh", "raipur", "छत्तीसगढ़", "रायपुर"]),
    ("Odisha", "India", ["odisha", "bhubaneswar", "ओडिशा", "भुवनेश्वर"]),
    ("West Bengal", "India", ["west bengal", "siliguri", "पश्चिम बंगाल", "सिलीगुड़ी"]),
    ("Assam", "India", ["assam", "guwahati", "असम", "गुवाहाटी"]), ("Manipur", "India", ["manipur", "imphal", "मणिपुर"]),
    ("Mizoram", "India", ["mizoram", "aizawl", "मिजोरम"]), ("Tripura", "India", ["tripura", "agartala", "त्रिपुरा"]),
    ("Gujarat", "India", ["gujarat", "ahmedabad", "surat", "vadodara", "kutch", "गुजरात", "अहमदाबाद", "कच्छ"]),
    ("Maharashtra", "India", ["maharashtra", "pune", "nagpur", "thane", "nashik", "महाराष्ट्र", "पुणे", "नागपुर", "ठाणे"]),
    ("Karnataka", "India", ["karnataka", "bengaluru", "bangalore", "mangaluru", "कर्नाटक", "बेंगलुरु"]),
    ("Kerala", "India", ["kerala", "kochi", "thiruvananthapuram", "kozhikode", "केरल"]),
    ("Tamil Nadu", "India", ["tamil nadu", "coimbatore", "madurai", "तमिलनाडु"]),
    ("Andhra Pradesh", "India", ["andhra pradesh", "tirupati", "chittoor", "आंध्र प्रदेश"]), ("Telangana", "India", ["telangana", "तेलंगाना"]),
    ("Haryana", "India", ["gurugram", "gurgaon", "faridabad", "kaithal", "sirsa", "panipat", "हरियाणा", "गुरुग्राम", "फरीदाबाद", "कैथल", "सिरसा", "पानीपत"]),
    ("Punjab (India)", "India", ["ludhiana", "amritsar", "jalandhar", "bathinda", "ferozepur", "पंजाब", "लुधियाना", "अमृतसर", "जालंधर", "बठिंडा", "फिरोजपुर"]),
    ("Himachal Pradesh", "India", ["himachal", "shimla", "solan", "baddi", "kullu", "हिमाचल", "शिमला", "सोलन", "बद्दी", "कुल्लू"]),
    ("Uttarakhand", "India", ["uttarakhand", "dehradun", "haridwar", "उत्तराखंड", "देहरादून", "हरिद्वार"]),
    ("Chandigarh", "India", ["chandigarh", "चंडीगढ़"]), ("Jammu and Kashmir", "India", ["jammu", "srinagar", "जम्मू", "श्रीनगर"]),
    ("Delhi", "India", ["दिल्ली"]),
    # Turkey (provinces; Turkish suffixes after an apostrophe are fine)
    ("Kocaeli", "Turkey", ["kocaeli", "gebze"]), ("Antalya", "Turkey", ["antalya", "alanya"]), ("Adana", "Turkey", ["adana"]),
    ("Gaziantep", "Turkey", ["gaziantep"]), ("Sanliurfa", "Turkey", ["şanlıurfa", "sanliurfa", "urfa"]), ("Hatay", "Turkey", ["hatay", "iskenderun"]),
    ("Mardin", "Turkey", ["mardin"]), ("Diyarbakir", "Turkey", ["diyarbakır", "diyarbakir"]), ("Hakkari", "Turkey", ["hakkari", "yüksekova"]),
    ("Sirnak", "Turkey", ["şırnak", "sirnak", "habur"]), ("Konya", "Turkey", ["konya"]), ("Bursa", "Turkey", ["bursa"]), ("Ankara", "Turkey", ["ankara"]),
    ("Edirne", "Turkey", ["edirne", "ipsala", "kapıkule", "kapikule"]), ("Tekirdag", "Turkey", ["tekirdağ", "tekirdag"]),
    ("Kirklareli", "Turkey", ["kırklareli", "kirklareli"]), ("Samsun", "Turkey", ["samsun"]), ("Trabzon", "Turkey", ["trabzon"]),
    ("Erzurum", "Turkey", ["erzurum"]), ("Agri", "Turkey", ["doğubayazıt", "dogubayazit"]), ("Kayseri", "Turkey", ["kayseri"]),
    ("Eskisehir", "Turkey", ["eskişehir", "eskisehir"]), ("Manisa", "Turkey", ["manisa"]), 
    ("Mugla", "Turkey", ["muğla", "bodrum", "marmaris"]), ("Denizli", "Turkey", ["denizli"]), ("Malatya", "Turkey", ["malatya"]),
    ("Elazig", "Turkey", ["elazığ", "elazig"]), ("Sakarya", "Turkey", ["sakarya"]), ("Balikesir", "Turkey", ["balıkesir", "balikesir"]),
    ("Canakkale", "Turkey", ["çanakkale", "canakkale"]), ("Kahramanmaras", "Turkey", ["kahramanmaraş", "kahramanmaras"]),
    ("Osmaniye", "Turkey", ["osmaniye"]), ("Adiyaman", "Turkey", ["adıyaman", "adiyaman"]), ("Izmir", "Turkey", ["izmir", "i̇zmir"]),
    # Egypt and Saudi Arabia (Arabic; a leading preposition such as ب / و / ل is fine)
    ("Sohag", "Egypt", ["سوهاج"]), ("Assiut", "Egypt", ["أسيوط", "اسيوط"]), ("Minya", "Egypt", ["المنيا"]), ("Qena", "Egypt", ["قنا"]),
    ("Luxor", "Egypt", ["الأقصر", "الاقصر"]), ("Aswan", "Egypt", ["أسوان", "اسوان"]), ("Giza", "Egypt", ["الجيزة"]),
    ("Qalyubia", "Egypt", ["القليوبية"]),  ("Dakahlia", "Egypt", ["الدقهلية"]), ("Tanta", "Egypt", ["طنطا"]),
    ("Monufia", "Egypt", ["المنوفية"]),  ("Kafr El Sheikh", "Egypt", ["كفر الشيخ"]), ("Damietta", "Egypt", ["دمياط"]),
    ("Port Said", "Egypt", ["بورسعيد", "بور سعيد"]), ("Ismailia", "Egypt", ["الإسماعيلية", "الاسماعيلية"]), ("Suez", "Egypt", ["السويس"]),
    ("Faiyum", "Egypt", ["الفيوم"]), ("Beni Suef", "Egypt", ["بني سويف"]), ("Matrouh", "Egypt", ["مرسى مطروح"]), ("Sinai", "Egypt", ["سيناء"]),
    ("Alexandria", "Egypt", ["الإسكندرية", "الاسكندرية"]),
    ("Jazan", "Saudi Arabia", ["جازان", "جيزان"]), ("Najran", "Saudi Arabia", ["نجران"]), ("Asir", "Saudi Arabia", ["أبها", "منطقة عسير"]),
    ("Tabuk", "Saudi Arabia", ["تبوك"]), ("Qassim", "Saudi Arabia", ["القصيم"]), ("Al Jawf", "Saudi Arabia", ["الجوف"]),
     ("Mecca", "Saudi Arabia", ["مكة المكرمة"]), ("Dammam", "Saudi Arabia", ["الدمام"]),
    # Russia (Cyrillic stems get case endings automatically)
    ("Krasnoyarsk", "Russia", ["краснояр"]), ("Novosibirsk", "Russia", ["новосибирск"]), ("Yekaterinburg", "Russia", ["екатеринбург"]),
    ("Samara", "Russia", ["самарск", "самар"]), ("Rostov", "Russia", ["ростов"]), ("Krasnodar", "Russia", ["краснодар", "кубан"]),
    ("Nizhny Novgorod", "Russia", ["нижегород"]), ("Kazan", "Russia", ["казан", "татарстан"]), ("Ufa", "Russia", ["башкир"]),
    ("Chelyabinsk", "Russia", ["челябинск"]), ("Omsk", "Russia", ["омск"]), ("Perm", "Russia", ["пермск"]), ("Volgograd", "Russia", ["волгоград"]),
    ("Voronezh", "Russia", ["воронеж"]), ("Irkutsk", "Russia", ["иркутск"]), ("Khabarovsk", "Russia", ["хабаровск"]), ("Primorye", "Russia", ["примор"]),
    ("Kaliningrad", "Russia", ["калининград"]), ("Kursk", "Russia", ["курск"]), ("Belgorod", "Russia", ["белгород"]), ("Bryansk", "Russia", ["брянск"]),
    ("Dagestan", "Russia", ["дагестан", "махачкал"]), ("Tyumen", "Russia", ["тюмен"]), ("Saratov", "Russia", ["саратов"]), ("Stavropol", "Russia", ["ставропол"]),
    ("Kemerovo", "Russia", ["кемеров", "кузбасс"]), ("Altai", "Russia", ["барнаул", "алтайск"]), ("Tomsk", "Russia", ["томск"]),
    ("Moscow region", "Russia", ["подмосков"]), ("Orenburg", "Russia", ["оренбург"]), ("Astrakhan", "Russia", ["астрахан"]),
]
PLACES += REGIONS
for _disp, _ctry, _als in PLACES:
    for _a in _als:
        PLACE_ALIAS[norm(_a)] = (_disp, _ctry)

# Russian place names inflect too, so they are matched as stems as well
_RU_PLACES = []
for _k in [k for k in PLACE_ALIAS if re.search(r"[\u0400-\u04ff]", k)]:
    _RU_PLACES.append((_k, PLACE_ALIAS.pop(_k)))
_RU_PLACES.sort(key=lambda x: len(x[0]), reverse=True)
PLACE_RX_RU = re.compile("|".join("(?P<p%d>(?<![\u0430-\u044f])%s[\u0430-\u044f]{0,4}(?![\u0430-\u044f]))" % (i, re.escape(k))
                                  for i, (k, _) in enumerate(_RU_PLACES)))


def ru_place(m):
    """(display, country) for a match of PLACE_RX_RU."""
    return _RU_PLACES[int(m.lastgroup[1:])][1]


_RU_STEMS.sort(key=lambda x: len(x[0]), reverse=True)
COUNTRY_RX_RU = re.compile("|".join("(?P<c%d>(?<![\u0430-\u044f])%s[\u0430-\u044f]{0,4}(?![\u0430-\u044f]))" % (i, st)
                                    for i, (st, _) in enumerate(_RU_STEMS)))


def ru_country(m):
    """Country for a match of COUNTRY_RX_RU."""
    return _RU_STEMS[int(m.lastgroup[1:])][1]


def _alt(keys):
    return "|".join(re.escape(k) for k in sorted(keys, key=len, reverse=True))


COUNTRY_RX = re.compile(r"(?<![a-z])(" + _alt(COUNTRY_ALIAS) + r")(?![a-z\u0600-\u06ff\u0900-\u097f])")
PLACE_RX = re.compile(r"(?<![a-z])(" + _alt(PLACE_ALIAS) + r")(?![a-z\u0600-\u06ff\u0900-\u097f])")
