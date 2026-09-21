# -*- coding: utf-8 -*-
"""Map coordinates (latitude, longitude) for the countries and places the reader knows. Used by the dashboard maps.
Add a place to lexicon.py AND here to see it on the map (a place without coordinates falls back to its country)."""
COUNTRY = {
"Afghanistan": [33.9,
67.7],
"Albania": [41.2,
20.2],
"Algeria": [28.0,
2.6],
"Angola": [-11.2,
17.9],
"Argentina": [-38.4,
-63.6],
"Armenia": [40.1,
45.0],
"Australia": [-25.3,
133.8],
"Austria": [47.5,
14.6],
"Azerbaijan": [40.1,
47.6],
"Bahamas": [25.0,
-77.4],
"Bahrain": [26.0,
50.55],
"Bangladesh": [23.7,
90.4],
"Belarus": [53.7,
27.9],
"Belgium": [50.5,
4.5],
"Benin": [9.3,
2.3],
"Bolivia": [-16.3,
-63.6],
"Bosnia and Herzegovina": [43.9,
17.7],
"Brazil": [-14.2,
-51.9],
"Bulgaria": [42.7,
25.5],
"Burkina Faso": [12.2,
-1.6],
"Cambodia": [12.6,
104.9],
"Cameroon": [7.4,
12.4],
"Canada": [56.1,
-106.3],
"Cape Verde": [16.0,
-24.0],
"Chile": [-35.7,
-71.5],
"China": [35.9,
104.2],
"Colombia": [4.6,
-74.1],
"Congo": [-2.9,
23.7],
"Costa Rica": [9.7,
-83.8],
"Croatia": [45.1,
15.2],
"Cuba": [21.5,
-77.8],
"Curacao": [12.17,
-69.0],
"Cyprus": [35.1,
33.4],
"Czech Republic": [49.8,
15.5],
"Denmark": [56.3,
9.5],
"Dominican Republic": [18.7,
-70.2],
"Ecuador": [-1.8,
-78.2],
"Egypt": [26.8,
30.8],
"El Salvador": [13.8,
-88.9],
"Equatorial Guinea": [1.65,
10.27],
"Estonia": [58.6,
25.0],
"Ethiopia": [9.1,
40.5],
"Finland": [61.9,
25.7],
"France": [46.2,
2.2],
"French Guiana": [3.9,
-53.1],
"Gambia": [13.4,
-15.3],
"Germany": [51.2,
10.4],
"Ghana": [7.95,
-1.0],
"Greece": [39.1,
21.8],
"Guadeloupe": [16.25,
-61.55],
"Guatemala": [15.8,
-90.2],
"Guinea": [9.9,
-9.7],
"Guinea-Bissau": [11.8,
-15.2],
"Guyana": [4.9,
-58.9],
"Haiti": [18.97,
-72.3],
"Honduras": [15.2,
-86.2],
"Hong Kong": [22.32,
114.17],
"Hungary": [47.2,
19.5],
"Iceland": [64.96,
-19.0],
"India": [20.6,
78.96],
"Indonesia": [-0.8,
113.9],
"Iran": [32.4,
53.7],
"Iraq": [33.2,
43.7],
"Ireland": [53.4,
-8.2],
"Israel": [31.0,
34.9],
"Italy": [41.9,
12.6],
"Ivory Coast": [7.5,
-5.5],
"Jamaica": [18.1,
-77.3],
"Japan": [36.2,
138.3],
"Jordan": [30.6,
36.2],
"Kazakhstan": [48.0,
66.9],
"Kenya": [-0.02,
37.9],
"Kosovo": [42.6,
20.9],
"Kuwait": [29.3,
47.5],
"Kyrgyzstan": [41.2,
74.8],
"Laos": [19.9,
102.5],
"Latvia": [56.9,
24.6],
"Lebanon": [33.85,
35.86],
"Liberia": [6.4,
-9.4],
"Libya": [26.3,
17.2],
"Lithuania": [55.2,
23.9],
"Luxembourg": [49.8,
6.1],
"Madagascar": [-18.8,
46.9],
"Malaysia": [4.2,
101.98],
"Maldives": [3.2,
73.2],
"Mali": [17.6,
-4.0],
"Malta": [35.9,
14.4],
"Martinique": [14.6,
-61.0],
"Mauritania": [21.0,
-10.9],
"Mauritius": [-20.3,
57.55],
"Mexico": [23.6,
-102.6],
"Moldova": [47.4,
28.4],
"Mongolia": [46.9,
103.8],
"Montenegro": [42.7,
19.4],
"Morocco": [31.8,
-7.1],
"Mozambique": [-18.7,
35.5],
"Myanmar": [21.9,
95.96],
"Namibia": [-22.96,
18.5],
"Nepal": [28.4,
84.1],
"Netherlands": [52.1,
5.3],
"New Zealand": [-40.9,
174.9],
"Nicaragua": [12.9,
-85.2],
"Niger": [17.6,
8.1],
"Nigeria": [9.1,
8.7],
"North Macedonia": [41.6,
21.7],
"Norway": [60.5,
8.5],
"Oman": [21.5,
55.9],
"Pakistan": [30.4,
69.3],
"Panama": [8.5,
-80.8],
"Papua New Guinea": [-6.3,
143.96],
"Paraguay": [-23.4,
-58.4],
"Peru": [-9.2,
-75.0],
"Philippines": [12.9,
121.8],
"Poland": [51.9,
19.1],
"Portugal": [39.4,
-8.2],
"Puerto Rico": [18.2,
-66.6],
"Qatar": [25.35,
51.2],
"Romania": [45.9,
25.0],
"Russia": [61.5,
105.3],
"Rwanda": [-1.9,
29.9],
"Saudi Arabia": [23.9,
45.1],
"Senegal": [14.5,
-14.5],
"Serbia": [44.0,
21.0],
"Sierra Leone": [8.5,
-11.8],
"Singapore": [1.35,
103.8],
"Slovakia": [48.7,
19.7],
"Slovenia": [46.15,
14.99],
"Somalia": [5.15,
46.2],
"South Africa": [-30.6,
22.9],
"South Korea": [35.9,
127.8],
"Spain": [40.5,
-3.7],
"Sri Lanka": [7.9,
80.8],
"Sudan": [12.9,
30.2],
"Suriname": [3.9,
-56.0],
"Sweden": [60.1,
18.6],
"Switzerland": [46.8,
8.2],
"Syria": [34.8,
38.99],
"Taiwan": [23.7,
121.0],
"Tajikistan": [38.9,
71.3],
"Tanzania": [-6.4,
34.9],
"Thailand": [15.9,
100.99],
"Togo": [8.6,
0.8],
"Trinidad and Tobago": [10.7,
-61.2],
"Tunisia": [33.9,
9.5],
"Turkey": [38.96,
35.2],
"Turkmenistan": [38.97,
59.6],
"Uganda": [1.4,
32.3],
"Ukraine": [48.4,
31.2],
"United Arab Emirates": [23.4,
53.8],
"United Kingdom": [54.0,
-2.5],
"United States": [39.8,
-98.6],
"Uruguay": [-32.5,
-55.8],
"Uzbekistan": [41.4,
64.6],
"Venezuela": [6.4,
-66.6],
"Vietnam": [14.06,
108.3],
"Yemen": [15.55,
48.5],
"Zambia": [-13.1,
27.85],
"Zimbabwe": [-19.0,
29.15]
}

