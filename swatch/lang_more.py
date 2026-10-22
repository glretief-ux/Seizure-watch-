# -*- coding: utf-8 -*-
"""Word lists for nine more languages: German (Austria focus), Danish, Estonian, Amharic, Icelandic,
Mongolian, Norwegian, Slovak and Swedish.

This module holds DATA ONLY. lexicon.py merges it at the same points where the Dutch additions are merged,
so the matching code is the same for every language. Every pattern is passed through lexicon.strip_accents
before use, so write words with their normal accents (a, o, u with umlauts or rings, Slovak and Icelandic
accents). Three letters are NOT removed by that step and must be written as they are: o-slash, ae-ligature,
eth and thorn (Danish, Norwegian, Icelandic), plus the German sharp s.

Coverage notes
  * German, Danish, Norwegian, Swedish: good. Estonian, Slovak, Icelandic: good for the common words, names are
    expanded into their inflected forms (see expand_* below). Mongolian and Amharic: basic - the common drug,
    seizure and place words only; a native speaker should extend them (see README).
  * Words that are also common in English or another supported language are deliberately left out
    ("island" for Iceland, bare "Herman"-type first names, "chat"/khat, which is legal in Ethiopia).
"""
import re
import unicodedata


def _strip(s):
    s = s.replace("ı", "i")
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def norm(s):
    return _strip((s or "").replace("’", "'")).lower()


# ---------------------------------------------------------------------------------------------- drug words
DRUG = {
    "Cocaine": [
        "kokaiin", "kokain", "ኮኬይን", "ኮካይን", "ኮኬን",
    ],
    "Cannabis": [
        r"\bhasch", r"\bhasj", r"\bhasis", r"kanep", r"marihuaana", r"\bkonope", r"\bhanf(?:plant|anbau|feld)",
        r"cannabisplant", "kannabis", "ሃሺሽ", "ሀሺሽ", "ሐሺሽ", "ካናቢስ", "ማሪዋና", "ማሪጁዋና",
    ],
    "Heroin/Opium": [
        "heroiin", "opiaat", "опиум", "ሄሮይን", "ሄሮዊን", "ሄሮየን", "opiat",
    ],
    "Methamphetamine": [
        "methamphetamin", "metamfetamiin", r"\bpervitin", "crystal-?meth", "ሜታምፌታሚን",
    ],
    "NSA": [
        r"(?<!meth)(?<!metham)amphetamin(?!e)", "amfetamiin", "ekstaas", r"\bextaz", r"synthetische\s+drogen", r"designerdrogen", r"partydrogen",
        r"syntetiske\s+(?:stoffer|narkotika|rusmidler)", r"syntetiska\s+droger", r"sunteetilised\s+narkootikumid",
        r"syntetick\w+\s+(?:drog|latk)\w*", r"tilbuin\w*\s+(?:fikniefni|efni)",
        "ኤክስታሲ", "ትራማዶል", "አምፌታሚን",
    ],
    "Cigarettes": [
        "zigarett", "cigarett", "cigaret", "sigarett", "sigaret", r"\btobak", r"\btabak", "cigariet",
        r"(?<!хар )тамхи", "тамхины", "ሲጋራ", "ትምባሆ",
    ],
}
GENERIC = [
    # German (Austria says Suchtgift)
    "suchtgift", "rauschgift", "suchtmittel", r"betaubungsmittel", r"\bdrogen\b", r"drogen(?:fund|schmuggel|handel|lager|labor|ring|bande|dealer|razzia|kurier)\w*",
    # Danish / Norwegian / Swedish
    "narkotik", "euforiserende", "rusmidl", r"\bknark", r"\bdroger\b", r"narko(?:lab|handel|smugl|fynd)\w*",
    # Estonian
    "narkootik", r"\buimasti", r"narko(?:labor|kaubandus|kurjategij)\w*",
    # Slovak
    r"\bdrog(?:y|a|ach|ami|ou|u|e)\b", r"omamn\w+\s+latk\w*", r"navykov\w+\s+latk\w*",
    # Icelandic
    "fikniefn", "eiturlyf",
    # Mongolian
    "мансуур", r"хар\s+тамхи", "мансууруулах",
    # Amharic
    "አደንዛዥ", "ሱስ አስያዥ", "ናርኮቲክ",
]
SEIZURE = [
    # German
    r"beschlagnahm", r"sichergestellt", r"sicherstell", r"\bstell\w*\s+(?:\S+\s+){0,6}?sicher\b", r"abgefangen", r"\bfang\w*\s+(?:\S+\s+){0,8}?ab\b", r"ausgehoben",
    r"schmuggel", r"geschmuggelt", r"aufgedeckt", r"entdeckt\b", r"(?:drogen|rauschgift|suchtgift|kokain|heroin|cannabis|waffen)fund\b",
    r"aufgegriffen", r"einbehalten", r"festgesetzt", r"\bfindet\b", r"\bfanden?\b", r"gefunden",
    r"(?:festgenommen|verhaftet|erwischt|ertappt)\s+(?:\S+\s+){0,4}?mit\b", r"\b(?:erwischt|ertappt)\b",
    # found / arrested with drugs: Swedish, Danish, Norwegian
    r"hittade\w*", r"hittat\b", r"hittades", r"\bfandt\b", r"\bfant\b", r"funnet\b", r"funnit\b",
    r"(?:anholdt\w*|arresteret|pagrebet|pagrepet|arrestert|gripen|gripna|anhallen|anhallna|haktad\w*)\s+(?:\S+\s+){0,4}?med\b",
    # Danish / Norwegian / Swedish ("beslag" = seizure)
    r"\w*beslag\w*", r"smugl\w*", r"smugg\w*", r"af?sl[oø]r\w*", r"avsloj\w*", r"avdekk\w*", r"avdekt\w*", r"patraff\w*",
    r"opdaget\b", r"fundet\b", r"inndratt", r"inndra\w*", r"konfiskerte?\b", r"konfiskerade", r"beslagtog", r"omhandertog",
    # Estonian
    r"konfiskeer", r"avasta", r"\btaba(?:ti|s|sid)\b", r"salakau\w*", r"kinni\s+peet", r"peeti\s+kinni", r"sissetoomi", r"sisse\s+smugeldat",
    r"aresti(?:ti|s)\b", r"leiti\b", r"leidis\b", r"leidsid\b",
    # Slovak
    r"zaist", r"skonfisk", r"zhab", r"odhal\w+", r"pasov", r"zadrz\w+", r"zachyt\w+", r"nasli\b", r"zaisten", r"\bnasl\w*", r"\bnasiel\b",
    # Icelandic
    r"lagd\w*\s+hald", r"lagði\s+hald", r"haldl[ao]g\w*", r"upptæk\w*", r"upptaek\w*", r"smygl\w*", r"fundust", r"fannst", r"fundu\b", r"handtok\w*\s+(?:\S+\s+){0,4}?me[dð]\b",
    r"afhjup\w+", r"gerd\w*\s+upptaek\w*",
    # Mongolian
    "хураа", "илрүүл", "нэвтрүүл", "саатуул", "таслан зогсоо", "баривчил", "хураагд", "олдлоо", "олджээ",
    # Amharic
    "ተያዘ", "ተያዙ", "ተይዘ", "ተይዟ", "ተይዞ", "ያዘ", "በቁጥጥር ስር", "ኮንትሮባንድ", "ተወረሰ", "ወረሰ", "ተገኘ", "ተጠለፈ", "አገኘ", "ተገኙ",
]
CONTAINER = ["konteiner", "kontajner", r"\bgam(?:ur|ar|i|inn|inum|ana)\b", "чингэлэг", "ኮንቴይነር", "schiffscontainer", "seecontainer"]
PORT = [
    r"(?<!flug)hafen\b", r"(?<!flug)hafen(?:stadt|behorde|gebiet|anlage)", "seehafen", "containerhafen", "frachtschiff", "schiffsfracht",
    r"(?<![a-z])havn", r"(?<![a-z])hamn", "skibsfragt", "godsbat", "lasteskip", "fraktfartyg", "lastfartyg",
    r"(?<![a-z])sadam", "laevafrakt", "kaubalaev",
    r"pristav", r"nakladn\w+\s+lod",
    r"hofn(?:in|ina|inni)?\b", r"hafnar(?:svaed|vorsl|vogur)", "flutningaskip",
    "ወደብ", "መርከብ",
]
AIR = [
    "flughafen", "luftfracht", "flugzeug", "lufthavn", "flygplats", "flyplass", "flyfragt", "lennujaam", "lennuk",
    "letisko", "letisku", "lietadl", r"flugvoll", r"flugvell", r"flugstod", r"flugvel\b", "нисэх онгоцны буудал", "нисэх онгоц",
    "አየር ማረፊያ", "አውሮፕላን",
]
ROAD = [
    r"\blkw\b", "lastwagen", "lastkraftwagen", "autobahn", "grenzubergang", "sattelzug", "reisebus",
    "lastbil", "motorvej", "motorvei", "motorvag", "grænseovergang", "grenseovergang", "gransovergang", "gransen",
    "veoauto", "kaubaauto", "piiripunkt", "maantee", "боомт",
    "kamion", "nakladn\\w+\\s+auto", "dialnic", "hranicn\\w+\\s+priechod",
    "vorubil", "flutningabil", "bifreid", "thjodveg", "þjóðveg",
    "ачааны машин", "автозам", "ጭነት መኪና", "መኪና",
]
# (regex part, kg factor). The literal start before the first backslash decides the factor in extract._kg_factor.
UNITS = [
    (r"kilogramm\w*", 1), (r"kilogram\w*", 1), ("kilo", 1), ("kilos", 1), ("kg", 1), ("kiló", 1),
    (r"tonnen", 1000), (r"tonn\w*", 1000), ("tony", 1000), ("tona", 1000), ("tonu", 1000), ("tonov", 1000),
    (r"gramm\w*", 0.001), (r"gramov", 0.001), (r"gramy", 0.001),
    ("грамм", 0.001), ("ኪሎ\\s*ግራም", 1), ("ኪሎግራም", 1), ("ኪሎ", 1), ("ኪ\\.ግ", 1), ("ኪግ", 1), ("ኩንታል", 100), ("ቶን", 1000), ("ግራም", 0.001),
]

