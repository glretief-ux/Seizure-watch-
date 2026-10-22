# -*- coding: utf-8 -*-
"""Cover load: the goods the drugs travelled with, or were declared as.

The extractor stores whichever goods word it matched, in the language of the article. Some of those
matches are noise: a short word found inside a longer one ("cement" in "enforcement", the Hindi for
"fruit" in "success"), a body-concealment or lab word ("clothing", "chemicals", a spare tyre), or a
phrase that merely follows "described as". Because article text is not kept, this module can only
judge the stored word. It therefore

  * keeps a word only if it is a recognised kind of goods, and names it in English;
  * for words that are often noise, keeps it only when the same word stands alone in the headline;
  * puts each kept item in one of a few groups, for the dashboard.

Missing a real cover load is acceptable here; showing a false one is not, because officers read
this as a lead.
"""
import re
from .lexicon import norm, strip_accents

# Group names, in the order the dashboard falls back to when counts tie.
FRUIT, FOOD, COFFEE, FISH, TIMBER, FURN, BUILD, METAL, MACH, ELEC, CHEM, CLOTH, GOODS = (
    "Fruit & vegetables", "Staple foods & drinks", "Coffee & cocoa", "Fish & meat", "Timber & wood",
    "Furniture", "Building materials", "Metals, scrap & fuel", "Machinery & vehicle parts",
    "Electronics & appliances", "Chemicals & plastics", "Clothing & textiles", "Toys & consumer goods")
GROUPS = [FRUIT, FOOD, COFFEE, FISH, TIMBER, FURN, BUILD, METAL, MACH, ELEC, CHEM, CLOTH, GOODS]

# (group, English item, pattern on the normalised stored word, must the word stand alone in the headline?)
# First match wins, so specific patterns come before general ones.
_RAW = [
    (CHEM, "plastic waste", r"plastic\s+(?:waste|scrap)|dechets\s+plastiques", False),
    (GOODS, "cosmetics", r"cosmetic|hair\s+treatment|body\s+scrub|baby\s+powder", False),
    (FRUIT, "banana", r"banan|platano|банан|香蕉", False),
    (FRUIT, "banana", r"^موز$|^muz$|^केला$", True),             # inside "distributors", "Muzaffer", "alone"
    (FRUIT, "pineapple", r"pineapple|^pinas?$", False),
    (FRUIT, "citrus", r"citrus|\borange", False),
    (FRUIT, "mango", r"\bmango", False),
    (FRUIT, "avocado", r"avocado|aguacate", False),
    (FRUIT, "fruit", r"(?<!hanging )fruit|^fruta|guava|meyve|فواكه|فاكهة|фрукт|水果", False),
    (FRUIT, "fruit", r"^फल$", True),                              # inside the Hindi for "success"
    (FRUIT, "vegetables", r"vegetable|cabbage|celery|sebze|خضروات|овощ|蔬菜|सब्जी|सबजी", False),
    (FOOD, "rice", r"\brice\b|arroz|大米|चावल|pirinc", False),
    (FOOD, "rice", r"^ارز$", True),
    (FOOD, "flour", r"\bflour\b", False),
    (FOOD, "sugar", r"\bsugar\b|azucar|\bsucre\b", False),
    (FOOD, "salt", r"\bsalt\b", False),
    (FOOD, "biscuits", r"biscuit", False),
    (FOOD, "starch", r"starch", False),
    (FOOD, "palm oil", r"palm\s+oil", False),
    (FOOD, "canned food", r"\bcanned\b|\btinned\b", False),
    (FOOD, "juice", r"juice|\bjugo\b", False),
    (FOOD, "pet food", r"dog\s+food|pet\s+food", False),
    (FOOD, "food", r"foodstuff|^food$", False),
    (COFFEE, "coffee", r"\bcoffee\b|кофе|咖啡|قهوة|kahve|कॉफी", False),
    (COFFEE, "cocoa", r"cocoa|cacao", False),
    (FISH, "fish", r"\bfish\b|seafood|pescado|poisson|मछली|鱼", False),
    (FISH, "meat", r"\bmeat\b|\bcarne\b|لحوم", False),
    (FISH, "frozen goods", r"frozen|congelad|congele|冷冻|冷凍|мороженн", True),
    (TIMBER, "timber", r"timber|\bwood\b|madera|\bbois\b|kereste|خشب|древесин|木材|लकडी", False),
    (FURN, "furniture", r"furniture|muebles|meubles|mobilya|اثاث|мебел|家具|फर्नीचर", False),
    (BUILD, "cement", r"cement", True),
    (BUILD, "tiles & ceramics", r"\btiles?\b|ceramic", False),
    (BUILD, "glass", r"\bglass\b", True),
    (BUILD, "marble & granite", r"marble|marmol|granite", False),
    (METAL, "steel", r"\bsteel\b|acero", False),
    (METAL, "aluminium", r"alumin", False),
    (METAL, "copper", r"\bcopper\b", False),
    (METAL, "scrap metal", r"\bscrap\b|chatarra|hurda|металлолом|废金属|廢金屬|خردة", False),
    (METAL, "coal & charcoal", r"\bcoal\b|charcoal", False),
    (MACH, "machinery", r"machinery|maquinaria|станк|机械|機械", False),
    (MACH, "machinery", r"^makine$|^मशीन$|^الات$", True),         # inside "machine gun" and many Arabic words
    (MACH, "equipment", r"оборудован", True),
    (MACH, "vehicle parts", r"spare\s+parts|auto\s?parts|vehicle\s+parts", False),
    (MACH, "batteries", r"bateria|batteries", False),
    (ELEC, "electronics", r"electronic|elektronik|الكترونيات", False),
    (ELEC, "appliances", r"appliances", False),
    (CHEM, "chemicals", r"chemical|sanitis|sanitiz", True),
    (CHEM, "fertiliser", r"fertili[sz]er", False),
    (CHEM, "insecticide", r"insecticide|pesticide", False),
    (CHEM, "polyurethane", r"polyurethane|\bpu\s+tubes", False),
    (CLOTH, "clothing", r"clothing|clothes|garments?|\bropa\b|^ملابس$|одежд|服装|कपडे", True),
    (CLOTH, "textiles", r"textile|tekstil", False),
    (GOODS, "toys", r"\btoys?\b|oyuncak|игрушк|玩具|खिलौने|^العاب$", False),
    (GOODS, "general goods", r"(?:consumer|household|industrial|general|non-hazardous)\s+(?:goods|products)|^goods$", False),
    # German, Danish, Estonian, Amharic, Icelandic, Mongolian, Norwegian, Slovak, Swedish
    (FRUIT, "pineapple", r"^ananas", False),
    (FRUIT, "citrus", r"^orangen|^appelsin|^apelsin", False),
    (FRUIT, "fruit", r"^obst|^frugt|^frukt|^puuvili|^ovocie|ፍራፍሬ|жимс", False),
    (FRUIT, "vegetables", r"^gemuse|^gronnsaker|^grontsager|^gronsaker|^zelenina", False),
    (FOOD, "sugar", r"^zucker|^sukker|^socker|^suhkur|^cukor|^sykur|ስኳር", False),
    (FOOD, "rice", r"^hrisgrjon|ሩዝ", False),
    (FOOD, "flour", r"ዱቄት", False),
    (COFFEE, "coffee", r"^kaffee|^kaffe|^kohv|^kaffi|^kava$|ቡና", False),
    (FISH, "fish", r"^fisch|^fisk|^ryba$|загас", False),
    (FISH, "meat", r"^fleisch|^maso$", False),
    (FISH, "frozen goods", r"^tiefkuhl|^gefrier|^frossen|^fryst|^kulmutatud|^mrazen", True),
    (TIMBER, "timber", r"^holz$|^timbur$|^puit$|^drevo$|እንጨት", False),
    (FURN, "furniture", r"^mobel|^mobler|^møbler|^husgogn|^mooblid|^nabytok|тавилга", False),
    (BUILD, "tiles & ceramics", r"^fliesen|^fliser|^flisar|^obklad", False),
    (BUILD, "marble & granite", r"^marmor|^mramor|^marmari", False),
    (METAL, "scrap metal", r"^schrott|^skrot|^brotajarn", False),
    (MACH, "vehicle parts", r"^ersatzteile|^autoteile|^reservedele|^reservdelar|^varuosad|^nahradne diely|^varahlutir|эд анги|የመኪና መለዋወጫ", False),
    (CLOTH, "clothing", r"^kleidung|^klaeder|^klader|^riided|^oblecenie|хувцас|ልብስ", True),
    (CLOTH, "textiles", r"^textilien|ጨርቃ ጨርቅ", False),
    (GOODS, "toys", r"^spielzeug|^legetoj|^leketoy|^leksaker|^hracky|^leikfong|^mangu|тоглоом", False),
]

