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
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def norm(s):
    return strip_accents((s or "").replace("\u2019", "'")).lower()


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
             r"\bepisode\b", r"video\s+game", r"\bseason\s+\d")

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
    ("Ho Chi Minh City", "Vietnam", ["ho chi minh"]),
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
    ('Hanoi', 'Vietnam', ['hanoi']),
    ('Phnom Penh', 'Cambodia', ['phnom penh']),
    ('Vientiane', 'Laos', ['vientiane']),
    ('Cebu', 'Philippines', ['cebu']),
    ('Davao', 'Philippines', ['davao']),
    ('Zamboanga', 'Philippines', ['zamboanga']),
    ('Mindanao', 'Philippines', ['mindanao']),
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
PLACE_ALIAS = {}
for _disp, _ctry, _als in _PLACES:
    for _a in _als:
        PLACE_ALIAS[norm(_a)] = (_disp, _ctry)


def _alt(keys):
    return "|".join(re.escape(k) for k in sorted(keys, key=len, reverse=True))


COUNTRY_RX = re.compile(r"(?<![a-z])(" + _alt(COUNTRY_ALIAS) + r")(?![a-z])")
PLACE_RX = re.compile(r"(?<![a-z])(" + _alt(PLACE_ALIAS) + r")(?![a-z])")