PLACE = {"Saint Petersburg": [59.93, 30.32], "Novorossiysk": [44.72, 37.77], "Vladivostok": [43.12, 131.89], "Odesa": [46.48, 30.73], "Sheremetyevo airport": [55.97, 37.41], "Domodedovo airport": [55.41, 37.91], "Almaty": [43.24, 76.89], "Tashkent": [41.3, 69.24], 
"Abidjan": [
5.32,
-4.02
],
"Algeciras": [
36.13,
-5.45
],
"Antwerp": [
51.26,
4.4
],
"Aqaba": [
29.53,
35.0
],
"Bandar Abbas": [
27.18,
56.27
],
"Beirut": [
33.9,
35.5
],
"Buenaventura": [
3.88,
-77.03
],
"Buenos Aires": [
-34.6,
-58.4
],
"Busan": [
35.1,
129.04
],
"Callao": [
-12.05,
-77.15
],
"Caucedo": [
18.43,
-69.63
],
"Colombo": [
6.95,
79.85
],
"Colon / Balboa": [
9.35,
-79.9
],
"Constanta": [
44.17,
28.65
],
"Cotonou": [
6.36,
2.43
],
"Dakar": [
14.68,
-17.43
],
"Dar es Salaam": [
-6.82,
39.29
],
"Durban": [
-29.87,
31.03
],
"Felixstowe": [
51.96,
1.35
],
"Freeport": [
26.53,
-78.7
],
"Gdansk / Gdynia": [
54.4,
18.6
],
"Gioia Tauro": [
38.43,
15.9
],
"Gothenburg": [
57.7,
11.9
],
"Guayaquil": [
-2.2,
-79.9
],
"Hamburg": [
53.55,
9.97
],
"Ho Chi Minh City": [
10.78,
106.7
],
"Jakarta": [
-6.1,
106.85
],
"Jebel Ali": [
25.0,
55.06
],
"Karachi": [
24.85,
67.0
],
"Kingston": [
17.97,
-76.79
],
"Koper": [
45.55,
13.73
],
"Laem Chabang": [
13.08,
100.88
],
"Lagos": [
6.45,
3.4
],
"Latakia": [
35.52,
35.78
],
"Lazaro Cardenas": [
17.96,
-102.2
],
"Le Havre": [
49.49,
0.11
],
"Lome": [
6.13,
1.22
],
"Manila": [
14.6,
120.97
],
"Mersin": [
36.8,
34.63
],
"Mombasa": [
-4.05,
39.67
],
"Montevideo": [
-34.9,
-56.2
],
"Nhava Sheva / Mundra": [
18.95,
72.95
],
"Paramaribo": [
5.85,
-55.2
],
"Piraeus": [
37.94,
23.64
],
"Port Everglades": [
26.09,
-80.12
],
"Port Klang": [
3.0,
101.4
],
"Port Said": [
31.26,
32.3
],
"Port of Spain": [
10.65,
-61.5
],
"Puerto Cortes": [
15.84,
-87.95
],
"Puerto Limon": [
9.99,
-83.03
],
"Rijeka": [
45.33,
14.44
],
"Rotterdam": [
51.95,
4.14
],
"Santos": [
-23.96,
-46.33
],
"Shanghai": [
31.23,
121.47
],
"Sines / Lisbon": [
38.7,
-9.14
],
"Sydney": [
-33.87,
151.2
],
"Tanger Med": [
35.89,
-5.5
],
"Tauranga": [
-37.65,
176.17
],
"Tema": [
5.62,
0.02
],
"Valparaiso / Iquique": [
-33.05,
-71.62
],
"Vancouver": [
49.29,
-123.1
],
"Varna / Burgas": [
43.2,
27.93
],
"OR Tambo / Johannesburg": [
-26.13,
28.24
],
"Cape Town": [
-33.92,
18.42
],
"Accra": [
5.6,
-0.19
],
"Kumasi": [
6.69,
-1.62
],
"Abuja": [
9.06,
7.49
],
"Kano": [
12.0,
8.52
],
"Port Harcourt": [
4.82,
7.03
],
"Ogun": [
7.0,
3.35
],
"Nairobi": [
-1.29,
36.82
],
"Addis Ababa": [
9.03,
38.74
],
"Kigali": [
-1.95,
30.06
],
"Kampala / Entebbe": [
0.35,
32.58
],
"Casablanca": [
33.57,
-7.59
],
"Cairo": [
30.04,
31.24
],
"Freetown": [
8.48,
-13.23
],
"Conakry": [
9.64,
-13.58
],
"Luanda": [
-8.84,
13.23
],
"Maputo": [
-25.97,
32.57
],
"Lusaka": [
-15.39,
28.32
],
"Harare": [
-17.83,
31.05
],
"Windhoek": [
-22.56,
17.08
],
"Tunis": [
36.8,
10.18
],
"Algiers": [
36.75,
3.06
],
"Bamako": [
12.64,
-8.0
],
"Niamey": [
13.51,
2.11
],
"Ouagadougou": [
12.37,
-1.52
],
"Douala": [
4.05,
9.7
],
"Kinshasa": [
-4.44,
15.27
],
"Antananarivo": [
-18.88,
47.51
],
"Port Louis": [
-20.16,
57.5
],
"Khartoum": [
15.5,
32.56
],
"Mogadishu": [
2.05,
45.32
],
"Doha": [
25.29,
51.53
],
"Dubai": [
25.2,
55.27
],
"Abu Dhabi": [
24.45,
54.38
],
"Riyadh": [
24.71,
46.68
],
"Jeddah": [
21.5,
39.17
],
"Tehran": [
35.69,
51.39
],
"Baghdad": [
33.31,
44.36
],
"Amman": [
31.95,
35.93
],
"Tel Aviv": [
32.09,
34.78
],
"Istanbul": [
41.01,
28.98
],
"Ankara": [
39.93,
32.86
],
"Kabul": [
34.53,
69.17
],
"Islamabad": [
33.69,
73.05
],
"Lahore": [
31.55,
74.34
],
"Peshawar": [
34.01,
71.58
],
"Quetta": [
30.18,
66.99
],
"Delhi": [
28.61,
77.21
],
"Mumbai": [
19.08,
72.88
],
"Kolkata": [
22.57,
88.36
],
"Chennai": [
13.08,
80.27
],
"Bengaluru": [
12.97,
77.59
],
"Hyderabad": [
17.39,
78.49
],
"Amritsar": [
31.63,
74.87
],
"Ludhiana": [
30.9,
75.85
],
"Jalandhar": [
31.33,
75.58
],
"Sri Ganganagar": [
29.92,
73.88
],
"Mizoram": [
23.2,
92.9
],
"Manipur": [
24.7,
93.9
],
"Assam": [
26.2,
92.9
],
"Meghalaya": [
25.5,
91.4
],
"Nagaland": [
26.2,
94.6
],
"Tripura": [
23.8,
91.7
],
"Gujarat": [
22.3,
71.2
],
"Rajasthan": [
26.9,
74.2
],
"Haryana": [
29.1,
76.1
],
"Uttar Pradesh": [
26.8,
80.9
],
"Kerala": [
10.5,
76.3
],
"Karnataka": [
15.3,
75.7
],
"Tamil Nadu": [
11.1,
78.7
],
"Maharashtra": [
19.7,
75.7
],
"Odisha": [
20.9,
84.0
],
"Bihar": [
25.1,
85.3
],
"West Bengal": [
22.9,
87.9
],
"Jammu and Kashmir": [
33.8,
76.6
],
"Himachal Pradesh": [
31.9,
77.2
],
"Uttarakhand": [
30.1,
79.3
],
"Madhya Pradesh": [
23.5,
78.0
],
"Kathmandu": [
27.72,
85.32
],
"Dhaka": [
23.81,
90.41
],
"Bangkok": [
13.75,
100.5
],
"Kuala Lumpur": [
3.14,
101.69
],
"Yangon": [
16.87,
96.2
],
"Shan State": [
21.5,
98.0
],
"Hanoi": [
21.03,
105.85
],
"Phnom Penh": [
11.56,
104.92
],
"Vientiane": [
17.97,
102.6
],
"Cebu": [
10.32,
123.89
],
"Davao": [
7.19,
125.46
],
"Zamboanga": [
6.91,
122.08
],
"Mindanao": [
8.0,
125.0
],
"Tokyo": [
35.68,
139.69
],
"Osaka": [
34.69,
135.5
],
"Seoul": [
37.57,
126.98
],
"Beijing": [
39.9,
116.4
],
"Guangzhou": [
23.13,
113.26
],
"Taipei": [
25.03,
121.57
],
"Hong Kong airport": [
22.31,
113.91
],
"Dunkirk": [
51.03,
2.38
],
"Paris": [
48.86,
2.35
],
"Lyon": [
45.76,
4.84
],
"Amsterdam": [
52.37,
4.9
],
"Brussels": [
50.85,
4.35
],
"Frankfurt": [
50.11,
8.68
],
"Munich": [
48.14,
11.58
],
"Berlin": [
52.52,
13.4
],
"Madrid": [
40.42,
-3.7
],
"Barcelona": [
41.39,
2.17
],
"Malaga": [
36.72,
-4.42
],
"Rome": [
41.9,
12.5
],
"Milan": [
45.46,
9.19
],
"Vienna": [
48.21,
16.37
],
"Zurich": [
47.38,
8.54
],
"Prague": [
50.08,
14.42
],
"Warsaw": [
52.23,
21.01
],
"Athens": [
37.98,
23.73
],
"Sofia": [
42.7,
23.32
],
"Bucharest": [
44.43,
26.1
],
"Belgrade": [
44.8,
20.46
],
"Budapest": [
47.5,
19.04
],
"Moscow": [
55.76,
37.62
],
"Kyiv": [
50.45,
30.52
],
"Copenhagen": [
55.68,
12.57
],
"Stockholm": [
59.33,
18.07
],
"Oslo": [
59.91,
10.75
],
"Helsinki": [
60.17,
24.94
],
"London": [
51.51,
-0.13
],
"Manchester": [
53.48,
-2.24
],
"Birmingham": [
52.49,
-1.89
],
"Liverpool": [
53.41,
-2.99
],
"Glasgow": [
55.86,
-4.25
],
"Edinburgh": [
55.95,
-3.19
],
"Belfast": [
54.6,
-5.93
],
"Cardiff": [
51.48,
-3.18
],
"Scotland": [
56.5,
-4.2
],
"Wales": [
52.3,
-3.7
],
"Dublin": [
53.35,
-6.26
],
"Cork": [
51.9,
-8.47
],
"Galway": [
53.27,
-9.05
],
"Alabama": [
32.8,
-86.8
],
"Alaska": [
64.0,
-152.0
],
"Arizona": [
34.2,
-111.7
],
"Arkansas": [
34.9,
-92.4
],
"California": [
37.2,
-119.5
],
"Colorado": [
39.0,
-105.5
],
"Connecticut": [
41.6,
-72.7
],
"Delaware": [
39.0,
-75.5
],
"Florida": [
28.6,
-82.4
],
"Hawaii": [
20.8,
-156.3
],
"Idaho": [
44.4,
-114.6
],
"Illinois": [
40.0,
-89.2
],
"Indiana": [
39.9,
-86.3
],
"Iowa": [
42.1,
-93.5
],
"Kansas": [
38.5,
-98.4
],
"Kentucky": [
37.5,
-85.3
],
"Louisiana": [
31.0,
-92.0
],
"Maine": [
45.3,
-69.2
],
"Maryland": [
39.0,
-76.8
],
"Massachusetts": [
42.3,
-71.8
],
"Michigan": [
44.3,
-85.4
],
"Minnesota": [
46.3,
-94.3
],
"Mississippi": [
32.7,
-89.7
],
"Missouri": [
38.4,
-92.5
],
"Montana": [
47.0,
-109.6
],
"Nebraska": [
41.5,
-99.8
],
"Nevada": [
39.3,
-116.6
],
"New Hampshire": [
43.7,
-71.6
],
"New Jersey": [
40.2,
-74.7
],
"New Mexico": [
34.4,
-106.1
],
"New York": [
42.9,
-75.5
],
"North Carolina": [
35.5,
-79.4
],
"North Dakota": [
47.5,
-100.5
],
"Ohio": [
40.4,
-82.8
],
"Oklahoma": [
35.6,
-97.5
],
"Oregon": [
44.0,
-120.5
],
"Pennsylvania": [
40.9,
-77.8
],
"Rhode Island": [
41.7,
-71.5
],
"South Carolina": [
33.9,
-80.9
],
"South Dakota": [
44.4,
-100.2
],
"Tennessee": [
35.9,
-86.4
],
"Texas": [
31.5,
-99.3
],
"Utah": [
39.3,
-111.7
],
"Vermont": [
44.0,
-72.7
],
"Virginia": [
37.5,
-78.8
],
"Washington": [
47.4,
-120.5
],
"West Virginia": [
38.6,
-80.6
],
"Wisconsin": [
44.6,
-89.9
],
"Wyoming": [
43.0,
-107.5
],
"Chicago": [
41.88,
-87.63
],
"Houston": [
29.76,
-95.37
],
"Dallas": [
32.78,
-96.8
],
"Atlanta": [
33.75,
-84.39
],
"Seattle": [
47.61,
-122.33
],
"Boston": [
42.36,
-71.06
],
"Detroit": [
42.33,
-83.05
],
"Phoenix": [
33.45,
-112.07
],
"Denver": [
39.74,
-104.99
],
"Las Vegas": [
36.17,
-115.14
],
"San Francisco": [
37.77,
-122.42
],
"Miami": [
25.76,
-80.19
],
"Baltimore": [
39.29,
-76.61
],
"Fresno": [
36.74,
-119.79
],
"Bakersfield": [
35.37,
-119.02
],
"Sacramento": [
38.58,
-121.49
],
"Tucson": [
32.22,
-110.97
],
"El Paso": [
31.76,
-106.49
],
"British Columbia": [
53.7,
-127.6
],
"Ontario": [
50.0,
-85.0
],
"Alberta": [
54.5,
-115.0
],
"Quebec": [
52.0,
-72.0
],
"Manitoba": [
55.0,
-98.0
],
"Saskatchewan": [
54.0,
-106.0
],
"Nova Scotia": [
45.0,
-63.0
],
"Toronto": [
43.65,
-79.38
],
"Calgary": [
51.05,
-114.07
],
"Edmonton": [
53.55,
-113.49
],
"Ottawa": [
45.42,
-75.7
],
"Winnipeg": [
49.9,
-97.14
],
"New South Wales": [
-32.0,
147.0
],
"Queensland": [
-22.0,
144.0
],
"Western Australia": [
-26.0,
121.0
],
"South Australia": [
-30.0,
135.0
],
"Tasmania": [
-42.0,
146.6
],
"Perth": [
-31.95,
115.86
],
"Adelaide": [
-34.93,
138.6
],
"Canberra": [
-35.28,
149.13
],
"Darwin": [
-12.46,
130.84
],
"Wellington": [
-41.29,
174.78
],
"Mexico City": [
19.43,
-99.13
],
"Michoacan": [
19.2,
-101.9
],
"Guerrero": [
17.6,
-99.9
],
"Sinaloa": [
25.0,
-107.5
],
"Sonora": [
29.3,
-110.3
],
"Jalisco": [
20.6,
-103.6
],
"Chihuahua": [
28.8,
-106.4
],
"Tijuana": [
32.51,
-117.04
],
"Tamaulipas": [
24.3,
-98.6
],
"Monterrey": [
25.67,
-100.31
],
"Oaxaca": [
17.0,
-96.7
],
"Chiapas": [
16.5,
-92.5
],
"Manzanillo": [
19.05,
-104.3
],
"Guatemala City": [
14.63,
-90.51
],
"Tegucigalpa": [
14.07,
-87.19
],
"San Salvador": [
13.69,
-89.19
],
"Managua": [
12.13,
-86.25
],
"Tocumen": [
9.07,
-79.38
],
"Bogota": [
4.71,
-74.07
],
"Medellin": [
6.24,
-75.58
],
"Cartagena": [
10.39,
-75.48
],
"Quito": [
-0.18,
-78.47
],
"Manta": [
-0.95,
-80.71
],
"Lima": [
-12.05,
-77.04
],
"Sao Paulo": [
-23.55,
-46.63
],
"Rio de Janeiro": [
-22.91,
-43.17
],
"Brasilia": [
-15.79,
-47.88
],
"Fortaleza": [
-3.73,
-38.53
],
"Recife": [
-8.05,
-34.88
],
"Caracas": [
10.48,
-66.9
],
"La Paz": [
-16.5,
-68.15
],
"Asuncion": [
-25.26,
-57.58
],
"Santiago": [
-33.45,
-70.67
],
"Havana": [
23.11,
-82.37
],
"Santo Domingo": [
18.49,
-69.93
],
"Port-au-Prince": [
18.54,
-72.34
],
"Nassau": [
25.05,
-77.35
],
"San Juan": [
18.47,
-66.11
],
"Posorja": [
-2.71,
-80.24
],
"Esmeraldas": [
0.98,
-79.65
],
"Puerto Bolivar": [
-3.26,
-79.99
],
"Santa Marta": [
11.24,
-74.2
],
"Barranquilla": [
10.96,
-74.8
],
"Tumaco": [
1.8,
-78.76
],
"Paita": [
-5.09,
-81.11
],
"Chancay": [
-11.57,
-77.27
],
"Paranagua": [
-25.52,
-48.51
],
"Itajai": [
-26.91,
-48.66
],
"Rio Grande": [
-32.03,
-52.1
],
"Suape": [
-8.39,
-34.97
],
"Pecem": [
-3.55,
-38.8
],
"Rosario": [
-32.95,
-60.64
],
"Cristobal": [
9.35,
-79.91
],
"Bocas del Toro": [
9.34,
-82.24
],
"Puerto Quetzal": [
13.93,
-90.79
],
"Santo Tomas de Castilla": [
15.7,
-88.61
],
"Puerto Moin": [
10.0,
-83.08
],
"Haina": [
18.42,
-70.03
],
"Point Lisas": [
10.4,
-61.48
],
"Willemstad": [
12.11,
-68.93
],
"Veracruz": [
19.2,
-96.13
],
"Altamira": [
22.4,
-97.93
],
"Ensenada": [
31.86,
-116.62
],
"Los Angeles": [
33.74,
-118.27
],
"Long Beach": [
33.75,
-118.19
],
"Oakland": [
37.8,
-122.28
],
"Savannah": [
32.08,
-81.09
],
"Charleston": [
32.78,
-79.93
],
"Norfolk": [
36.85,
-76.29
],
"Newark": [
40.68,
-74.15
],
"Philadelphia": [
39.95,
-75.14
],
"JFK airport": [
40.64,
-73.78
],
"LAX airport": [
33.94,
-118.41
],
"Marseille-Fos": [
43.4,
4.88
],
"Bremerhaven": [
53.55,
8.58
],
"Zeebrugge": [
51.33,
3.21
],
"Valencia": [
39.44,
-0.32
],
"Vigo": [
42.24,
-8.72
],
"Bilbao": [
43.35,
-3.03
],
"Las Palmas": [
28.14,
-15.41
],
"Tenerife": [
28.47,
-16.25
],
"Genoa": [
44.41,
8.93
],
"La Spezia": [
44.1,
9.83
],
"Livorno": [
43.55,
10.3
],
"Naples": [
40.84,
14.25
],
"Trieste": [
45.65,
13.77
],
"Salerno": [
40.68,
14.77
],
"Southampton": [
50.9,
-1.4
],
"London Gateway": [
51.5,
0.49
],
"Dover": [
51.13,
1.31
],
"Klaipeda": [
55.71,
21.13
],
"Riga": [
56.95,
24.1
],
"Tallinn": [
59.44,
24.75
],
"Leixoes": [
41.19,
-8.7
],
"Heathrow airport": [
51.47,
-0.45
],
"Gatwick airport": [
51.15,
-0.19
],
"Schiphol airport": [
52.31,
4.76
],
"Charles de Gaulle airport": [
49.01,
2.55
],
"Barajas airport": [
40.49,
-3.57
],
"Monrovia": [
6.3,
-10.8
],
"Banjul": [
13.45,
-16.58
],
"Nouakchott": [
18.09,
-15.98
],
"Bissau": [
11.86,
-15.6
],
"Takoradi": [
4.89,
-1.75
],
"Pointe-Noire": [
4.78,
11.86
],
"Walvis Bay": [
-22.96,
14.5
],
"Beira": [
-19.83,
34.84
],
"Nacala": [
-14.54,
40.68
],
"Khor Fakkan": [
25.34,
56.36
],
"Sharjah": [
25.35,
55.39
],
"Salalah": [
16.94,
54.0
],
"Sohar": [
24.35,
56.73
],
"Dammam": [
26.43,
50.1
],
"Izmir": [
38.44,
27.14
],
"Ambarli": [
40.97,
28.69
],
"Haifa": [
32.82,
34.99
],
"Ashdod": [
31.8,
34.65
],
"Umm Qasr": [
30.03,
47.93
],
"Chittagong": [
22.33,
91.83
],
"Tanjung Pelepas": [
1.36,
103.55
],
"Surabaya": [
-7.2,
112.73
],
"Haiphong": [
20.86,
106.68
],
"Ningbo": [
29.87,
121.55
],
"Shenzhen": [
22.54,
114.06
],
"Qingdao": [
36.07,
120.38
],
"Tianjin": [
39.08,
117.2
],
"Yokohama": [
35.44,
139.64
],
"Kaohsiung": [
22.62,
120.3
],
"Kandla": [
23.03,
70.22
],
"Tuticorin": [
8.76,
78.13
],
"Visakhapatnam": [
17.69,
83.22
],
"Gwadar": [
25.13,
62.33
],
"Melbourne": [
-37.81,
144.96
],
"Brisbane": [
-27.47,
153.03
],
"Fremantle": [
-32.06,
115.75
],
"Auckland": [
-36.85,
174.76
]
}


def payload(place_alias):
    """JSON-ready dict for the dashboard: countries, and places with their country."""
    disp2c = {d: c for d, c in place_alias.values()}
    return {"c": {k: list(v) for k, v in COUNTRY.items()},
            "p": {d: [*PLACE[d], disp2c[d]] for d in sorted(disp2c) if d in PLACE and disp2c[d] in COUNTRY}}
