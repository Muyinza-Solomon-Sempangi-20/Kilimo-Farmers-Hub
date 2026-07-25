"""
SMS Command Parser for Kilimo Hub - 8217
Parses incoming SMS commands and returns responses.

Supported commands:
  PRICE [commodity]      - Market prices for a commodity
  WEATHER [district]     - Weather for a district
  DISEASE [crop] [symptoms] - Crop disease diagnosis
  VET [animal] [symptom] - Vet advice
  DISTRICT [name]        - Set your district
  HELP                   - List commands
"""
from weather.views import get_weather, DISTRICT_COORDS
from market.models import Commodity, MarketPrice
from disease.service import analyze_symptoms
from core.models import FarmerProfile
from .models import SmsLog
import re


def handle_incoming_sms(phone_number, message, user=None):
    """
    Parse and handle incoming SMS command.
    Returns the response text to send back.
    """
    # Log incoming
    SmsLog.objects.create(
        phone_number=phone_number, direction='IN',
        message=message, command=message.split()[0].upper() if message.strip() else '',
    )

    text = message.strip()
    if not text:
        return _help_text()

    parts = text.split()
    command = parts[0].upper()
    args = parts[1:]

    handlers = {
        'PRICE': _handle_price,
        'PRICES': _handle_price,
        'WEATHER': _handle_weather,
        'W': _handle_weather,
        'DISEASE': _handle_disease,
        'DIAGNOSE': _handle_disease,
        'VET': _handle_vet,
        'DISTRICT': _handle_district,
        'HELP': lambda p, a, u: _help_text(),
        'H': lambda p, a, u: _help_text(),
    }

    handler = handlers.get(command)
    if handler:
        response = handler(phone_number, args, user)
    else:
        response = (
            f"Unknown command: {command}\n\n"
            + _help_text()
        )

    # Log outgoing
    SmsLog.objects.create(
        phone_number=phone_number, direction='OUT',
        message=response, command=command,
    )

    return response


def _handle_price(phone_number, args, user):
    """Handle PRICE command: PRICE MAIZE"""
    if not args:
        # Show top commodities
        commodities = list(Commodity.objects.values_list('name', flat=True)[:8])
        if not commodities:
            commodities = ['Maize', 'Beans', 'Coffee', 'Banana', 'Cassava']
        lines = ['Market Prices\n']
        lines.append('SMS: PRICE [commodity]')
        lines.append(f'Available: {", ".join(commodities)}')
        return '\n'.join(lines)

    commodity_name = ' '.join(args)

    # Get user district from profile
    user_district = ''
    if user:
        profile = getattr(user, 'farmer_profile', None)
        if profile:
            user_district = profile.district or ''

    try:
        commodity = Commodity.objects.get(name__iexact=commodity_name)
    except Commodity.DoesNotExist:
        # Try partial match
        commodity = Commodity.objects.filter(name__icontains=commodity_name).first()
        if not commodity:
            return (
                f"Commodity '{commodity_name}' not found.\n\n"
                "Available: Maize, Beans, Coffee, Banana, Cassava,\n"
                "Tomatoes, Onions, Rice, Irish Potato\n\n"
                "SMS: PRICE [name]"
            )

    prices = MarketPrice.objects.filter(commodity=commodity).select_related('market').order_by('-recorded_at')[:5]

    if user_district:
        local_prices = prices.filter(market__district__icontains=user_district)
        if local_prices.exists():
            prices = local_prices

    lines = [f'{commodity.name} Prices (UGX):']
    if prices.exists():
        for p in prices[:5]:
            lines.append(f'{p.market.name}: {int(p.price_ugx):,}/{commodity.unit}')
        if user_district:
            lines.append(f'\nShowing {user_district} market prices')
    else:
        lines.append('No prices available yet.')

    lines.append('\nSMS: PRICE [crop] for updates')
    return '\n'.join(lines)


