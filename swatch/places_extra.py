# -*- coding: utf-8 -*-
"""More places and 'cues' that tell the reader which country a report is from when the headline names a
small town, a county, a police agency or a currency instead of the country. Plain data; add freely.
Everything is matched on accent-stripped lower-case text. Ambiguous names (Worcester, Peterborough,
Georgia, Punjab...) are left out on purpose."""

# (display name, country, [aliases])
PLACES = [
    # --- Malaysia
    ("Penang", "Malaysia", ["penang", "pulau pinang", "george town penang", "butterworth"]), ("Kuching", "Malaysia", ["kuching"]),
    ("Sarawak", "Malaysia", ["sarawak", "miri"]), ("Sabah", "Malaysia", ["sabah", "kota kinabalu", "tawau", "sandakan"]),
    ("Johor", "Malaysia", ["johor", "johor bahru", "pasir gudang", "tanjung pelepas"]), ("Selangor", "Malaysia", ["selangor", "klang", "port klang", "shah alam", "petaling jaya", "subang"]),
    ("Kedah", "Malaysia", ["kedah", "alor setar", "langkawi"]), ("Perak", "Malaysia", ["perak", "ipoh"]), ("Kelantan", "Malaysia", ["kelantan", "kota bharu", "rantau panjang"]),
    ("Pahang", "Malaysia", ["pahang", "kuantan"]), ("Terengganu", "Malaysia", ["terengganu", "kuala terengganu"]), ("Melaka", "Malaysia", ["melaka", "malacca"]),
    ("Negeri Sembilan", "Malaysia", ["negeri sembilan", "seremban"]), ("Perlis", "Malaysia", ["perlis", "padang besar"]), ("Putrajaya", "Malaysia", ["putrajaya"]),
    # --- Canada
    ("Ontario", "Canada", ["ontario"]), ("Alberta", "Canada", ["alberta"]), ("British Columbia", "Canada", ["british columbia"]), ("Manitoba", "Canada", ["manitoba"]),
    ("Saskatchewan", "Canada", ["saskatchewan", "saskatoon", "regina sask"]), ("Nova Scotia", "Canada", ["nova scotia", "halifax"]), ("New Brunswick", "Canada", ["new brunswick canada", "moncton"]),
    ("Quebec", "Canada", ["quebec", "montreal"]), ("Calgary", "Canada", ["calgary"]), ("Edmonton", "Canada", ["edmonton"]), ("Winnipeg", "Canada", ["winnipeg"]),
    ("Ottawa", "Canada", ["ottawa"]), ("Brampton", "Canada", ["brampton"]), ("Mississauga", "Canada", ["mississauga"]), ("Surrey (BC)", "Canada", ["surrey b.c", "surrey bc"]),
    ("Chilliwack", "Canada", ["chilliwack"]), ("Orillia", "Canada", ["orillia"]), ("Kitchener", "Canada", ["kitchener", "waterloo region", "waterloo regional"]),
    ("Hamilton (ON)", "Canada", ["hamilton ont", "hamilton, ont"]), ("London (ON)", "Canada", ["london, ont", "london ont"]), ("Kelowna", "Canada", ["kelowna"]),
    ("Abbotsford", "Canada", ["abbotsford"]), ("Windsor (ON)", "Canada", ["windsor, ont", "windsor ont"]), ("Sarnia", "Canada", ["sarnia"]), ("Thunder Bay", "Canada", ["thunder bay"]),
    ("Sudbury", "Canada", ["sudbury"]), ("Barrie", "Canada", ["barrie"]), ("Oshawa", "Canada", ["oshawa"]), ("Red Deer", "Canada", ["red deer"]), ("Lethbridge", "Canada", ["lethbridge"]),
    # --- Nigeria
    ("Kogi", "Nigeria", ["kogi", "lokoja"]), ("Enugu", "Nigeria", ["enugu"]), ("Kano", "Nigeria", ["kano"]), ("Kaduna", "Nigeria", ["kaduna"]), ("Abuja", "Nigeria", ["abuja"]),
    ("Port Harcourt", "Nigeria", ["port harcourt"]), ("Ogun", "Nigeria", ["ogun", "abeokuta"]), ("Oyo", "Nigeria", ["ibadan"]), ("Edo", "Nigeria", ["benin city"]),
    ("Delta (Nigeria)", "Nigeria", ["warri", "asaba"]), ("Anambra", "Nigeria", ["anambra", "onitsha", "awka"]), ("Imo", "Nigeria", ["owerri"]), ("Borno", "Nigeria", ["borno", "maiduguri"]),
    ("Adamawa", "Nigeria", ["adamawa", "yola"]), ("Niger State", "Nigeria", ["minna"]), ("Plateau", "Nigeria", ["jos plateau", "plateau state"]), ("Benue", "Nigeria", ["benue", "makurdi"]),
    ("Katsina", "Nigeria", ["katsina"]), ("Sokoto", "Nigeria", ["sokoto"]), ("Rivers State", "Nigeria", ["rivers state"]), ("Akwa Ibom", "Nigeria", ["akwa ibom", "uyo"]),
    # --- Philippines
    ("Cebu", "Philippines", ["cebu"]), ("Davao", "Philippines", ["davao"]), ("Quezon City", "Philippines", ["quezon city"]), ("Pampanga", "Philippines", ["pampanga"]),
    ("Zamboanga", "Philippines", ["zamboanga"]), ("Iloilo", "Philippines", ["iloilo"]), ("Cavite", "Philippines", ["cavite"]), ("Bulacan", "Philippines", ["bulacan"]),
    ("Laguna", "Philippines", ["laguna"]), ("Batangas", "Philippines", ["batangas"]), ("Cagayan de Oro", "Philippines", ["cagayan de oro"]), ("Pasay", "Philippines", ["pasay", "naia"]),
    # --- Fiji and the Pacific
    ("Suva", "Fiji", ["suva"]), ("Nadi", "Fiji", ["nadi"]), ("Lautoka", "Fiji", ["lautoka"]),
    # --- United Kingdom and Ireland
    ("Stoke-on-Trent", "United Kingdom", ["stoke-on-trent", "stoke on trent"]), ("Sheffield", "United Kingdom", ["sheffield"]), ("Leeds", "United Kingdom", ["leeds"]),
    ("Liverpool", "United Kingdom", ["liverpool"]), ("Manchester", "United Kingdom", ["manchester"]), ("Birmingham (UK)", "United Kingdom", ["west midlands police"]),
    ("Glasgow", "United Kingdom", ["glasgow"]), ("Edinburgh", "United Kingdom", ["edinburgh"]), ("Belfast", "United Kingdom", ["belfast"]), ("Cardiff", "United Kingdom", ["cardiff"]),
    ("Felixstowe", "United Kingdom", ["felixstowe"]), ("Southampton", "United Kingdom", ["southampton"]), ("Dover", "United Kingdom", ["dover"]), ("Heathrow", "United Kingdom", ["heathrow"]),
    ("Meath", "Ireland", ["county meath", "meath"]), ("Cork", "Ireland", ["cork"]), ("Limerick", "Ireland", ["limerick"]), ("Galway", "Ireland", ["galway"]),
    ("Louth", "Ireland", ["louth", "dundalk", "drogheda"]), ("Kildare", "Ireland", ["kildare"]), ("Wexford", "Ireland", ["wexford", "rosslare"]), ("Kerry", "Ireland", ["county kerry"]),
    # --- United States: cities that local news names alone
    ("Boston", "United States", ["boston"]), ("Chicago", "United States", ["chicago"]), ("Houston", "United States", ["houston"]), ("Dallas", "United States", ["dallas"]),
    ("San Antonio", "United States", ["san antonio"]), ("El Paso", "United States", ["el paso"]), ("Phoenix", "United States", ["phoenix"]), ("Tucson", "United States", ["tucson"]),
    ("Las Vegas", "United States", ["las vegas"]), ("Denver", "United States", ["denver"]), ("Seattle", "United States", ["seattle"]), ("Portland (OR)", "United States", ["portland, ore", "portland oregon"]),
    ("Detroit", "United States", ["detroit"]), ("Atlanta", "United States", ["atlanta"]), ("Charlotte", "United States", ["charlotte, n", "charlotte nc"]), ("Baltimore", "United States", ["baltimore"]),
    ("Pittsburgh", "United States", ["pittsburgh"]), ("Cleveland", "United States", ["cleveland"]), ("Cincinnati", "United States", ["cincinnati"]), ("Columbus (OH)", "United States", ["columbus, ohio"]),
    ("Indianapolis", "United States", ["indianapolis"]), ("Milwaukee", "United States", ["milwaukee"]), ("Minneapolis", "United States", ["minneapolis"]), ("Kansas City", "United States", ["kansas city"]),
    ("St. Louis", "United States", ["st. louis", "saint louis"]), ("Memphis", "United States", ["memphis"]), ("Nashville", "United States", ["nashville"]), ("Louisville", "United States", ["louisville"]),
    ("New Orleans", "United States", ["new orleans"]), ("Tampa", "United States", ["tampa"]), ("Orlando", "United States", ["orlando"]), ("Jacksonville", "United States", ["jacksonville"]),
    ("Sacramento", "United States", ["sacramento"]), ("San Francisco", "United States", ["san francisco"]), ("San Jose", "United States", ["san jose, calif", "san jose california"]),
    ("Oakland", "United States", ["oakland"]), ("Fresno", "United States", ["fresno"]), ("Bakersfield", "United States", ["bakersfield"]), ("Riverside", "United States", ["riverside county", "riverside, calif"]),
    ("Temecula", "United States", ["temecula", "fallbrook", "murrieta"]), ("San Bernardino", "United States", ["san bernardino"]), ("Orange County (CA)", "United States", ["orange county, calif"]),
    ("Albuquerque", "United States", ["albuquerque"]), ("Oklahoma City", "United States", ["oklahoma city"]), ("Tulsa", "United States", ["tulsa"]), ("Omaha", "United States", ["omaha"]),
    ("Salt Lake City", "United States", ["salt lake city"]), ("Spokane", "United States", ["spokane"]), ("Tacoma", "United States", ["tacoma"]), ("Anchorage", "United States", ["anchorage"]),
    ("Honolulu", "United States", ["honolulu"]), ("Buffalo", "United States", ["buffalo, n"]), ("Rochester (NY)", "United States", ["rochester, n"]), ("Syracuse", "United States", ["syracuse"]),
    ("Albany", "United States", ["albany, n"]), ("Providence", "United States", ["providence"]), ("Hartford", "United States", ["hartford"]), ("Greenville", "United States", ["greenville"]),
    ("Charleston", "United States", ["charleston, s"]), ("Raleigh", "United States", ["raleigh"]), ("Richmond (VA)", "United States", ["richmond, va"]), ("Lewiston", "United States", ["lewiston"]),
    ("Dyersburg", "United States", ["dyersburg"]), ("Laredo", "United States", ["laredo"]), ("Brownsville", "United States", ["brownsville"]), ("McAllen", "United States", ["mcallen"]),
    ("Eagle Pass", "United States", ["eagle pass"]), ("Del Rio", "United States", ["del rio"]), ("Yuma", "United States", ["yuma"]), ("Calexico", "United States", ["calexico"]),
    ("Otay Mesa", "United States", ["otay mesa"]), ("Nogales (AZ)", "United States", ["nogales, ariz"]), ("Interstate 15", "United States", ["interstate 15", "interstate 5", "interstate 10", "interstate 95", "interstate 40", "interstate 35", "interstate 80", "interstate 70"]),
    # --- Mexico, Colombia and others in Spanish
    ("Sinaloa", "Mexico", ["sinaloa", "culiacan", "mazatlan"]), ("Sonora", "Mexico", ["sonora", "hermosillo"]), ("Baja California", "Mexico", ["baja california", "tijuana", "mexicali", "ensenada"]),
    ("Chihuahua", "Mexico", ["chihuahua", "ciudad juarez"]), ("Jalisco", "Mexico", ["jalisco", "guadalajara"]), ("Michoacan", "Mexico", ["michoacan", "lazaro cardenas"]),
    ("Tamaulipas", "Mexico", ["tamaulipas", "reynosa", "matamoros", "nuevo laredo"]), ("Nuevo Leon", "Mexico", ["nuevo leon", "monterrey"]), ("Veracruz", "Mexico", ["veracruz"]),
    ("Oaxaca", "Mexico", ["oaxaca"]), ("Chiapas", "Mexico", ["chiapas", "tapachula"]), ("Guerrero", "Mexico", ["guerrero", "acapulco"]), ("Yucatan", "Mexico", ["yucatan", "merida"]),
    ("Cancun", "Mexico", ["cancun", "quintana roo"]), ("Puebla", "Mexico", ["puebla"]), ("Queretaro", "Mexico", ["queretaro"]), ("Manzanillo", "Mexico", ["manzanillo"]),
    ("Nariño", "Colombia", ["narino", "tumaco", "pasto"]), ("Cauca", "Colombia", ["cauca", "popayan"]), ("Antioquia", "Colombia", ["antioquia", "medellin"]), ("Meta", "Colombia", ["puerto gaitan", "villavicencio"]),
    ("Putumayo", "Colombia", ["putumayo"]), ("Norte de Santander", "Colombia", ["norte de santander", "cucuta"]), ("Valle del Cauca", "Colombia", ["valle del cauca", "cali", "buenaventura"]),
    ("Barranquilla", "Colombia", ["barranquilla"]), ("Cartagena", "Colombia", ["cartagena"]), ("Santa Marta", "Colombia", ["santa marta"]), ("Bogota", "Colombia", ["bogota"]),
    ("Ñuble", "Chile", ["nuble", "chillan"]), ("Valparaiso", "Chile", ["valparaiso", "san antonio chile"]), ("Antofagasta", "Chile", ["antofagasta"]), ("Arica", "Chile", ["arica"]),
    ("Iquique", "Chile", ["iquique"]), ("Santiago (Chile)", "Chile", ["region metropolitana"]), ("Biobio", "Chile", ["biobio", "concepcion chile"]),
    ("Guayas", "Ecuador", ["guayas", "esmeraldas", "manabi"]), ("Callao", "Peru", ["callao"]), ("Piura", "Peru", ["piura", "tumbes"]), ("Santa Cruz (Bolivia)", "Bolivia", ["santa cruz de la sierra"]),
    # --- India extras
    ("Lakshadweep", "India", ["lakshadweep"]), ("Punjab (India)", "India", ["punjab police", "punjab, india", "amritsar"]), ("Goa", "India", ["goa"]), ("Mumbai", "India", ["nhava sheva", "jnpt"]),
    ("Mundra", "India", ["mundra"]), ("Kolkata", "India", ["kolkata"]), ("Hyderabad (India)", "India", ["hyderabad police", "rajiv gandhi international"]),
    # --- Pakistan, Bangladesh, Sri Lanka, Nepal
    ("Karachi", "Pakistan", ["karachi"]), ("Lahore", "Pakistan", ["lahore"]), ("Islamabad", "Pakistan", ["islamabad"]), ("Peshawar", "Pakistan", ["peshawar"]), ("Quetta", "Pakistan", ["quetta"]),
    ("Dhaka", "Bangladesh", ["dhaka"]), ("Chattogram", "Bangladesh", ["chattogram", "chittagong", "cox's bazar", "teknaf"]), ("Colombo", "Sri Lanka", ["colombo"]), ("Kathmandu", "Nepal", ["kathmandu"]),
    # --- Southeast Asia, Australia, New Zealand
    ("Jakarta", "Indonesia", ["jakarta"]), ("Surabaya", "Indonesia", ["surabaya"]), ("Medan", "Indonesia", ["medan"]), ("Batam", "Indonesia", ["batam"]), ("Aceh", "Indonesia", ["aceh"]), ("Bali", "Indonesia", ["bali"]),
    ("Bangkok", "Thailand", ["bangkok"]), ("Chiang Mai", "Thailand", ["chiang mai"]), ("Hanoi", "Vietnam", ["hanoi"]), ("Ho Chi Minh City", "Vietnam", ["ho chi minh", "saigon"]), ("Phnom Penh", "Cambodia", ["phnom penh"]),
    ("Sydney", "Australia", ["sydney"]), ("Melbourne", "Australia", ["melbourne"]), ("Brisbane", "Australia", ["brisbane"]), ("Perth", "Australia", ["perth"]), ("Adelaide", "Australia", ["adelaide"]),
    ("Queensland", "Australia", ["queensland"]), ("New South Wales", "Australia", ["new south wales", "nsw"]), ("Victoria (AU)", "Australia", ["victoria police"]), ("Auckland", "New Zealand", ["auckland"]),
    ("Wellington", "New Zealand", ["wellington"]), ("Christchurch", "New Zealand", ["christchurch"]),
    # --- Africa
    ("Johannesburg", "South Africa", ["johannesburg", "joburg", "gauteng"]), ("Durban", "South Africa", ["durban", "kwazulu-natal", "kzn"]), ("Cape Town", "South Africa", ["cape town", "western cape"]),
    ("Nairobi", "Kenya", ["nairobi"]), ("Mombasa", "Kenya", ["mombasa"]), ("Accra", "Ghana", ["accra", "tema"]), ("Kumasi", "Ghana", ["kumasi"]), ("Dakar", "Senegal", ["dakar", "ouakam"]),
    ("Abidjan", "Ivory Coast", ["abidjan"]), ("Lome", "Togo", ["lome"]), ("Cotonou", "Benin", ["cotonou"]), ("Dar es Salaam", "Tanzania", ["dar es salaam"]), ("Kampala", "Uganda", ["kampala", "entebbe"]),
    ("Tamanrasset", "Algeria", ["tamanrasset"]), ("Oran", "Algeria", ["oran"]), ("Marrakech", "Morocco", ["marrakech", "marrakesh"]), ("Casablanca", "Morocco", ["casablanca"]), ("Tangier", "Morocco", ["tanger", "tangier"]),
    # --- Europe extras
    ("Saint-Etienne", "France", ["saint-etienne"]), ("Marseille", "France", ["marseille"]), ("Lyon", "France", ["lyon"]), ("Toulouse", "France", ["toulouse"]), ("Le Havre", "France", ["le havre"]),
    ("Ampfing", "Germany", ["ampfing", "bavaria", "bayern"]), ("Hamburg", "Germany", ["hamburg"]), ("Rotterdam", "Netherlands", ["rotterdam"]), ("Antwerp", "Belgium", ["antwerp", "anvers", "antwerpen"]),
    ("Bishkek", "Kyrgyzstan", ["bishkek", "issyk-kul", "issyk kul"]), ("Pristina", "Kosovo", ["pristina", "prishtina"]), ("Belgrade", "Serbia", ["belgrade"]),
    ("Istanbul", "Turkey", ["istanbul"]), ("Erzincan", "Turkey", ["erzincan"]), ("Cairo", "Egypt", ["cairo"]), ("Dubai", "United Arab Emirates", ["dubai"]), ("Riyadh", "Saudi Arabia", ["riyadh"]),
]