# ------------------------------------------------------------------------------------- concealment / cover load
def _w(*words):
    """Whole-word-start patterns (a short goods word must never match inside a longer, unrelated word)."""
    return [r"\b" + w for w in words]


CONCEAL = {
    "Legitimate cargo (food/produce)": _w(
        "bananen", "ananas", "kaffee", "zucker", "tiefkuhl", "gefrier", "orangen", "fruchtsaft", "fisch", "fleisch", "gemuse", "obst",
        "bananer", "kaffe", "sukker", "frossen", "appelsin", "frugt", "frukt", "fisk", "gronnsaker", "grontsager",
        "bananas", "socker", "fryst", "gronsaker",
        "kohv", "suhkur", "puuvili", "banaan", "kulmutatud",
        "banany", "cukor", "ovocie", "zelenina", "mrazen", "citrus",
        "kaffi", "sykur", "avoxt", "grænmeti", "fiskur", "hrisgrjon",
        "жимс", "хоол хүнс", "загас", "ቡና", "ስኳር", "ፍራፍሬ", "ሩዝ", "ዱቄት"),
    "Legitimate cargo (industrial/goods)": _w(
        "holz\\b", "mobel", "fliesen", "schrott", "kleidung", "spielzeug", "kunststoff", "autoteile", "ersatzteile", "marmor", "textilien",
        "deklariert als", "angegeben als", "getarnt als", "tarnung",
        "møbler", "mobler", "fliser", "legetoj", "klaeder", "klader", "leketoy", "leksaker", "reservedele", "reservdelar", "husgogn",
        "mooblid", "riided", "mänguasjad", "mangu", "varuosad", "nabytok", "obklad", "oblecenie", "hracky", "nahradne diely", "mramor",
        "timbur\\b", "flisar", "leikfong", "varahlutir", "marmari",
        "тавилга", "хувцас", "тоглоом", "эд анги", "እንጨት", "ጨርቃ ጨርቅ", "ልብስ", "የመኪና መለዋወጫ"),
    "Body concealment": _w("verschluckt", "geschluckt", "schlucker", "slugt", "neelatud", "prehltnut", "gleypt"),
    "Luggage / passenger goods": _w("koffer", "rucksack", "reisetasche", "handgepack", "kuffert", "bagasje", "bagage", "kohver", "batoh", "kufor", "ferdataska", "ሻንጣ"),
    "Postal / parcel": _w("postsendung", "postpaket", "paketsendung", "paketdienst", "paketpost", "pakkesendelse", "pakkepost", "zasielk", "baliky", "balikov", "илгээмж", "እሽግ"),
    "Container structure / false compartment": _w(
        "doppelboden", "doppelter boden", "versteck", "geheimfach", "dobbeltbund", "dobbel bunn", "dubbelbotten", "topeltpohi",
        "dvojite dno", "dvojity spodok", "tvofaldur botn", "давхар ёроол", "ድርብ ታች"),
    "Vessel hull / underwater": _w("schiffsrumpf", "unterwasser", "skibsskrog", "skipsskrog", "fartygsskrov", "laevakere", "lodny trup", "skipsskrokkur"),
}
GENERIC_COMPARTMENT = [r"doppelter?\s+boden", "geheimfach", r"versteck\w*", "dobbeltbund", r"dobbel\s+bunn", "dubbelbotten", "topeltpohi", r"dvojit\w+\s+dn", "falsk bund"]

