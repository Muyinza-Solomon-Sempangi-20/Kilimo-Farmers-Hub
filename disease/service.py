import re
from .models import Disease

# Comprehensive Ugandan crop disease knowledge base
# Each entry: (disease_name, scientific_name, crop, symptoms_keywords, treatment, prevention, severity)
DISEASE_KB = [
    # Maize diseases
    ("Fall Armyworm", "Spodoptera frugiperda", "Maize",
     ["armyworm", "ragged", "hole", "whorl", "frass", "chewed", "eaten", "larvae", "caterpillar", "worm", "leaf damage", "maize worm"],
     "Apply Emamectin benzoate (0.5g/L) or Spinosad. Spray into the whorl for best results. Repeat after 10 days if needed.",
     "Use Push-Pull technology. Plant Desmodium as intercrop. Monitor fields weekly. Use pheromone traps.", "high"),

    ("Maize Lethal Necrosis", "Maize lethal necrosis virus", "Maize",
     ["yellowing", "necrosis", "dead", "wilt", "stunt", "mosaic", "leaf tip", "chlorosis", "brown", "rot", "maize necrosis"],
     "No cure. Uproot and destroy affected plants immediately. Report to MAAIF district office.",
     "Use certified seed. Practice crop rotation. Control maize chaffer beetle. Remove alternate hosts.", "high"),

    ("Grey Leaf Spot", "Cercospora zeae-maydis", "Maize",
     ["grey", "spot", "rectangular", "lesion", "leaf spot", "grey spot", "blight", "brown spot"],
     "Apply Mancozeb (2.5g/L) or Propiconazole. Spray at first symptom appearance.",
     "Use resistant varieties. Practice crop rotation with non-cereals. Ensure proper spacing.", "medium"),

    ("Northern Corn Leaf Blight", "Exserohilum turcicum", "Maize",
     ["blight", "long", "cigar", "lesion", "tan", "leaf blight", "torpedo"],
     "Apply Azoxystrobin or Mancozeb. Spray when lesions first appear.",
     "Use resistant hybrids. Rotate crops. Remove crop debris after harvest.", "medium"),

    ("Maize Rust", "Puccinia sorghi", "Maize",
     ["rust", "pustule", "orange", "brown pustule", "powder", "dust"],
     "Apply Propiconazole or Tebuconazole at first sign of pustules.",
     "Use resistant varieties. Early planting helps avoid peak rust pressure.", "low"),

    # Bean diseases
    ("Bean Root Rot", "Fusarium solani", "Beans",
     ["root rot", "wilting", "brown root", "root lesion", "yellow", "die back", "bean wilt"],
     "Apply Carboxin + Thiram seed treatment. Improve drainage. Remove infected plants.",
     "Use certified clean seed. Rotate with non-legumes. Improve soil drainage.", "medium"),

    ("Angular Leaf Spot", "Phaeoisariopsis griseola", "Beans",
     ["angular", "leaf spot", "brown patch", "dead tissue", "bean leaf", "hole in leaf"],
     "Apply Mancozeb (2g/L). Remove infected crop debris.",
     "Use resistant varieties. Rotate crops. Use certified seed.", "medium"),

    ("Bean Anthracnose", "Colletotrichum lindemuthianum", "Beans",
     ["anthracnose", "sunken", "canker", "dark lesion", "bean pod", "brown spot bean"],
     "Apply copper-based fungicide. Remove infected plants.",
     "Use certified seed. Rotate for 2-3 years. Avoid overhead irrigation.", "high"),

    ("Bean Common Mosaic Virus", "Bean common mosaic virus", "Beans",
     ["mosaic", "mottle", "curled leaf", "stunted", "bean virus", "yellow streak", "distorted"],
     "No cure. Remove infected plants. Control aphid vectors with Neem extract.",
     "Use virus-free certified seed. Control aphids. Plant resistant varieties.", "medium"),

    # Coffee diseases
    ("Coffee Wilt Disease", "Fusarium xylarioides", "Coffee",
     ["wilt", "coffee die", "branch dieback", "drying", "coffee wilt", "trunk canker", "brown ring"],
     "No cure. Uproot and burn affected trees. Report to UCDA immediately.",
     "Use certified planting material. Maintain field hygiene. Avoid wounding trees.", "high"),

    ("Coffee Berry Disease", "Colletotrichum kahawae", "Coffee",
     ["berry", "coffee spot", "coffee lesion", "berry rot", "black spot coffee", "sunken lesion coffee"],
     "Apply Copper Hydroxide. Spray before and during flowering.",
     "Use resistant varieties (e.g. Ruiru 11). Prune to improve air circulation.", "high"),

    ("Coffee Leaf Rust", "Hemileia vastatrix", "Coffee",
     ["rust coffee", "orange powder", "coffee leaf yellow", "leaf rust", "yellow spot coffee"],
     "Apply Copper fungicide. Remove heavily infected leaves.",
     "Use resistant varieties. Proper shade management. Regular pruning.", "medium"),

    # Banana diseases
    ("Banana Xanthomonas Wilt", "Xanthomonas campestris pv. musacearum", "Banana",
     ["yellow wilt banana", "ooze", "cut stem", "banana die", "wilting banana", "yellowing banana leaf", "banana xanthomonas"],
     "No cure. Remove entire mat including rhizome. Disinfect tools with JIK or bleach.",
     "Use clean planting material. Disinfect tools. Control banana weevils. Remove infected mats immediately.", "high"),

    ("Banana Bacterial Wilt", "Xanthomonas campestris pv. musacearum", "Banana",
     ["bacterial wilt banana", "banana yellow", "stem ooze", "banana wilt"],
     "Uproot and destroy. Sterilize all tools.",
     "Use tissue culture plants. Avoid sharing tools between mats.", "high"),

    ("Black Sigatoka", "Mycosphaerella fijiensis", "Banana",
     ["sigatoka", "black spot banana", "leaf black", "banana leaf spot", "dark streak"],
     "Apply Copper + Mancozeb. Remove and destroy infected leaves.",
     "Use resistant varieties. Maintain proper spacing. Regular de-leafing.", "medium"),

    # Cassava diseases
    ("Cassava Mosaic Disease", "Cassava mosaic geminivirus", "Cassava",
     ["mosaic cassava", "cassava yellow", "distorted leaf cassava", "cassava virus", "stunted cassava", "leaf curl cassava"],
     "No cure. Remove infected plants. Control whitefly vectors.",
     "Use resistant/tolerant varieties. Plant clean stems. Control whiteflies.", "high"),

    ("Cassava Brown Streak Disease", "Cassava brown streak virus", "Cassava",
     ["brown streak cassava", "cassava root rot", "cassava tuber necrosis", "brown patch cassava leaf"],
     "No cure. Remove and burn infected plants.",
     "Use resistant varieties. Plant disease-free cuttings. Roguing infected plants.", "high"),

    # Tomato diseases
    ("Tomato Late Blight", "Phytophthora infestans", "Tomatoes",
     ["tomato blight", "late blight", "water soaked", "tomato rot", "white mold", "tomato fuzzy"],
     "Apply Metalaxyl + Mancozeb. Remove affected leaves immediately.",
     "Use resistant varieties. Avoid overhead watering. Stake plants for airflow.", "high"),

    ("Tomato Bacterial Wilt", "Ralstonia solanacearum", "Tomatoes",
     ["bacterial wilt tomato", "tomato wilt sudden", "brown vascular", "tomato die sudden"],
     "No effective treatment. Remove plants. Solarize soil.",
     "Rotate with non-solanaceous crops. Use raised beds. Use grafted plants.", "high"),

    ("Tomato Leaf Curl", "Tomato yellow leaf curl virus", "Tomatoes",
     ["tomato curl", "leaf curl tomato", "tomato stunted", "tomato yellow leaf"],
     "Control whitefly vectors with Neem oil or Imidacloprid.",
     "Use resistant varieties. Use insect-proof nets. Remove weeds.", "medium"),

    # Livestock diseases
    ("African Swine Fever", "African swine fever virus", "Livestock",
     ["swine fever", "pig sick", "pig die", "pig bleeding", "pig fever", "pig hemorrhage", "asf"],
     "No vaccine or treatment. Report immediately to veterinary officer. Cull affected herd.",
     "Strict biosecurity. No swill feeding. Control ticks. Isolate new animals.", "high"),

    ("East Coast Fever", "Theileria parva", "Livestock",
     ["coast fever", "tick fever", "cattle swollen", "cattle lymph", "cattle dying", "east coast"],
     "Inject Buparvaquone (Butalex) within 2 weeks of tick attachment.",
     "Regular tick dipping. Immunization through infection and treatment method (ITM).", "high"),

    ("Newcastle Disease", "Newcastle disease virus", "Livestock",
     ["newcastle", "poultry respiratory", "poultry nervous", "chicken sick", "bird die", "poultry droopy"],
     "No cure. Supportive care with electrolytes and vitamins.",
     "Vaccinate at 1 day, 4 weeks, and every 3 months. Biosecurity.", "high"),

    ("Foot and Mouth Disease", "Foot-and-mouth disease virus", "Livestock",
     ["foot mouth", "blister", "lameness", "drooling", "cattle mouth", "hoof blister", "fmd"],
     "No cure. Report to government vet. Rest affected animals.",
     "Regular vaccination. Quarantine new animals. Disinfect premises.", "high"),

    ("Rift Valley Fever", "Rift Valley fever virus", "Livestock",
     ["rift valley", "abortion livestock", "hemorrhage livestock", "liver disease cattle"],
     "No specific treatment. Supportive veterinary care.",
     "Vaccinate livestock. Control mosquitoes. Avoid grazing in flood-prone areas.", "high"),

    # General plant issues
    ("Nutrient Deficiency", "Abiotic", "General",
     ["yellow leaf", "yellowing", "stunted growth", "purple", "chlorosis", "interveinal", "nutrient", "fertilizer", "deficiency"],
     "Apply appropriate fertilizer based on soil test. For nitrogen: Urea (46-0-0). For phosphorus: DAP. For potassium: MOP.",
     "Regular soil testing. Apply balanced fertilizer. Maintain soil pH 6.0-7.0.", "low"),

    ("Drought Stress", "Abiotic", "General",
     ["dry", "wilting dry", "no rain", "parched", "drought", "water stress", "crispy leaf"],
     "Irrigate if possible. Mulch heavily around plants. Apply at dawn or dusk.",
     "Mulch fields. Use drought-tolerant varieties. Water conservation structures.", "low"),

    ("Waterlogging", "Abiotic", "General",
     ["waterlogged", "flood", "soggy", "root rot water", "standing water", "drainage"],
     "Improve drainage channels. Create furrows to drain excess water.",
     "Plant on raised beds. Improve field drainage. Avoid heavy clay soils.", "low"),
]


