# -*- coding: utf-8 -*-
"""Examination prompts for an officer, built from the indicators a report shows.

The dashboard builds the checklist for any event in the browser: it takes the indicators that fired
(risk flags), how the goods were hidden, the transport mode and the category, and lists the matching
prompts below. The wording is general good-practice guidance written for this tool, in the style of
risk-indicator cards. It is NOT official PCCP, WCO or UNODC material, and it is a starting point for
a trained officer's judgement, never a substitute for it or for local procedures and the law.
"""

# keyed by the risk-flag labels in analyze.FLAG_LABELS
FLAGS = {
    "Container cargo": [
        "Compare container number, seal number and gross weight across the booking, manifest and gate record. A seal replaced after loading or a weight that does not match is a reason to open it.",
        "Look at the container's movement history for unusual transhipment, a change of destination or a long unexplained stop.",
        "Compare the scanner image with the declared goods. If the density or layout does not fit, devanning and a physical check of the walls, roof and floor are justified.",
    ],
    "Hidden in legitimate cargo": [
        "Check the declared goods against the shipper's normal trade. A new company, a shell company or an unrelated business is a warning sign.",
        "Look past the top layer: weigh and sample the cover cargo, and check for uneven packing, extra layers, odd smell or packaging that does not match the goods.",
        "For refrigerated or perishable cargo, check temperature records and whether the load really needs the declared handling.",
    ],
    "Advanced concealment": [
        "Look for signs of modification: fresh welding, paint or sealant, new panels, or inside dimensions that are shorter than the outside.",
        "Use a density meter, fibre-scope, X-ray or a detector dog on walls, floors, roof and fittings before cutting anything.",
        "For impregnated or liquid concealment, test fabrics, plastics and liquids with field test kits and look for unusual weight, odour or residue.",
    ],
    "Large quantity": [
        "Prepare for a large find: secure the area, record every step, and consider a controlled delivery before the seizure becomes known.",
        "Check whether other containers or consignments from the same shipper, consignee or vessel are in the port or on the same voyage.",
    ],
    "Multi-country route": [
        "Review the full routing and every transhipment point. A hub added for no commercial reason, or a route that avoids a direct option, deserves a closer look.",
        "Ask partner customs for information on the earlier legs of the journey through the established channels.",
    ],
    "Emerging corridor": [
        "Treat the origin-destination pair as unfamiliar: check that the trade lane fits the shipper's history and the type of goods.",
        "Tell neighbouring ports and the regional analysis unit about the new pattern to see whether they see it too.",
    ],
    "Organised network": [
        "Look for links between shipper, consignee, forwarder and broker in earlier shipments, and share them with your analysis or intelligence unit.",
    ],
    "Insider indicator": [
        "Review access logs, gate passes and CCTV for the time the container or consignment was in the facility. Check out-of-hours handling and access by staff who were not rostered.",
        "Check whether the unit was moved or lifted without a matching paper trail, which can point to a rip-on/rip-off.",
        "Use the integrity or security reporting channel, and limit who knows about the examination in advance.",
    ],
    "Multiple drugs": [
        "Expect mixed substances: use different field tests, keep the substances separate, and record each one.",
    ],
}

# keyed by the concealment categories in lexicon.CONCEALMENT
CONCEAL = {
    "Legitimate cargo (food/produce)": [
        "Open boxes and pallets at several depths, not just the top. Check the produce against the season, the origin and the temperature records.",
    ],
    "Legitimate cargo (industrial/goods)": [
        "Check machinery, building materials and bulk goods for cavities, new fillers or weight that is out of line with the volume.",
    ],
    "Container structure / false compartment": [
        "Measure the inside against the outside dimensions and look at the doors, the floor beams and the roof for added panels or fresh work.",
    ],
    "Vehicle compartment": [
        "Check fuel tanks, spare wheels, door and roof panels, bumpers and the chassis. A density meter or scanner helps before dismantling.",
    ],
    "Body concealment": [
        "Follow your agency's procedures and the law for body searches and medical screening, and involve qualified staff.",
    ],
    "Postal / parcel": [
        "Compare the sender, addressee and declared contents with the weight and the packaging. Repeated small parcels to the same address are worth linking.",
    ],
    "Luggage / passenger goods": [
        "Compare the traveller's route, stay length and baggage with the story given. Check the lining, the frame and the sealed goods inside the luggage.",
    ],
    "Impregnation / liquid / disguised": [
        "Test unusual fabrics, plastics, liquids and drinks with field test kits. Look for goods that are heavier or smell different from what is declared.",
    ],
    "Vessel hull / underwater": [
        "Ask for an underwater or hull inspection (divers or ROV) and check sea chests and external fittings, in line with the port's procedures.",
    ],
}

TRANSPORT = {
    "Sea - container": ["Check the full container journey, the shipping line and the booking party, and the time between loading and arrival."],
    "Sea - cargo (other)": ["Check the cargo manifest, crew and vessel history, and any unusual stops on the voyage."],
    "Sea - vessel/small craft": ["Check the vessel's recent track, crew and ownership, and any rendezvous at sea."],
    "Air - passenger": ["Cross-check the passenger's itinerary and booking details, and compare the baggage with the trip."],
    "Air": ["Check the air waybill, consignee and handling agent, and the timing between check-in and loading."],
    "Post/express": ["Link the sender and addressee across parcels, and check the declared contents against weight and value."],
    "Road": ["Check driver documents, trailer seals, the route against the delivery order, and the tachograph for unexplained stops."],
    "Rail": ["Check the wagon numbers, consignee and the route against the consignment note."],
}

CATEGORY = {
    "Arms and ammunition": [
        "Check export and end-user certificates and licence numbers with the issuing authority. Look for serial numbers that have been removed or altered.",
        "Compare the declared goods with the packing, since components are often shipped as ordinary parts or spares.",
    ],
    "Precursor chemical": [
        "Check the licence, the end-use declaration and the buyer's legitimate business. Compare the quantity with plausible industrial use.",
        "Send a sample for laboratory identification and notify the competent national authority and the regional contact point.",
    ],
    "Hazardous chemical": [
        "Wear the right protective equipment. Do not open unknown containers without a hazardous-materials procedure, and involve the competent authority.",
    ],
    "Stolen vehicle": [
        "Check the VIN and engine number against national and international stolen-vehicle databases, and look for altered or re-stamped plates.",
    ],
    "CITES elephant ivory": [
        "Ask for CITES permits and check them with the issuing management authority. Look for worked or antique claims that do not fit the material.",
        "Keep the evidence intact for identification and, where possible, DNA or age testing.",
    ],
    "CITES protected fauna": [
        "Ask for CITES permits and check them with the management authority. Involve a specialist for live animals and arrange safe care.",
    ],
    "CITES protected timber": [
        "Check the CITES permit and the species declared against the wood. Look at the end-grain and take samples for identification.",
    ],
    "Cultural heritage": [
        "Ask for the export licence and provenance papers. Check the item against stolen-art databases and involve a cultural-heritage expert.",
    ],
}


def model():
    """The checklist rules the dashboard uses (sent once as part of the page data)."""
    return {"flags": FLAGS, "conceal": CONCEAL, "transport": TRANSPORT, "category": CATEGORY,
            "note": "General guidance written for this tool. It is not official PCCP, WCO or UNODC material and does not replace "
                    "local procedures, training or the law."}