# ------------------------------------------------------------------------------------------------ chemicals
CHEM = {
    "Ozone-depleting refrigerants": ["kaltemittel", "kuhlmittel", "kuhlgas", "fckw", "hfkw", "kolemiddel", "kolegas", "kjolemiddel", "koldmedium", "kulmaaine", "chladiv", "kaelimidill", "kælimiðill"],
    "Pesticides/agrochemicals": ["pestizid", "pflanzenschutzmittel", "insektizid", "pesticider", "sprojtemidler", "sprøjtemidler", "sprøytemidler", "plantevernmidler", "bekampningsmedel", "pestitsiid", "taimekaitse", "pesticid", "meindyraeitur", "skordyraeitur"],
    "Mercury": ["quecksilber", "kviksolv", "kviksølv", "kvikksolv", "kvikksølv", "kvicksilver", "elavhõbe", "elavhobe", r"\bortut\b", "kvikasilfur", "мөнгөн ус", "ሜርኩሪ"],
    "Explosive precursors": ["ammoniumnitrat", "ammooniumnitraat", "dusicnan amonny", "ammoniumnitrat", "kaliumchlorat", "wasserstoffperoxid", "vandperoxid", "hydrogenperoksid"],
    "Hazardous/toxic waste": ["giftmull", "sondermull", "elektroschrott", "mullexport", "farligt affald", "elektronisk affald", "farlig avfall", "farligt avfall", "elavfall", "ohtlikud jaatmed", "ohtlik praht", "nebezpecny odpad", "haettuleg urgangsefni"],
    "Industrial/toxic chemicals": ["schwefelsaure", "salzsaure", "natriumhydroxid", "atznatron", "svovlsyre", "svavelsyra", "vaveldhape", "kaustiline sooda"],
}
GENERIC_CHEMICAL = ["chemikalien", "gefahrliche stoffe", "giftige stoffe", "kemikalier", "kemikaalid", "chemikalie", "kemisk efni", "kemisk\\w*\\s+efni", "ኬሚካል"]
GENERIC_PRECURSOR = [
    "grundstoffe", "drogenvorlaufer", "vorlauferchemikalien", "ausgangsstoffe", "prakursor", "prækursor", "prekursor", "forstadier",
    "lahteained", "prekurzor", "undanfaraefni", "прекурсор",
    "drogenlabor", "drogenkuche", "narkolaboratorium", "narkolab", "narkotikalaboratorium", "stoflaboratorium", "amfetaminlabb", "narkolabor",
    "varna drog", "fikniefnaverksmidja", "fikniefnaframleidsla",
]
# ------------------------------------------------------------------------------ category tables (name -> {key: parts})
TABLES = {
    "TIMBER_PATTERNS": {
        "Rosewood (Dalbergia)": ["palisander", "rosenholz", "rosentra", "palisandr"],
        "Mahogany": ["mahagoni", "mahogny", "mahagon"],
        "Ebony": ["ebenholz", "ibenholt", "ebenholt"],
    },
    "IVORY_PATTERNS": {
        "Elephant ivory": [r"elfenbein(?!kuste)", r"elfenben(?!skyst|skust)", r"elevandiluu(?!rannik)", r"(?<!pobrezie )(?<!pobrezia )slonovin",
                           r"filabein(?!sstrond)", r"заан\s+соёо", r"ዝሆን ጥርስ", r"ዝሆን ጥርሶች", "stosszahn", r"stoßzahn", "stødtand", "stottann"],
    },
    "FAUNA_PATTERNS": {
        "Rhino horn": ["nashorn", "naesehorn", r"næsehorn", "neshorn", "noshorning", "ninasarvik", "nosorozec", "nashyrning", "አውራሪስ"],
        "Pangolin": ["schuppentier", r"skældyr", "skjelldyr", "soomusloom", "luskun"],
        "Reptiles and turtles": ["schildkrot", "reptilien", "krokodil", "skildpadde", "krybdyr", "skilpadde", "reptiler", "skoldpadd", "kilpkonn", "roomaja", "korytnack", "skjaldbak", "skriðdýr"],
        "Birds": ["papagei", "greifvogel", "falken", "papegoj", "papegøj", "papegoy", "papagoi", "papagaj", "pafagauk", "páfagauk"],
        "Primates": [r"\baffen\b", "menneskeaber", "apekatter", r"\bapor\b", r"\bprimaat", r"\bprimat", r"\bopice"],
        "Sharks, rays and marine species": ["haifischflosse", "haiflosse", "haj-?finner", "haifinner", "hainugge", "haibarda", "hailuud"],
        "Glass eels": ["glasaal", r"\bglasal\b"],
        "Big cat parts": ["tigerfell", "tigerknochen", "tigerskind", "tigerskinn", "tigerskinn", "tiigri", "tigria koza"],
    },
    "ARMS_PATTERNS": {
        "Firearms": ["schusswaffe", r"waffen\b", "pistole\\b", "gewehr", "kalaschnikow", "automatwaffe", "skydevaben", r"våben", "vaben", "pistol\\b", "gevær", "gevaer", "automatvapen", r"våpen", "vapen", "skytevapen",
                     "relv\\b", "relva", "relvi", "relvad", "tulirelv", "zbran", "pistol", "puska", "samopal", "skotvopn", "vopn\\b", "byssa", "skammbyssa",
                     "галт зэвсэг", "зэвсэг", "ጦር መሳሪያ", "የጦር መሳሪያ", "ሽጉጥ", "ክላሽ"],
        "Ammunition": ["munition", "patronen", "ammunition", "patroner", "skarpe skud", "laskemoon", "padrun", "strelivo", "naboj", "skotfaeri", "skotfæri", "ጥይት"],
        "Explosives/grenades": ["sprengstoff", "handgranate", "sprængstof", "sprengstoff", "sprängämne", "handgranat", "granat\\b", "lohkeaine", "lõhkeaine", "granaat", "vybusnin", "granat\\b", "sprengiefni", "handsprengja", "тэсэрч бодис", "ቦምብ", "ፈንጂ"],
    },
    "HERITAGE_PATTERNS": {
        "Antiquities/archaeological objects": [
            "kulturguter", "antiquitaten", r"archaologische\s+(?:funde|objekte|gegenstande|artefakte)", "raubgrabung", "oldsager", "antikviteter", "arkaeologiske", "arkeologiske", "fornminnen", "fornlamningar", "kulturminner",
            "arheoloogilis", "muististe", "kultuuriväärtus", "kultuurivaartus", "arch[ae]ologick\\w+\\s+nalez", "archeologick\\w+", "starozitnost", "kulturne pamiatky", "fornmunir", "menningarverdmaeti", "fornleifa",
            "эртний олдвор", "соёлын өв", "ጥንታዊ ቅርስ", "ቅርሶች", "ቅርስ"],
        "Ancient coins": ["antike munzen", "romische munzen", "gamle monter", "antikke monter", "gamla mynt", "vanad mundid", "stare mince", "gamlir peningar", "эртний зоос", "ጥንታዊ ሳንቲም"],
        "Artworks": ["gestohlene gemalde", "kunstraub", "kunstdiebstahl", "stjalne malerier", "stulna malningar", "kunsttyveri", "varastatud maalid", "ukradnute obrazy", "stolin malverk", "хулгайлагдсан зураг"],
        "Fossils": ["fossilien", "dinosaurier", "fossiler", "fossiilid", "fosilie", "steingervinga"],
    },
    "PRECURSOR_PATTERNS": {
        "Acetic anhydride": ["essigsaureanhydrid", "eddikesyreanhydrid", "attiksyraanhydrid", "aaidikhappe", "anhydrid kyseliny octovej"],
        "Ephedrine/Pseudoephedrine": ["ephedrin", "efedrin", "efedriin", "efedrin"],
        "Potassium permanganate": ["kaliumpermanganat", "kaaliumpermanganaat", "manganistan"],
        "Acetone/solvents": ["aceton\\b", "toluol"],
    },
    "STOLEN_VEHICLE_PATTERNS": {
        "Stolen car": [r"gestohlene[nr]?\s+(?:autos|pkw|fahrzeuge|wagen)", r"stjalne\s+(?:biler|bilar|kjoretoy|koretojer)", r"stjålne\s+(?:biler|køretøjer)", r"stulna\s+(?:bilar|fordon)",
                       r"varastatud\s+(?:autod|soidukid|sõidukid)", r"ukradnut\w+\s+(?:auta|vozidl)", r"stolnir\s+bilar", r"хулгайлагдсан\s+автомашин"],
        "Stolen truck/heavy vehicle": [r"gestohlene\s+(?:lkw|lastwagen|baumaschinen)", r"stjalne\s+lastbil", r"stulna\s+lastbil", r"varastatud\s+veoauto"],
    },
}
GENERICS = {
    "GENERIC_TIMBER": [r"geschutztes\s+holz", r"cites-?holz", r"illegaler\s+holzeinschlag", "holzschmuggel", "tropenholz", r"beskyttet\s+tra", r"vernet\s+tre", r"skyddat\s+tra", r"kaitstud\s+puit", "salapuit",
                       r"ebaseaduslik\w*\s+raie", r"chranen\w+\s+drevo", r"nelegaln\w+\s+tazba", r"fridad\w*\s+timbur", r"ulovlig\w*\s+(?:skovhugst|hogst)", r"olaglig\w*\s+avverkning"],
    "GENERIC_FAUNA": [r"artenschutz", "wilderei", "wildtierschmuggel", "tierschmuggel", r"geschutzte\s+(?:tiere|arten)", r"udryddelsestruede\s+dyr", "dyresmugling", r"truede\s+dyrearter", r"smugling\s+av\s+dyr",
                      "djursmuggling", "utrotningshotade", r"ohustatud\s+liigid", "ohustatud loomad", r"ohrozen\w+\s+druh", r"chranen\w+\s+zivocich", "dyrasmygl", r"friðuð\w*\s+dýr"],
    "GENERIC_ARMS": [r"illegale\s+waffen", "waffenschmuggel", "waffenfund", "waffenlager", "waffenarsenal", r"ulovlige\s+vaben", "vabensmugling", r"ulovlige\s+vapen", "vapensmuggling", "vapenfynd", "vabenfund",
                     r"ebaseaduslik\w*\s+relv", "relvasalakaup", r"nelegaln\w+\s+zbran", "zbrojny arsenal", r"ólögleg\w*\s+vopn", "vopnasmygl", "vopnafundur", "хууль бус зэвсэг", "ህገ ወጥ የጦር መሳሪያ"],
    "GENERIC_HERITAGE": [r"kulturgut", "kulturgüter", "kulturerbe", "kulturarv", "kulturgenstande", "kulturminner", "kulturforemal", "kultuuripärand", r"kulturne\s+pamiatky", r"menningarverd", "соёлын өв", "ቅርስ"],
    "GENERIC_STOLEN_VEHICLE": [r"gestohlene\s+(?:fahrzeuge|autos|pkw)", "autodiebstahl", "fahrzeugschieber", "autoschieber", "biltyveri", "biltjuveri", "bilstold", r"stjalne\s+(?:biler|bilar|kjoretoy)", r"stulna\s+(?:bilar|fordon)",
                              "autovargus", r"varastatud\s+(?:autod|soidukid)", r"ukradnut\w+\s+(?:auta|vozidl)", r"krad(?:ez|eze)\s+(?:aut|vozidiel)", r"bílaþjófnaður", "bilathjofnadur", r"stolnir\s+bilar", "автомашин хулгай"],
}
VEHICLE_THEFT_CUE = ["gestohlen", "diebstahl", "stjalne", "stulna", "stulen", "tyveri", "tjuveri", "varastatud", "vargus", "ukradnut", "kradez", "stolnir", "stolin", "thjofnadur", "хулгай"]
VEHICLE_WORDS = ["fahrzeug", r"\bautos?\b", r"\bpkw\b", r"\blkw\b", "lastwagen", r"\bbil\b", "biler", "bilar", "fordon", "kjoretoy", "koretojer", "soiduk", "vozidl", "bifreid", "okutaeki", "автомашин", "машин"]