def analyze_symptoms(crop_name, description, photo_filename=''):
    """
    Analyze crop symptoms and return likely diseases.
    Returns a list of (disease_info, confidence_score) tuples.
    """
    desc_lower = description.lower() if description else ''
    crop_lower = crop_name.lower() if crop_name else ''
    combined_text = f"{crop_lower} {desc_lower}"

    results = []

    for entry in DISEASE_KB:
        name, sci_name, crop, keywords, treatment, prevention, severity = entry

        score = 0
        crop_match = False

        # Crop type matching (strong signal)
        if crop_lower and crop.lower() in crop_lower or crop_lower in crop.lower():
            score += 30
            crop_match = True
        elif crop_lower and any(w in crop_lower for w in crop.split()):
            score += 15

        # Keyword matching
        matched_keywords = []
        for kw in keywords:
            if kw in combined_text:
                score += 12
                matched_keywords.append(kw)

        # Bonus for multiple keyword matches
        if len(matched_keywords) >= 2:
            score += len(matched_keywords) * 5

        # Crop-specific bonus: if crop matches AND keywords match, strong signal
        if crop_match and matched_keywords:
            score += 15

        # Severity weighting
        severity_bonus = {"high": 5, "medium": 3, "low": 1}
        score += severity_bonus.get(severity, 0)

        if score >= 30:
            confidence = min(round(score / 100, 2), 0.98)
            results.append({
                'disease_name': name,
                'scientific_name': sci_name,
                'crop': crop,
                'confidence': confidence,
                'treatment': treatment,
                'prevention': prevention,
                'severity': severity,
                'matched_keywords': matched_keywords,
                'score': score,
            })

    # Sort by score (highest first)
    results.sort(key=lambda x: x['score'], reverse=True)

    # Return top 3 results
    return results[:3]


def get_general_recommendation(crop_name, description):
    """Fallback recommendation when no disease matches."""
    crop_lower = (crop_name or '').lower()

    if not description and not crop_lower:
        return {
            'disease_name': 'Insufficient Information',
            'scientific_name': '',
            'crop': crop_name or 'Unknown',
            'confidence': 0.10,
            'treatment': 'Please provide more details about the symptoms you observe. Include information about: leaf color changes, spots, wilting, insects visible, affected plant parts, and when symptoms started.',
            'prevention': 'Regular field scouting helps catch problems early. Walk through fields at least twice a week during the growing season.',
            'severity': 'unknown',
            'matched_keywords': [],
        }

    return {
        'disease_name': 'Unidentified Issue',
        'scientific_name': '',
        'crop': crop_name or 'Unknown',
        'confidence': 0.15,
        'treatment': 'Conduct a thorough field inspection. Look for insects, spots, wilting patterns, and root health. Consult your local extension officer for hands-on diagnosis.',
        'prevention': 'Maintain good field hygiene. Use certified seeds and planting material. Practice crop rotation. Monitor fields regularly.',
        'severity': 'unknown',
        'matched_keywords': [],
    }