def _handle_weather(phone_number, args, user):
    """Handle WEATHER command: WEATHER MUKONO"""
    if not args:
        return (
            "Weather\n\n"
            "SMS: WEATHER [district]\n"
            "Example: WEATHER Mukono\n\n"
            "Districts: " + ', '.join(list(DISTRICT_COORDS.keys())[:8])
        )

    district_input = ' '.join(args)

    # Find matching district
    matched = None
    for d in DISTRICT_COORDS:
        if d.lower() == district_input.lower():
            matched = d
            break
    if not matched:
        for d in DISTRICT_COORDS:
            if district_input.lower() in d.lower():
                matched = d
                break

    if not matched:
        return (
            f"District '{district_input}' not found.\n\n"
            "Available: " + ', '.join(list(DISTRICT_COORDS.keys()))
        )

    forecast = get_weather(matched)
    current = forecast.get('current', {})
    advisory = forecast.get('advisory', '')

    text = (
        f"Weather - {matched}\n"
        f"Temp: {current.get('temp', '?')}C\n"
        f"Condition: {current.get('desc', 'N/A')}\n"
        f"Humidity: {current.get('humidity', '?')}%\n"
        f"Wind: {current.get('wind', 'N/A')}\n\n"
        f"Farming Tip:\n{advisory}"
    )
    return text


def _handle_disease(phone_number, args, user):
    """Handle DISEASE command: DISEASE MAIZE yellow leaves holes"""
    if len(args) < 1:
        return (
            "Crop Disease Check\n\n"
            "SMS: DISEASE [crop] [symptoms]\n"
            "Examples:\n"
            "- DISEASE Maize yellow leaves\n"
            "- DISEASE Beans wilting brown root\n"
            "- DISEASE Coffee orange rust spots"
        )

    crop = args[0]
    symptoms = ' '.join(args[1:]) if len(args) > 1 else ''

    if not symptoms:
        return (
            f"Disease check for {crop}\n\n"
            "Please describe symptoms.\n"
            f"SMS: DISEASE {crop} [symptoms]\n\n"
            "Example: DISEASE Maize yellow leaves with holes"
        )

    results = analyze_symptoms(crop, symptoms)

    if results:
        top = results[0]
        confidence_pct = int(top['confidence'] * 100)
        text = (
            f"Diagnosis - {crop}\n\n"
            f"Disease: {top['disease_name']}\n"
            f"Confidence: {confidence_pct}%\n"
            f"Severity: {top['severity'].upper()}\n\n"
            f"Treatment:\n{top['treatment']}\n\n"
            f"Prevention:\n{top['prevention']}"
        )
        if len(results) > 1:
            other = results[1]
            text += f"\n\nAlso: {other['disease_name']} ({int(other['confidence']*100)}%)"
    else:
        text = (
            f"Could not identify disease for {crop}.\n\n"
            "Try being more specific:\n"
            "DISEASE [crop] [what you see]\n\n"
            "Example:\n"
            "DISEASE Maize holes in whorl brown frass\n"
            "DISEASE Beans yellow wilting brown roots"
        )

    return text