# ----------------------------------------------------------------------------------------------- risk phrases
RISK = {
    "ORGANIZED": [r"organisiert\w*\s+kriminalitat", "drogenbande", "drogenkartell", "drogenring", r"kriminelle\s+organisation", "tatergruppe", "mafia",
                  r"organiseret\s+kriminalitet", r"kriminelt\s+netvaerk", r"organisert\s+kriminalitet", r"kriminelt\s+nettverk", r"organiserad\s+brottslighet", r"kriminellt\s+natverk",
                  r"organiseeritud\s+kuritegevus", r"kuritegelik\w*\s+grupeering", r"organizovan\w+\s+zlocin", r"zlocinec\w+\s+skupin", r"skipulog\w+\s+glaepa", r"glæpahóp", "glaepahop", "narkokartel", "narkotikakartell"],
    "INSIDER": [r"korrupt\w*\s+(?:zoll|hafen)\w*", "bestochen", "bestechung", r"korrupt\w*\s+(?:told|toll|tull)\w*", "bestukket", "mutor", r"korrumpeeritud\w*", r"skorumpovan\w+\s+colnik"],
    "CONTROLLED_DELIVERY": [r"kontrollierte\s+lieferung", r"kontrolleret\s+levering", r"kontrollert\s+levering", r"kontrollerad\s+leverans", r"kontrollitud\s+tarne", r"kontrolovan\w+\s+dodavk"],
    "FALSE_DECLARATION": [r"falsch\s+deklariert", r"gefalschte\s+(?:papiere|dokumente|rechnungen)", r"falsche\s+angaben", r"ohne\s+genehmigung", r"falskt\s+deklarer", r"falske\s+(?:papirer|dokumenter)", r"forfalskede\s+dokumenter",
                          r"forfalskade\s+dokument", r"vale\s+deklar", r"võltsitud\s+dokument", r"voltsitud\s+dokument", r"falosn\w+\s+doklad", r"falosn\w+\s+dokument", r"fólsuð\s+skjöl", r"folsud\s+skjol"],
    "FRONT_COMPANY": [r"scheinfirma", "briefkastenfirma", "tarnfirma", "skuffeselskab", "dækselskab", "postboksselskap", "skallselskap", "skalbolag", "bulvanforetag", "napufirma", r"fiktivn\w+\s+firm", r"pochybn\w+\s+firm"],
    "TRANSSHIPMENT": ["umschlagplatz", "hafenumschlag", "umgeladen", "umladung", "freihafen", "freizone", "omlastning", "omlasting", "omladning", "umberlaadimine", "ümberlaadimine", "prekladk", "prekladan", "umskipun"],
    "ROUTE_CHANGE": ["umgeleitet", "routenanderung", "omdirigeret", "omdirigert", "omdirigerad", "suunati ümber", "suunati umber", "presmerovan"],
    "INTEL_TIP": [r"nach\s+einem\s+hinweis", r"aufgrund\s+eines\s+hinweises", r"hinweis\s+(?:von|aus)", r"efter\s+(?:et\s+)?tip", r"efter\s+tips", "efterretninger", "underrattelse", "etterretning", r"vihje\s+alusel", r"na\s+zaklade\s+(?:informacie|tipu)", "abending", "ábending"],
}

# ------------------------------------------------------------------------------------- "who sent to whom" cues
# Written for text that is already lower-case and accent-stripped. Each is a regex part that must sit directly
# before the place name (see lexicon._cue). Bare words such as Slovak "do" are left out on purpose: they are also
# ordinary words in Portuguese or English and would turn "porto do Rio" into a destination.
ORIGIN_CUE = (r"(?<![a-z])aus|stammend\s+aus|stammt\s+aus|kommend\s+aus|eingefuhrt\s+aus|eingeschmuggelt\s+aus|"
              r"(?<![a-z])fra|kommet\s+fra|indfort\s+fra|"
              r"(?<![a-z])fran|kommit\s+fran|infort\s+fran|"
              r"(?<![a-z])parit|saabunud\s+(?:\w+\s+)?|"
              r"(?<![a-z])z(?![a-z])|(?<![a-z])zo(?![a-z])|pochadzajuc\w+\s+z|dovezen\w+\s+z|"
              r"ከ")
DEST_CUE = (r"(?<![a-z])nach|bestimmt\s+fur|in\s+richtung|unterwegs\s+nach|auf\s+dem\s+weg\s+nach|mit\s+ziel|"
            r"(?<![a-z])til|(?<![a-z])mod|bestemt\s+for|pa\s+vej\s+til|pa\s+vei\s+til|med\s+destination|"
            r"(?<![a-z])till|(?<![a-z])mot|avsedd\s+for|pa\s+vag\s+till|"
            r"suunduv|teel\s+(?:\w+\s+)?|"
            r"smerom\s+do|na\s+ceste\s+do|urcen\w+\s+(?:do|pre)|odoslan\w+\s+do|"
            r"a\s+leid\s+til|"
            r"ወደ")
TRANSIT_CUE = (r"(?<![a-z])uber|(?<![a-z])durch|transit\s+durch|umschlag\s+in|"
               r"gennem|gjennom|(?<![a-z])genom|"
               r"(?<![a-z])cez|tranzit\s+cez|"
               r"i\s+gegnum")
TO_CUE = r"(?<![a-z])nach|(?<![a-z])til|(?<![a-z])till"
# Mongolian: "X руу" = to X (the word after the name); ablative -аас/-ээс/-оос/-өөс = from X (checked on the name itself)
POST_DEST = r"^\s+(?:улс\s+)?(?:руу|рүү)(?![а-я])"
MN_FROM = r"(?:аас|ээс|оос|өөс)$"

# --------------------------------------------------------------------- numbers, arrests, running totals
CUMUL = (r"\bseit\b|\bbislang\b|\binsgesamt\b|\bin diesem jahr\b|\bim vergangenen jahr\b|\bim jahr 20\d\d\b|\bjahresbilanz\b|\bbisher\b|\bheuer\b"
         r"|\bsiden\b|\bhidtil\b|\bi ar\b|\bsidste ar\b|\bi alt\b|\bhittil\b|\bi fjor\b|\btotalt\b|\bsedan\b|\bhittills\b|\bforra aret\b|\bsammanlagt\b"
         r"|\balates\b|\bsel aastal\b|\bkokku\b|\bmoodunud aastal\b|\btanavu\b|\bseni\b"
         r"|\bod zaciatku\b|\btento rok\b|\bspolu\b|\bcelkovo\b|\bminuly rok\b|\bdoteraz\b|\bza posledn\w+"
         r"|\bfra þvi\b|\bsamtals\b|\ba þessu ari\b|\bi fyrra\b|\bþað sem af er\b"
         r"|\bнийт\b|\bөнгөрсөн жил\b|\bэнэ жил\b|\bэхэлснээс хойш\b|\bнийтдээ\b"
         r"|በጠቅላላው|ባለፈው ዓመት|ከተጀመረ ጀምሮ|በዚህ ዓመት")
ARREST_VERBS = (r"festgenommen|verhaftet|anholdt\w*|arresteret|pagrebet|pagrepet|arrestert|gripna|gripits|gripen|anhallna|haktade|omhandertagna|"
                r"kinni\s+peetud|vahistatud|zadrzan\w+|zatknut\w+|handtekin\w*|handtekn\w+|баривчлагд\w+|баривчилсан|цагдан")
# words that show a text is NOT English, so numbers are read as 2,5 = 2.5 and 1.200 = 1200 (extract._english)
LAT_WORDS = (r"und|der|von|mit|bei|wurde|wurden|zoll|polizei|"
             r"og|som|har|ikke|ble|blev|politiet|tolden|tollvesenet|"
             r"och|av|att|tullen|polisen|"
             r"oli|ning|kuni|politsei|"
             r"boli|bol|ktore|policajti|colnici|"
             r"voru|hald|logreglan|tollgaeslan|"
             r"нь|дээр|болон|байна|гаалийн|цагдаа|"
             r"እና|ነው|ላይ|ውስጥ")
UNIT_WORDS = [
    # (regex word, kind)
    ("zigaretten", "cigarettes"), ("cigaretter", "cigarettes"), ("cigarett", "cigarettes"), ("sigaretter", "cigarettes"),
    ("sigaretti", "cigarettes"), ("sigaretid", "cigarettes"), ("cigariet", "cigarettes"), ("sigarettur", "cigarettes"),
    ("tabletter", "pills"), ("piller", "pills"), ("tabletti", "pills"), ("tabliet", "pills"), ("toflur", "pills"),
    ("fahrzeuge", "vehicles"), ("fahrzeug", "vehicles"), ("pakki", "packs"), ("zigarettenpackungen", "packs"), ("schachteln", "packs"),
]

# --------------------------------------------------------------------------------------- name generation
# Place and country names are inflected in Estonian, Slovak, Icelandic and Mongolian ("Ecuadorist" = from Ecuador,
# "v Bratislave" = in Bratislava). Instead of a language parser, each name is written once as a stem plus an ending
# class and expanded into its common forms; every form is then an exact alias.
ET_V = "- s st sse l lt le ga ks"            # vowel-final stem: soome, soomes, soomest, soomesse, soomel, soomelt, soomele
ET_I = "- i is ist isse ile ilt iga"         # consonant-final stem: ecuador, ecuadori, ecuadoris, ecuadorist ...
ET_A = "- a as ast asse ale alt aga"         # Tallinn, Tallinna, Tallinnas, Tallinnast ...
SK_O = "o a u e om"                          # Slovensko, Slovenska, Slovensku, Slovensku, Slovenskom
SK_A = "a y e u ou"                          # Bratislava, Bratislavy, Bratislave, Bratislavu, Bratislavou
SK_C = "- a u e om"                          # Iran, Iranu, Irane, Iranom
SK_IA = "a e i u ou"                      # Kolumbia, Kolumbie, Kolumbii, Kolumbiu, Kolumbiou
SK_K = "e iach ami iam -"                    # Kosice, Kosiciach ...
IS_L = "- i s"                               # Russland: Russland, Russlandi, Russlands
IS_F = "- u"                                 # Kolumbia -> Kolumbiu (final a becomes u; see _expand)
IS_M = "ur i s -"                            # Noregur, Noregi, Noregs, Noreg
MN = "- д ын ийн ыг ийг аас ээс оос өөс аар ээр оор өөр тай тэй той"