ITEMS = [(g, label, re.compile(strip_accents(p), re.I), bool(c)) for g, label, p, c in _RAW]
GROUP_OF = {label: g for g, label, _, _ in ITEMS}

_ARABIC = re.compile(r"[؀-ۿ]")


def _split(v):
    return [x.strip() for x in str(v).split(";") if x.strip()] if isinstance(v, str) else []


def _standalone(token, headline):
    """The stored word stands as a word of its own in the (normalised) headline.
    Latin words may take a plural; Arabic words may take the article and one-letter prefix."""
    t = re.escape(token)
    if _ARABIC.search(token):
        pat = r"(?<![؀-ۿ])[وبلكف]?(?:ال)?" + t + r"(?![؀-ۿ])"
    else:
        pat = r"(?<!\w)" + t + r"(?:s|es)?(?!\w)"
    return re.search(pat, headline) is not None


def items(cargo, headline=""):
    """Recognised goods in a stored cover-cargo string, named in English, without repeats."""
    out, h = [], norm(headline or "")
    for raw in _split(cargo):
        tok = norm(raw)
        for _g, label, pat, confirm in ITEMS:
            if not pat.search(tok):
                continue
            if confirm and not _standalone(tok, h):
                break
            if label not in out:
                out.append(label)
            break
    return out


def groups(cargo):
    """The groups for an already-cleaned item string ('banana; steel'), most specific first, no repeats."""
    seen = []
    for label in _split(cargo):
        g = GROUP_OF.get(label)
        if g and g not in seen:
            seen.append(g)
    return seen


def clean(cargo, *headlines):
    """The stored string, replaced by its recognised English items ('banana; steel'), or None."""
    return "; ".join(items(cargo, " ".join(h for h in headlines if isinstance(h, str) and h))) or None