def _handle_vet(phone_number, args, user):
    """Handle VET command: VET COW FEVER"""
    if not args:
        return (
            "Vet Help\n\n"
            "SMS: VET [animal] [symptom]\n"
            "Examples:\n"
            "- VET Cow fever\n"
            "- VET Goat not eating\n"
            "- VET Chicken sneezing\n"
            "- VET EMERGENCY [details]"
        )

    animal = args[0].lower()
    symptoms = ' '.join(args[1:]).lower() if len(args) > 1 else ''

    vet_kb = {
        'cow': {
            'fever': "East Coast Fever suspected. Inject Buparvaquone (Butalex). Consult vet immediately.",
            'cough': "Lungworm or pneumonia. Deworm with Ivermectin. Consult vet for antibiotics.",
            'not eating': "Could be Rift Valley Fever or FMD. Check mouth for blisters. Isolate and call vet.",
            'diarrhoea': "Check for dehydration. Give oral rehydration. Could be parasitic. Deworm.",
            'tick': "Dip with Amitraz-based acaricide. Clean wounds. Repeat in 14 days.",
            'lameness': "Check hooves for Foot & Mouth blisters. Rest animal. Call vet.",
        },
        'goat': {
            'fever': "PPR suspected. Isolate. Give supportive care. Call vet for confirmation.",
            'not eating': "Check teeth, deworm with Albendazole. Give multivitamin.",
            'diarrhoea': "Deworm immediately. Give oral rehydration. Check for coccidiosis.",
            'cough': "Lungworm or pasteurellosis. Deworm and give antibiotic if needed.",
            'swollen': "Check for abscess or Caseous Lymphadenitis. Lance and drain. Disinfect.",
        },
        'sheep': {
            'fever': "PPR or Caseous Lymphadenitis. Isolate animal. Call vet.",
            'not eating': "Deworm with Albendazole. Check teeth. Give multivitamin.",
            'scab': "Sheep scab. Pour-on Ivermectin. Treat entire flock.",
        },
        'chicken': {
            'sneezing': "Newcastle Disease or CRD. Vaccinate. Improve ventilation. Give antibiotics.",
            'diarrhoea': "Coccidiosis. Give Amprolium in water. Improve hygiene.",
            'not laying': "Check nutrition. Give layer mash. Check for parasites. Provide calcium.",
            'dying': "Could be Newcastle Disease. Vaccinate healthy birds. Isolate sick ones.",
            'droopy': "Newcastle Disease. No cure. Supportive care with electrolytes.",
        },
        'emergency': "EMERGENCY: For immediate vet help call MAAIF hotline: 0800-320-320. Or visit your nearest District Vet Office.",
    }

    # Find animal advice
    animal_symptoms = vet_kb.get(animal, {})
    if not animal_symptoms:
        animals = ', '.join(vet_kb.keys())
        return (
            f"No advice for '{animal}'.\n\n"
            f"Available animals: {animals}\n\n"
            "SMS: VET [animal] [symptom]"
        )

    if not symptoms:
        lines = [f"{animal.title()} health:"]
        for s in animal_symptoms:
            lines.append(f"- VET {animal} {s}")
        return '\n'.join(lines)

    # Find matching symptom
    for key, advice in animal_symptoms.items():
        if key in symptoms or symptoms in key:
            return f"{animal.title()} - {key.title()}:\n\n{advice}"

    # Partial match
    for key, advice in animal_symptoms.items():
        if any(w in symptoms for w in key.split()):
            return f"{animal.title()} - {key.title()}:\n\n{advice}"

    return (
        f"No specific advice for '{symptoms}' in {animal}.\n\n"
        "Try simpler symptoms:\n"
        f"VET {animal} [fever/cough/not eating/diarrhoea]\n\n"
        "Or call MAAIF: 0800-320-320"
    )


def _handle_district(phone_number, args, user):
    """Handle DISTRICT command: DISTRICT MUKONO"""
    if not args:
        return (
            "Set District\n\n"
            "SMS: DISTRICT [name]\n"
            "Example: DISTRICT Mukono\n\n"
            "Available: " + ', '.join(list(DISTRICT_COORDS.keys()))
        )

    district_input = ' '.join(args)

    matched = None
    for d in DISTRICT_COORDS:
        if d.lower() == district_input.lower():
            matched = d
            break
    if not matched:
        for d in DISTRICT_COORDS:
            if district_input.lower() in d.lower():
                matched = d
                break

    if not matched:
        return (
            f"District '{district_input}' not found.\n\n"
            "Available: " + ', '.join(list(DISTRICT_COORDS.keys()))
        )

    # Update user profile if linked
    if user:
        profile, _ = FarmerProfile.objects.get_or_create(user=user)
        profile.district = matched.lower()
        profile.save()
        return f"District set to {matched}.\n\nWeather and prices will now show {matched} data."

    # For anonymous users, just confirm
    return (
        f"District: {matched}\n\n"
        "Note: To save your district permanently,\n"
        "register at kilimo-hub.com or dial *217#"
    )


def _help_text():
    return (
        "Kilimo Hub SMS Commands:\n\n"
        "PRICE [crop] - Market prices\n"
        "WEATHER [district] - Weather info\n"
        "DISEASE [crop] [symptoms] - Diagnosis\n"
        "VET [animal] [symptom] - Vet advice\n"
        "DISTRICT [name] - Set district\n"
        "HELP - This message\n\n"
        "Examples:\n"
        "PRICE Maize\n"
        "WEATHER Mukono\n"
        "DISEASE Maize yellow leaves\n"
        "VET Cow fever\n\n"
        "USSD: Dial *217#"
    )