ALIAS_ROLE = {}        # exact alias (normalised) -> "origin" / "dest": set for Estonian forms that carry the case


def _forms(stem, endings, role_from=("st", "lt"), role_to=("sse", "le")):
    out = []
    for e in endings.split():
        f = stem if e == "-" else stem + e
        out.append(f)
        if e != "-":
            if any(e.endswith(x) and e[-len(x):] == x and (len(e) == len(x) or e[:-len(x)] in ("a", "e", "i", "u", "")) for x in role_from):
                ALIAS_ROLE[norm(f)] = "origin"
            elif any(e.endswith(x) and (len(e) == len(x) or e[:-len(x)] in ("a", "e", "i", "u", "")) for x in role_to):
                ALIAS_ROLE[norm(f)] = "dest"
    return out


def _expand(spec, endings_by_class, strip_role=False):
    """'soome/V, ecuador/I' -> all forms."""
    out = []
    for item in [x.strip() for x in spec.split(",") if x.strip()]:
        if "/" in item:
            stem, cls = item.rsplit("/", 1)
            out += _forms(stem, endings_by_class[cls]) if strip_role is False else _forms(stem, endings_by_class[cls], (), ())
        elif ":" in item:
            stem, cls = item.rsplit(":", 1)
            if endings_by_class is _IS and cls == "F":              # feminine -a name: Kolumbia -> Kolumbiu
                out += [stem, stem[:-1] + "u"]
            else:
                out += _forms(stem, endings_by_class[cls], (), ())
        else:
            out.append(item)
    return out


_ET = {"V": ET_V, "I": ET_I, "A": ET_A}
_SK = {"O": SK_O, "A": SK_A, "C": SK_C, "IA": SK_IA, "K": SK_K}
_IS = {"L": IS_L, "F": IS_F, "M": IS_M}


def _germanic(spec):
    out = []
    for n in [x.strip() for x in spec.split(",") if x.strip()]:
        out.append(n)
        if not n.lower().endswith(("s", "x", "z")):
            out.append(n + "s")              # genitive: "Hamburgs Hafen", "Københavns Havn"
    return out