# (regex on accent-stripped lower-case text, country). Used only when no place or country is named.
CUES = [
    # police, customs and drug agencies
    (r"\b(?:ndlea|nafdac|nigeria customs|nscdc)\b", "Nigeria"),
    (r"\b(?:rcmp|cbsa|opp|wrps|vpd|ottawa police|toronto police|peel police|surete du quebec)\b", "Canada"),
    (r"\b(?:border patrol|usbp|cbp|u\.s\. customs|us customs|dea|hsi|homeland security investigations|fbi|atf|ice agents|us marshals|sheriff|deputies|state troopers|highway patrol|hcso|sjcso|lmpd|nypd|lapd)\b", "United States"),
    (r"\b[a-z]+ county\b(?! (?:meath|cork|kerry|louth|galway|kildare|wexford|dublin|donegal|mayo|clare|limerick|waterford))", "United States"),
    (r"\b(?:pdea|pnp|bureau of customs|naia|philippine coast guard|pcg)\b", "Philippines"),
    (r"\b(?:garda|gardai|revenue commissioners)\b", "Ireland"),
    (r"\b(?:national crime agency|border force|hmrc|met police|scotland yard)\b", "United Kingdom"),
    (r"\b(?:australian border force|australian federal police)\b", "Australia"),
    (r"\b(?:narcotics control bureau|ncb|dri|directorate of revenue intelligence|bsf|ncb officials)\b", "India"),
    (r"\b(?:pdrm|aadk|royal malaysia police|kastam|jabatan kastam)\b", "Malaysia"),
    (r"\b(?:bnn|polri)\b", "Indonesia"),
    (r"\b(?:prf|policia rodoviaria federal|receita federal)\b", "Brazil"),
    (r"\b(?:dian|policia antinarcoticos)\b", "Colombia"),
    (r"\b(?:guardia civil|policia nacional|mossos)\b", "Spain"),
    (r"\b(?:sanepa|sunat|digemid)\b", "Peru"),
    (r"\b(?:sedena|guardia nacional|fgr|semar)\b", "Mexico"),
    (r"\b(?:sars|saps)\b", "South Africa"),
    # Dutch / Flemish agencies (used only when the text names no place or country)
    (r"\b(?:federale gerechtelijke politie|federale politie|politiezone|douane antwerpen|parket antwerpen|vlaamse politie)\b", "Belgium"),
    (r"\b(?:koninklijke marechaussee|kmar|fiod|openbaar ministerie|nederlandse douane|belastingdienst)\b", "Netherlands"),
    # Nordic, Baltic, Slovak and Austrian agencies
    (r"\b(?:tolletaten|tollvesenet|kripos|politidistrikt|oslo politidistrikt)\b", "Norway"),
    (r"\b(?:tullverket|polismyndigheten|polisregion|kustbevakningen)\b", "Sweden"),
    (r"\b(?:rigspolitiet|skattestyrelsen|told ?skat|koebenhavns politi|københavns politi)\b", "Denmark"),
    (r"\b(?:maksu- ja tolliamet|emta|politsei- ja piirivalveamet)\b", "Estonia"),
    (r"\b(?:financna sprava|financnej spravy|policajny zbor|policajt\w*|colnic\w*|colna sprava)\b", "Slovakia"),
    (r"\b(?:tollg(?:ae|æ)sla\w*|logreglan|rikislogreglustjori|landhelgisg(?:ae|æ)slan)\b", "Iceland"),
    (r"\b(?:suchtgift|bundeskriminalamt|landespolizeidirektion|zollamt (?:wien|salzburg|graz|linz|innsbruck))\b", "Austria"),
    (r"\b(?:anti-narcotics force|anf)\b", "Pakistan"),
    (r"\b(?:bgb|dnc bangladesh|rab)\b", "Bangladesh"),
    # currencies written next to an amount
    (r"\brm ?\d|\bringgit\b", "Malaysia"),
    (r"\b(?:crore|lakh)\b|₹|\brs\.? ?\d", "India"),
    (r"₦|\bnaira\b", "Nigeria"),
    (r"₱|\bphp ?\d", "Philippines"),
    (r"\bbaht\b", "Thailand"),
    (r"\brupiah\b|\brp ?\d", "Indonesia"),
    (r"\ba\$ ?\d|\baud ?\d", "Australia"),
    (r"\bc\$ ?\d|\bcad ?\d", "Canada"),
    (r"£ ?\d", "United Kingdom"),
    (r"\bshabu\b|\bp\d[\d,.]*\s?(?:k|m|million|billion)?\b(?= worth| of| in)", "Philippines"),
    (r"\bn\d[\d,.]*\s?(?:bn|m|million|billion|trillion)\b", "Nigeria"),
    (r"\bshekels?\b", "Israel"),
    (r"\bride stop\b|\bont\.|\bb\.c\.|\balta\.", "Canada"),
    (r"\b\d[\d,.]* pounds\b|\bpounds of\b", "United States"),
    (r"\bfj\$|\bfijian\b|\bfiji\b", "Fiji"),
]

# Languages that are in practice spoken in one country of our sources; used only when the text names no place at all
LANG_COUNTRY = {"tr": "Turkey", "hi": "India", "vi": "Vietnam", "et": "Estonia", "sk": "Slovakia", "is": "Iceland", "mn": "Mongolia",
                "am": "Ethiopia", "da": "Denmark", "sv": "Sweden", "no": "Norway"}