# English name | German, Danish, Norwegian, Swedish (plus genitive -s) | Estonian | Slovak | Icelandic | Mongolian stems | Amharic
# Estonian "x/V" = stem x with ending class V; Slovak "x:O"; Icelandic "x:L". A bare name is kept as it is.
# Names that read the same as an English word are left out (Icelandic "Island", Georgian "Georgia").
COUNTRY_TABLE = r"""
Austria|Österreich,Oesterreich,Østrig,Østerrike,Österrike|austria/V|rakusk:O|austurríki:L|австри|
Germany|Deutschland,Tyskland|saksamaa/V|nemeck:O|þýskaland:L|герман улс,германы,германд|ጀርመን
Denmark|Dänemark,Danemark,Danmark|taani/V|dansk:O|danmörk,danmerkur,danmorku|дани улс,данийн|ዴንማርክ
Estonia|Estland,Eesti|eesti/V|estonsk:O|eistland:L|эстони|ኢስቶኒያ
Ethiopia|Äthiopien,Etiopien,Etiopia|etioopia/V|etiopi:IA|eþíópía:F|эфиоп|ኢትዮጵያ
Iceland|Islandia|-|-|íslandi|исланд|አይስላንድ
Mongolia|Mongolei,Mongoliet,Mongolia|mongoolia/V|mongolsk:O|mongólía:F|монгол|ሞንጎሊያ
Norway|Norwegen,Norge|norra/V|norsk:O|noreg:M|норвег|ኖርዌይ
Slovakia|Slowakei,Slovakiet,Slovakia,Slovakien|slovakkia/V|slovensk:O|slóvakía:F|словак|ስሎቫኪያ
Sweden|Schweden,Sverige|rootsi/V|svedsk:O|svíþjóð,svíþjóðar|швед|ስዊድን
Finland|Finnland,Finland|soome/V|finsk:O|finnland:L|финлянд|ፊንላንድ
Latvia|Lettland,Letland|läti/V|lotyssk:O|lettland:L|латви|ላትቪያ
Lithuania|Litauen|leedu/V|litv:A|litháen|литв|ሊትዌኒያ
Russia|Russland,Rusland,Ryssland|venemaa/V|rusk:O|rússland:L|орос|ሩሲያ
Ukraine|Ukraine,Ukraina|ukraina/V|ukrajin:A|úkraína:F|украин|ዩክሬን
Poland|Polen|poola/V|polsk:O|pólland:L|польш|ፖላንድ
Netherlands|Niederlande,Holland,Nederlandene,Nederländerna|holland/I,madalmaad|holandsk:O|holland:L|нидерланд|ኔዘርላንድ
Belgium|Belgien,Belgia|belgia/V|belgick:O|belgía:F|бельги|ቤልጂየም
France|Frankreich,Frankrig,Frankrike|prantsusmaa/V|francuzsk:O|frakkland:L|франц улс,францын|ፈረንሳይ
Spain|Spanien|hispaania/V|spanielsk:O|spánn|испани|ስፔን
Italy|Italien,Italia|itaalia/V|taliansk:O|ítalía:F|итали|ጣሊያን
Switzerland|Schweiz,Sveits|sveits/I|svajciarsk:O|sviss|швейцар|ስዊዘርላንድ
United Kingdom|Großbritannien,Grossbritannien,Storbritannien,Vereinigtes Königreich,England|suurbritannia/V|britani:IA|bretland|их британи,англи|እንግሊዝ,ዩናይትድ ኪንግደም
Ireland|Irland|iirimaa/V|irsk:O|írland:L|ирланд|አየርላንድ
Czech Republic|Tschechien,Tjekkiet,Tsjekkia,Tjeckien|tsehhi/V|cesk:O|tékkland:L|-|ቼክ
Hungary|Ungarn,Ungern|ungari/V|madarsk:O|ungverjaland|унгар|ሃንጋሪ
Romania|Rumänien,Rumænien,Romania|rumeenia/V|rumunsk:O|rúmenía:F|румын|ሮማኒያ
Bulgaria|Bulgarien|bulgaaria/V|bulharsk:O|búlgaría:F|болгар|ቡልጋሪያ
Serbia|Serbien|serbia/V|srbsk:O|serbía:F|серб|ሰርቢያ
Croatia|Kroatien,Kroatia|horvaatia/V|chorvatsk:O|króatía:F|хорват|ክሮኤሺያ
Slovenia|Slowenien,Slovenien,Slovenia|sloveenia/V|slovinsk:O|slóvenía:F|словен|ስሎቬኒያ
Albania|Albanien,Albania|albaania/V|albansk:O|albanía:F|албани|አልባኒያ
Greece|Griechenland,Grækenland,Hellas,Grekland|kreeka/V|greck:O|grikkland:L|грек улс,грекийн|ግሪክ
Turkey|Türkei,Tyrkiet,Tyrkia,Turkiet|türgi/V|tureck:O|tyrkland:L|турк улс,туркийн|ቱርክ
Cyprus|Zypern,Cypern,Kypros|küpros/I|cyprus:C|kýpur|кипр|ቆጵሮስ
Belarus|Weißrussland,Belarus,Hviderusland,Hviterussland,Vitryssland|valgevene/V|bielorusk:O|hvíta-rússland|беларус|ቤላሩስ
Moldova|Moldau,Moldawien,Moldova,Moldavien|moldova/V|moldavsk:O|moldóva:F|молдав|ሞልዶቫ
Kosovo|Kosovo|kosovo/V|kosov:O|kósóvó|косов|ኮሶቮ
Luxembourg|Luxemburg|luksemburg/I|luxembursk:O|lúxemborg|люксембург|ሉክሰምበርግ
Portugal|Portugal|portugal/I|portugalsk:O|portúgal|португал|ፖርቱጋል
Colombia|Kolumbien,Colombia|colombia/V|kolumbi:IA|kólumbía:F|колумби|ኮሎምቢያ
Ecuador|Ecuador|ecuador/I|ekvador:C|ekvador|эквадор|ኢኳዶር
Brazil|Brasilien,Brasil|brasiilia/V|brazili:IA|brasilía:F|бразил|ብራዚል
Peru|Peru|peruu/V|peru:C|perú|-|ፔሩ
Mexico|Mexiko,Mexico|mehhiko/V|mexik:O|mexíkó|мексик|ሜክሲኮ
Argentina|Argentinien,Argentina|argentina/V|argentin:A|argentína:F|аргентин|አርጀንቲና
Chile|Chile|tsiili/V|cile|síle|-|ቺሊ
Venezuela|Venezuela|venezuela/V|venezuel:A|venesúela:F|венесуэл|ቬንዙዌላ
Bolivia|Bolivien,Bolivia|boliivia/V|bolivi:IA|bólivía:F|боливи|ቦሊቪያ
Paraguay|Paraguay|paraguay/I|paraguaj:C|paragvæ|парагвай|ፓራጓይ
Uruguay|Uruguay|uruguay/I|uruguaj:C|úrúgvæ|уругвай|ኡራጓይ
Cuba|Kuba|kuuba/V|kub:A|kúba:F|-|ኩባ
Panama|Panama|panama/V|panam:A|panama|панам|ፓናማ
Jamaica|Jamaika,Jamaica|jamaica/V|jamajk:A|jamaíka:F|ямайк|ጃማይካ
Canada|Kanada,Canada|kanada/V|kanad:A|kanada|канад|ካናዳ
United States|Vereinigte Staaten,Forenede Stater,Forente stater,Förenta staterna,USA|ameerika uhendriigid,usa|spojene staty,spojenych statoch,spojenych statov,usa|bandaríkin,bandarikjanna,bandarikjunum|америкийн нэгдсэн улс,ану|አሜሪካ,ዩናይትድ ስቴትስ
China|China,Kina|hiina/V|cin:A|kína|хятад|ቻይና
India|Indien,Indien|india/V|indi:IA|indland:L|энэтхэг|ህንድ
Pakistan|Pakistan|pakistan,pakistanist,pakistanisse,pakistanile,pakistanilt|pakistan:C|pakistan|пакистан|ፓኪስታን
Afghanistan|Afghanistan|afganistan/I|afganistan:C|afganistan|афганистан|አፍጋኒስታን
Iran|Iran|iraan/I|iran:C|íran|иран|ኢራን
Iraq|Irak|iraak/I|irak:C|írak|ирак|ኢራቅ
Israel|Israel|iisrael/I|izrael:C|ísrael|израил|እስራኤል
Syria|Syrien,Syria|suuria/V|syri:IA|sýrland:L|сири улс|ሶሪያ
Lebanon|Libanon|liibanon/I|libanon:C|líbanon|ливан|ሊባኖስ
Saudi Arabia|Saudi-Arabien,Saudi Arabia,Saudi-Arabia|saudi-araabia/V|saudsk:O|sádi-arabía|саудын араб|ሳዑዲ አረቢያ,ሳውዲ አረቢያ
United Arab Emirates|Vereinigte Arabische Emirate,Forenede Arabiske Emirater,Forente arabiske emirater,Förenade arabemiraten,VAE|araabia uhendemiraadid|spojene arabske emiraty|sameinuðu arabísku furstadæmin|арабын нэгдсэн эмират|የተባበሩት አረብ ኤምሬትስ,ዩኤኢ
Egypt|Ägypten,Egypten,Egypt|egiptus,egiptuse/V|egypt:C|egyptaland:L|египет|ግብፅ,ግብጽ
Morocco|Marokko|maroko/V|marok:O|marokkó|марокко|ሞሮኮ
Algeria|Algerien,Algeriet|alzeeria/V|alzirsk:O|alsír|алжир|አልጄሪያ
Tunisia|Tunesien|tuneesia/V|tunisk:O|túnis|тунис|ቱኒዚያ
Libya|Libyen|liibua/V|libyj:C|líbía:F|ливи|ሊቢያ
Nigeria|Nigeria|nigeeria/V|nigeri:IA|nígería:F|нигери|ናይጄሪያ
Kenya|Kenia,Kenya|keenia/V|ken:A|kenía:F|-|ኬንያ
Tanzania|Tansania,Tanzania|tansaania/V|tanzani:IA|tansanía:F|танзани|ታንዛኒያ
Uganda|Uganda|uganda/V|ugand:A|úganda|уганд|ዩጋንዳ
Mozambique|Mosambik,Mozambique|mosambiik/I|mozambik:C|mósambík|мозамбик|ሞዛምቢክ
South Africa|Südafrika,Sydafrika,Sør-Afrika|louna-aafrika/V|juhoafricka republika,juhoafrickej republiky,juhoafrickej republike|suður-afríka|өмнөд африк|ደቡብ አፍሪካ
Sudan|Sudan|sudaan/I|sudan:C|súdan|судан|ሱዳን
Somalia|Somalia|somaalia/V|somalsk:O|sómalía:F|сомали|ሶማሊያ
Yemen|Jemen|jeemen/I|jemen:C|jemen|йемен|የመን
Ivory Coast|Elfenbeinküste,Elfenbenskysten,Elfenbenskusten|elevandiluurannik/I|pobrezie slonoviny,pobrezia slonoviny|fílabeinsströndin|кот-д'ивуар|አይቮሪኮስት,አይቮሪ ኮስት
Senegal|Senegal|senegal/I|senegal:C|senegal|сенегал|ሴኔጋል
Ghana|Ghana|ghana/V|ghan:A|-|гана|ጋና
Cameroon|Kamerun|kamerun/I|kamerun:C|kamerún|камерун|ካሜሩን
Thailand|Thailand|-|thajsk:O|taíland|тайланд|ታይላንድ
Vietnam|Vietnam|vietnam/I|vietnam:C|víetnam|вьетнам|ቬትናም
Myanmar|Myanmar,Burma|myanmar/I|mjanmarsk:O|mjanmar|мьянмар|ማያንማር
Japan|Japan|jaapan/I|japonsk:O|japan|япон|ጃፓን
South Korea|Südkorea,Sydkorea,Sør-Korea|louna-korea/V|juzna korea|suður-kórea|өмнөд солонгос|ደቡብ ኮሪያ
Indonesia|Indonesien,Indonesia|indoneesia/V|indonezsk:O|indónesía:F|индонез|ኢንዶኔዥያ
Malaysia|Malaysia|malaisia/V|malajzi:IA|malasía:F|малайз|ማሌዥያ
Philippines|Philippinen,Filippinerne,Filippinene,Filippinerna|filipiinid|filipin:C|filippseyjar|филиппин|ፊሊፒንስ
Kazakhstan|Kasachstan,Kasakhstan,Kazakhstan,Kasakstan|kasahstan/I|kazachstan:C|kasakstan|казахстан|ካዛኪስታን
Uzbekistan|Usbekistan,Uzbekistan|usbekistan/I|uzbekistan:C|úsbekistan|узбекистан|ኡዝቤኪስታን
Tajikistan|Tadschikistan,Tadsjikistan,Tadzjikistan|tadzikistan/I|tadzikistan:C|tadsíkistan|тажикистан|ታጂኪስታን
Turkmenistan|Turkmenistan|turkmenistan/I|turkmenistan:C|túrkmenistan|туркменистан|ቱርክሜኒስታን
Kyrgyzstan|Kirgisistan,Kirgisistan|korgozstan/I|kirgizsk:O|kirgistan|киргиз,кыргыз|ኪርጊዝስታን
Azerbaijan|Aserbaidschan,Aserbajdsjan,Azerbajdzjan|aserbaidzaan/I|azerbajdzan:C|aserbaídsjan|азербайжан|አዘርባጃን
Armenia|Armenien|armeenia/V|armensk:O|armenía:F|армени|አርሜኒያ
Cambodia|Kambodscha,Cambodja,Kambodsja|kambodza/V|kambodz:A|kambódía:F|камбож|ካምቦዲያ
Australia|Australien,Australia|austraalia/V|australi:IA|ástralía:F|австрали|አውስትራሊያ
New Zealand|Neuseeland,New Zealand|uus-meremaa/V|novy zeland,noveho zelandu,novom zelande|nýja-sjáland|шинэ зеланд|ኒው ዚላንድ
Dominican Republic|Dominikanische Republik,Den Dominikanske Republik,Dominikanska republiken|dominikaani vabariik/V|dominikansk:O|dóminíska lýðveldið|доминикан|ዶሚኒካን
Costa Rica|Costa Rica|costa rica/V|kostarik:A|kostaríka|коста-рик|ኮስታሪካ
Djibouti|Dschibuti,Djibouti|djibouti/V|dzibuti|djíbútí|жибути|ጅቡቲ
Eritrea|Eritrea|eritrea/V|eritrej:C|erítrea|эритре|ኤርትራ
South Sudan|Südsudan,Sydsudan,Sør-Sudan|louna-sudaan/I|juzny sudan|suður-súdan|өмнөд судан|ደቡብ ሱዳን
Hong Kong|Hongkong|hongkong/I|hongkong:C|hong kong|хонконг|ሆንግ ኮንግ
Malta|Malta|malta/V|malt:A|malta|-|ማልታ
"""

# Ports, airports and cities: (display, country, [aliases]); Germanic names also get the genitive -s.
# Estonian "x/V", Slovak "x:A", Icelandic and Mongolian are expanded the same way as the countries above.
PLACE_TABLE = r"""
Vienna|Austria|wien,vienna,flughafen wien,schwechat,wien-schwechat,wiener
Salzburg|Austria|salzburg,salzburger
Graz|Austria|graz,grazer
Linz|Austria|linz,linzer
Innsbruck|Austria|innsbruck,innsbrucker
Klagenfurt|Austria|klagenfurt
Villach|Austria|villach
Nickelsdorf|Austria|nickelsdorf
Spielfeld|Austria|spielfeld
Kufstein|Austria|kufstein
Tyrol|Austria|tirol,tyrol
Carinthia|Austria|kärnten
Styria|Austria|steiermark
Burgenland|Austria|burgenland
Upper Austria|Austria|oberösterreich
Lower Austria|Austria|niederösterreich
Vorarlberg|Austria|vorarlberg
Bremerhaven|Germany|bremerhaven,bremerhavener
Hamburg|Germany|hamburg,hamburger hafen
Frankfurt|Germany|frankfurt,flughafen frankfurt
Munich|Germany|münchen
Berlin|Germany|berlin
Cologne|Germany|köln
Düsseldorf|Germany|düsseldorf
Duisburg|Germany|duisburg
Stuttgart|Germany|stuttgart
Leipzig|Germany|leipzig
Dresden|Germany|dresden
Bremen|Germany|bremen
Hanover|Germany|hannover
Nuremberg|Germany|nürnberg
Passau|Germany|passau
Rostock|Germany|rostock
Lübeck|Germany|lübeck
Kiel|Germany|kiel
Wilhelmshaven|Germany|wilhelmshaven
Copenhagen|Denmark|københavn,kobenhavn,copenhagen,kastrup,københavns havn
Aarhus|Denmark|aarhus,århus
Aalborg|Denmark|aalborg
Odense|Denmark|odense
Esbjerg|Denmark|esbjerg
Fredericia|Denmark|fredericia
Roskilde|Denmark|roskilde
Frederikshavn|Denmark|frederikshavn
Gedser|Denmark|gedser
Helsingør|Denmark|helsingør
Billund|Denmark|billund
Padborg|Denmark|padborg
Jutland|Denmark|jylland
Zealand|Denmark|sjælland
Oslo|Norway|oslo,gardermoen
Bergen|Norway|bergen
Stavanger|Norway|stavanger
Trondheim|Norway|trondheim
Kristiansand|Norway|kristiansand
Tromsø|Norway|tromsø
Drammen|Norway|drammen
Fredrikstad|Norway|fredrikstad
Halden|Norway|halden
Larvik|Norway|larvik
Sandefjord|Norway|sandefjord
Stockholm|Sweden|stockholm,arlanda
Gothenburg|Sweden|göteborg,gothenburg,landvetter
Malmö|Sweden|malmö
Helsingborg|Sweden|helsingborg
Uppsala|Sweden|uppsala
Norrköping|Sweden|norrköping
Örebro|Sweden|örebro
Västerås|Sweden|västerås
Jönköping|Sweden|jönköping
Södertälje|Sweden|södertälje
Trelleborg|Sweden|trelleborg
Ystad|Sweden|ystad
Kapellskär|Sweden|kapellskär
Nynäshamn|Sweden|nynäshamn
Halmstad|Sweden|halmstad
Karlshamn|Sweden|karlshamn
Luleå|Sweden|luleå
Umeå|Sweden|umeå
Gävle|Sweden|gävle
Borås|Sweden|borås
Tallinn|Estonia|tallinn/A,tallinna lennujaam,muuga/V,paldiski/I
Tartu|Estonia|tartu/V
Narva|Estonia|narva/V
Pärnu|Estonia|pärnu/V
Sillamäe|Estonia|sillamäe/V
Koidula|Estonia|koidula/V
Luhamaa|Estonia|luhamaa/V
Valga|Estonia|valga/V
Ikla|Estonia|ikla/V
Bratislava|Slovakia|bratislav:A
Košice|Slovakia|košic:K
Nitra|Slovakia|nitr:A
Žilina|Slovakia|žilin:A
Prešov|Slovakia|prešov:C
Trnava|Slovakia|trnav:A
Trenčín|Slovakia|trenčín:C
Komárno|Slovakia|komárn:O
Banská Bystrica|Slovakia|banská bystrica,banskej bystrici,banskou bystricou
Čierna nad Tisou|Slovakia|čierna nad tisou,čiernej nad tisou,čiernu nad tisou
Vyšné Nemecké|Slovakia|vyšné nemecké,vyšnom nemeckom
Michalovce|Slovakia|michalovce,michaloviec,michalovciach
Malacky|Slovakia|malacky,malaciek,malackách
Dunajská Streda|Slovakia|dunajská streda,dunajskej strede
Petržalka|Slovakia|petržalk:A
Poprad|Slovakia|poprad:C
Zvolen|Slovakia|zvolen:C
Skalica|Slovakia|skalic:A
Šamorín|Slovakia|šamorín:C
Reykjavik|Iceland|reykjavík,reykjavik,reykjavíkur
Keflavik|Iceland|keflavík,keflavik,keflavíkur,keflavíkurflugvöllur,keflavíkurflugvelli,leifsstöð
Akureyri|Iceland|akureyri
Seyðisfjörður|Iceland|seyðisfjörður,seyðisfirði
Hafnarfjörður|Iceland|hafnarfjörður,hafnarfirði
Kópavogur|Iceland|kópavogur,kópavogi
Reykjanesbær|Iceland|reykjanesbær
Sundahöfn|Iceland|sundahöfn
Straumsvík|Iceland|straumsvík
Vestmannaeyjar|Iceland|vestmannaeyjar
Ísafjörður|Iceland|ísafjörður
Selfoss|Iceland|selfoss
Ulaanbaatar|Mongolia|улаанбаатар,улаанбаатар хот,чингис хаан
Zamyn-Üüd|Mongolia|замын-үүд,замын үүд
Erdenet|Mongolia|эрдэнэт
Darkhan|Mongolia|дархан
Altanbulag|Mongolia|алтанбулаг
Sükhbaatar|Mongolia|сүхбаатар хот
Choibalsan|Mongolia|чойбалсан
Khovd|Mongolia|ховд
Ölgii|Mongolia|өлгий
Addis Ababa|Ethiopia|አዲስ አበባ,አዲስ አበባ,አዲስ አበባ
Bole airport|Ethiopia|ቦሌ,ቦሌ አየር ማረፊያ
Moyale|Ethiopia|ሞያሌ
Dire Dawa|Ethiopia|ድሬዳዋ
Adama|Ethiopia|አዳማ,ናዝሬት
Hawassa|Ethiopia|ሀዋሳ,ሐዋሳ
Bahir Dar|Ethiopia|ባሕር ዳር,ባህር ዳር
Gondar|Ethiopia|ጎንደር
Mekelle|Ethiopia|መቀሌ
Jimma|Ethiopia|ጅማ
Metema|Ethiopia|መተማ
Dewele|Ethiopia|ደዋሌ
Semera|Ethiopia|ሰመራ
Awash|Ethiopia|አዋሽ
Gambela|Ethiopia|ጋምቤላ
Kombolcha|Ethiopia|ኮምቦልቻ
Humera|Ethiopia|ሁመራ
Jijiga|Ethiopia|ጅጅጋ
Harar|Ethiopia|ሐረር,ሀረር
Djibouti port|Djibouti|ጅቡቲ ወደብ
Dubai|United Arab Emirates|ዱባይ
Istanbul|Turkey|ኢስታንቡል
Bangkok|Thailand|ባንኮክ
Johannesburg|South Africa|ጆሃንስበርግ
Nairobi|Kenya|ናይሮቢ
Mombasa|Kenya|ሞምባሳ
Cairo|Egypt|ካይሮ
Khartoum|Sudan|ካርቱም
Kampala|Uganda|ካምፓላ
Jeddah|Saudi Arabia|ጅዳ
Riyadh|Saudi Arabia|ሪያድ
Beijing|China|ቤጂንግ
Mumbai|India|ሙምባይ
Lagos|Nigeria|ሌጎስ
"""

# Approximate map coordinates for the new places (latitude, longitude)
GEO_PLACES = {
    "Vienna": (48.21, 16.37), "Salzburg": (47.81, 13.04), "Graz": (47.07, 15.44), "Linz": (48.31, 14.29), "Innsbruck": (47.27, 11.39),
    "Klagenfurt": (46.62, 14.31), "Villach": (46.61, 13.85), "Nickelsdorf": (47.93, 17.07), "Spielfeld": (46.71, 15.63),
    "Kufstein": (47.58, 12.17), "Brenner": (47.0, 11.5), "Bremerhaven": (53.55, 8.58), "Kiel": (54.32, 10.14),
    "Duisburg": (51.43, 6.76), "Rostock": (54.09, 12.14), "Lübeck": (53.87, 10.69), "Wilhelmshaven": (53.53, 8.11), "Passau": (48.57, 13.46),
    "Copenhagen": (55.68, 12.57), "Aarhus": (56.16, 10.2), "Aalborg": (57.05, 9.92), "Odense": (55.4, 10.39), "Esbjerg": (55.48, 8.45),
    "Fredericia": (55.57, 9.75), "Roskilde": (55.64, 12.08), "Frederikshavn": (57.44, 10.54), "Gedser": (54.57, 11.93),
    "Helsingør": (56.04, 12.6), "Billund": (55.73, 9.12), "Padborg": (54.82, 9.36),
    "Oslo": (59.91, 10.75), "Bergen": (60.39, 5.32), "Stavanger": (58.97, 5.73), "Trondheim": (63.43, 10.4), "Kristiansand": (58.15, 8.0),
    "Tromsø": (69.65, 18.96), "Drammen": (59.74, 10.2), "Fredrikstad": (59.21, 10.94), "Halden": (59.12, 11.39),
    "Larvik": (59.05, 10.03), "Sandefjord": (59.13, 10.22),
    "Stockholm": (59.33, 18.07), "Gothenburg": (57.71, 11.97), "Malmö": (55.6, 13.0), "Helsingborg": (56.05, 12.69), "Uppsala": (59.86, 17.64),
    "Norrköping": (58.59, 16.18), "Örebro": (59.27, 15.21), "Västerås": (59.61, 16.55), "Jönköping": (57.78, 14.16), "Södertälje": (59.2, 17.63),
    "Trelleborg": (55.38, 13.16), "Ystad": (55.43, 13.82), "Kapellskär": (59.72, 19.07), "Nynäshamn": (58.9, 17.95), "Halmstad": (56.67, 12.86),
    "Karlshamn": (56.17, 14.86), "Luleå": (65.58, 22.15), "Umeå": (63.83, 20.26), "Gävle": (60.67, 17.14), "Borås": (57.72, 12.94),
    "Tallinn": (59.44, 24.75), "Tartu": (58.38, 26.72), "Narva": (59.38, 28.2), "Pärnu": (58.38, 24.5), "Sillamäe": (59.4, 27.76),
    "Koidula": (57.8, 27.0), "Luhamaa": (57.62, 27.4), "Valga": (57.78, 26.05), "Ikla": (57.9, 24.35),
    "Bratislava": (48.15, 17.11), "Košice": (48.72, 21.26), "Nitra": (48.31, 18.09), "Žilina": (49.22, 18.74), "Prešov": (49.0, 21.24),
    "Trnava": (48.38, 17.59), "Trenčín": (48.89, 18.04), "Komárno": (47.76, 18.13), "Banská Bystrica": (48.74, 19.15),
    "Čierna nad Tisou": (48.43, 22.08), "Vyšné Nemecké": (48.79, 22.4), "Michalovce": (48.76, 21.92), "Malacky": (48.44, 17.02),
    "Dunajská Streda": (47.99, 17.62), "Petržalka": (48.1, 17.11), "Poprad": (49.06, 20.3), "Zvolen": (48.58, 19.12),
    "Skalica": (48.84, 17.22), "Šamorín": (48.03, 17.31),
    "Reykjavik": (64.15, -21.94), "Keflavik": (63.99, -22.56), "Akureyri": (65.68, -18.1), "Seyðisfjörður": (65.26, -14.0),
    "Hafnarfjörður": (64.07, -21.94), "Kópavogur": (64.11, -21.91), "Reykjanesbær": (63.99, -22.56), "Sundahöfn": (64.15, -21.87),
    "Straumsvík": (64.04, -22.04), "Vestmannaeyjar": (63.44, -20.27), "Ísafjörður": (66.07, -23.13), "Selfoss": (63.93, -21.0),
    "Ulaanbaatar": (47.92, 106.92), "Zamyn-Üüd": (43.72, 111.9), "Erdenet": (49.03, 104.08), "Darkhan": (49.49, 105.92),
    "Altanbulag": (50.3, 106.5), "Sükhbaatar": (50.23, 106.2), "Choibalsan": (48.07, 114.53), "Khovd": (48.0, 91.64), "Ölgii": (48.97, 89.96),
    "Bremen": (53.08, 8.8), "Cologne": (50.94, 6.96), "Dresden": (51.05, 13.74), "Düsseldorf": (51.23, 6.78), "Hanover": (52.37, 9.74),
    "Leipzig": (51.34, 12.37), "Nuremberg": (49.45, 11.08), "Stuttgart": (48.78, 9.18),
    "Burgenland": (47.5, 16.4), "Carinthia": (46.75, 14.0), "Lower Austria": (48.3, 15.7), "Styria": (47.3, 15.0), "Tyrol": (47.2, 11.4),
    "Upper Austria": (48.1, 14.0), "Vorarlberg": (47.25, 9.9), "Jutland": (56.0, 9.3), "Zealand": (55.5, 11.8),
    "Dubai": (25.2, 55.27), "Istanbul": (41.01, 28.98), "Bangkok": (13.75, 100.5), "Johannesburg": (-26.2, 28.05), "Nairobi": (-1.29, 36.82),
    "Mombasa": (-4.04, 39.67), "Cairo": (30.04, 31.24), "Khartoum": (15.5, 32.56), "Kampala": (0.35, 32.58), "Jeddah": (21.54, 39.17),
    "Riyadh": (24.71, 46.68), "Beijing": (39.9, 116.4), "Mumbai": (19.08, 72.88), "Lagos": (6.52, 3.38),
    "Addis Ababa": (9.03, 38.74), "Bole airport": (8.98, 38.8), "Moyale": (3.52, 39.05), "Dire Dawa": (9.6, 41.85), "Adama": (8.54, 39.27),
    "Hawassa": (7.06, 38.48), "Bahir Dar": (11.59, 37.39), "Gondar": (12.6, 37.47), "Mekelle": (13.5, 39.47), "Jimma": (7.67, 36.83),
    "Metema": (12.95, 36.2), "Dewele": (11.4, 42.15), "Semera": (11.79, 41.0), "Awash": (8.98, 40.17), "Gambela": (8.25, 34.59),
    "Kombolcha": (11.08, 39.74), "Humera": (14.28, 36.6), "Jijiga": (9.35, 42.8), "Harar": (9.31, 42.12), "Djibouti port": (11.6, 43.14),
}
GEO_COUNTRIES = {"Djibouti": (11.8, 42.6), "Eritrea": (15.2, 39.8), "South Sudan": (7.9, 29.7)}


def _split(row):
    return [c.strip() for c in row.split("|")]


def country_rows():
    """[(English name, [aliases])] with every inflected form written out."""
    rows = []
    for line in COUNTRY_TABLE.strip().splitlines():
        f = _split(line)
        if len(f) < 3:
            continue
        eng = f[0]
        als = []
        als += _germanic(f[1]) if len(f) > 1 else []
        if len(f) > 2 and f[2] not in ("", "-"):
            als += _expand(f[2], _ET)
        if len(f) > 3 and f[3] not in ("", "-"):
            als += _expand(f[3], _SK)
        if len(f) > 4 and f[4] not in ("", "-"):
            als += _expand(f[4], _IS)
        if len(f) > 5 and f[5] not in ("", "-"):
            for stem in f[5].split(","):
                stem = stem.strip()
                if stem:
                    als.append(stem)                       # case endings are handled by the Cyrillic stem matcher
        if len(f) > 6:
            als += [x.strip() for x in f[6].split(",") if x.strip()]
        rows.append((eng, als))
    return rows


def place_rows():
    """[(display, country, [aliases])]."""
    rows = []
    for line in PLACE_TABLE.strip().splitlines():
        f = _split(line)
        if len(f) < 3:
            continue
        als = []
        for a in [x.strip() for x in f[2].split(",") if x.strip()]:
            if "/" in a:
                als += _expand(a, _ET)
            elif ":" in a:
                stem, cls = a.rsplit(":", 1)
                als += _expand(a, _SK) if cls in _SK else _expand(a, _IS)
            else:
                als.append(a)
                if f[1] in ("Austria", "Germany", "Denmark", "Norway", "Sweden") and not a.lower().endswith(("s", "x", "z")):
                    als.append(a + "s")
        rows.append((f[0], f[1], als))
    return rows
