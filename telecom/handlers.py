"""
USSD Handler for Kilimo Hub - *217#
Handles multi-session USSD menu navigation for farmers.
"""
from django.conf import settings
from weather.views import get_weather, DISTRICT_COORDS
from market.models import Commodity, MarketPrice, Market
from disease.service import analyze_symptoms, get_general_recommendation
from core.models import Alert
import requests


def handle_ussd(phone_number, session_id, text, user=None):
    """
    Main USSD router. Returns (response_text, continue_session).
    Africa's Talking sends text as the full user input history separated by '*'.
    First request has empty text.
    """
    from .models import UssdSession

    session, _ = UssdSession.objects.get_or_create(
        session_id=session_id,
        defaults={'phone_number': phone_number, 'current_menu': 'main', 'menu_state': {}}
    )

    # Parse input
    parts = text.split('*') if text else []
    choice = parts[-1].strip() if parts else ''
    history = parts[:-1] if parts else []

    menu = session.current_menu
    state = session.menu_state or {}

    response = ''
    continue_session = True

    # Route to the right menu handler
    handlers = {
        'main': _handle_main_menu,
        'weather': _handle_weather_menu,
        'weather_district': _handle_weather_district,
        'weather_result': _handle_weather_result,
        'prices': _handle_prices_menu,
        'prices_commodity': _handle_prices_commodity,
        'disease': _handle_disease_menu,
        'disease_crop': _handle_disease_crop,
        'disease_symptoms': _handle_disease_result,
        'vet': _handle_vet_menu,
        'vet_topic': _handle_vet_topic,
        'account': _handle_account_menu,
    }

    handler = handlers.get(menu, _handle_main_menu)
    response, continue_session, next_menu, next_state = handler(
        choice, history, state, session, user
    )

    # Update session
    session.current_menu = next_menu
    session.menu_state = next_state
    session.save()

    return response, continue_session


def _handle_main_menu(choice, history, state, session, user):
    if not choice:
        name = ''
        if user and user.first_name:
            name = f" {user.first_name}"
        text = (
            f"Welcome to Kilimo Hub{name}!\n"
            "Uganda's Farmer Information Service\n\n"
            "1. Weather\n"
            "2. Market Prices\n"
            "3. Crop Disease Check\n"
            "4. Vet Help\n"
            "5. My Account\n"
            "0. Exit"
        )
        return text, True, 'main', state

    if choice == '1':
        text = (
            "Weather Information\n\n"
            "Enter your district name:\n"
            "(e.g. Mukono, Kampala, Jinja)\n\n"
            "0. Back"
        )
        return text, True, 'weather_district', state

    elif choice == '2':
        commodities = list(Commodity.objects.values_list('name', flat=True)[:10])
        if not commodities:
            commodities = ['Maize', 'Beans', 'Coffee', 'Banana', 'Cassava', 'Tomatoes']
        lines = [f"{i+1}. {c}" for i, c in enumerate(commodities)]
        text = "Market Prices\n\n" + "\n".join(lines) + "\n\n0. Back"
        state['commodities'] = commodities
        return text, True, 'prices_commodity', state

    elif choice == '3':
        crops = ['Maize', 'Beans', 'Coffee', 'Banana', 'Cassava', 'Tomatoes', 'Irish Potato']
        lines = [f"{i+1}. {c}" for i, c in enumerate(crops)]
        text = "Crop Disease Check\n\nSelect your crop:\n" + "\n".join(lines) + "\n\n0. Back"
        state['crops'] = crops
        return text, True, 'disease_crop', state

    elif choice == '4':
        text = (
            "Vet Help\n\n"
            "1. Common cattle diseases\n"
            "2. Common goat/sheep diseases\n"
            "3. Common poultry diseases\n"
            "4. Emergency: Report sick animal\n"
            "0. Back"
        )
        return text, True, 'vet', state

    elif choice == '5':
        district = ''
        if user:
            profile = getattr(user, 'farmer_profile', None)
            if profile:
                district = profile.district or 'Not set'
        text = (
            f"My Account\n\n"
            f"Phone: {session.phone_number}\n"
            f"District: {district}\n\n"
            "To update your district, SMS:\n"
            "DISTRICT [name]\n"
            "e.g. DISTRICT Mukono\n\n"
            "0. Back"
        )
        return text, True, 'account', state

    elif choice == '0':
        return "Thank you for using Kilimo Hub!\nTatula *217# again anytime.", False, 'main', state

    else:
        text = (
            "Invalid option. Please choose:\n\n"
            "1. Weather\n"
            "2. Market Prices\n"
            "3. Crop Disease Check\n"
            "4. Vet Help\n"
            "5. My Account\n"
            "0. Exit"
        )
        return text, True, 'main', state


def _handle_weather_district(choice, history, state, session, user):
    if choice == '0':
        return _handle_main_menu('', [], state, session, user)

    district_input = choice.strip()
    # Find matching district (case-insensitive)
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
        districts_list = ', '.join(list(DISTRICT_COORDS.keys())[:8])
        text = f"District not found. Available:\n{districts_list}\n\nEnter district name:\n0. Back"
        return text, True, 'weather_district', state

    state['district'] = matched
    text = (
        f"Weather for {matched}\n\n"
        "1. Current weather\n"
        "2. Farming advisory\n"
        "0. Back"
    )
    return text, True, 'weather', state


def _handle_weather_menu(choice, history, state, session, user):
    if choice == '0':
        text = "Enter your district name:\n(e.g. Mukono, Kampala, Jinja)\n\n0. Back"
        return text, True, 'weather_district', state

    district = state.get('district', 'Mukono')

    if choice == '1':
        # Current weather
        forecast = get_weather(district)
        current = forecast.get('current', {})
        text = (
            f"Weather - {district}\n"
            f"Temp: {current.get('temp', '?')}C (feels {current.get('feels_like', '?')}C)\n"
            f"Condition: {current.get('desc', 'N/A')}\n"
            f"Humidity: {current.get('humidity', '?')}%\n"
            f"Wind: {current.get('wind', 'N/A')}\n\n"
            "1. Farming advisory\n"
            "2. Back to weather\n"
            "0. Main menu"
        )
        return text, True, 'weather_result', state

    elif choice == '2':
        forecast = get_weather(district)
        advisory = forecast.get('advisory', 'No advisory available.')
        text = (
            f"Farming Advisory - {district}\n\n"
            f"{advisory}\n\n"
            "1. Current weather\n"
            "2. Back to weather\n"
            "0. Main menu"
        )
        return text, True, 'weather_result', state

    else:
        text = (
            f"Weather for {district}\n\n"
            "1. Current weather\n"
            "2. Farming advisory\n"
            "0. Back"
        )
        return text, True, 'weather', state


def _handle_weather_result(choice, history, state, session, user):
    if choice == '1':
        return _handle_weather_menu('1', history, state, session, user)
    elif choice == '2':
        return _handle_weather_menu('', history, state, session, user)
    else:
        return _handle_main_menu('', [], state, session, user)


def _handle_prices_commodity(choice, history, state, session, user):
    if choice == '0':
        return _handle_main_menu('', [], state, session, user)

    commodities = state.get('commodities', [])
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(commodities):
            commodity_name = commodities[idx]
            state['selected_commodity'] = commodity_name

            # Get user district from profile
            user_district = ''
            if user:
                profile = getattr(user, 'farmer_profile', None)
                if profile:
                    user_district = profile.district or ''

            # Get prices
            try:
                commodity = Commodity.objects.get(name__iexact=commodity_name)
                prices = MarketPrice.objects.filter(commodity=commodity).select_related('market').order_by('-recorded_at')[:5]

                if user_district:
                    local_prices = prices.filter(market__district__icontains=user_district)
                    if local_prices.exists():
                        prices = local_prices
            except Commodity.DoesNotExist:
                prices = MarketPrice.objects.none()

            lines = [f"--- {commodity_name} ---"]
            if prices.exists():
                for p in prices[:5]:
                    lines.append(f"{p.market.name}: UGX {int(p.price_ugx):,}/{p.commodity.unit}")
                lines.append(f"\nSource: Kilimo Hub")
                if user_district:
                    lines.append(f"Showing prices for {user_district}")
            else:
                lines.append("No prices available yet.")
                lines.append("SMS: PRICE [crop] for updates")

            lines.append("\n0. Main menu")
            text = "\n".join(lines)
            return text, True, 'prices', state
    except (ValueError, IndexError):
        pass

    commodities = state.get('commodities', ['Maize', 'Beans', 'Coffee', 'Banana', 'Cassava'])
    lines = [f"{i+1}. {c}" for i, c in enumerate(commodities)]
    text = "Select a commodity:\n" + "\n".join(lines) + "\n\n0. Back"
    return text, True, 'prices_commodity', state


def _handle_prices_menu(choice, history, state, session, user):
    return _handle_main_menu('2', [], state, session, user)


def _handle_disease_crop(choice, history, state, session, user):
    if choice == '0':
        return _handle_main_menu('', [], state, session, user)

    crops = state.get('crops', ['Maize', 'Beans', 'Coffee', 'Banana', 'Cassava', 'Tomatoes'])
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(crops):
            state['crop'] = crops[idx]
            text = (
                f"Describe symptoms for {crops[idx]}:\n\n"
                "Type a description:\n"
                "(e.g. yellow leaves, holes in leaves)\n\n"
                "0. Back"
            )
            return text, True, 'disease_symptoms', state
    except (ValueError, IndexError):
        pass

    lines = [f"{i+1}. {c}" for i, c in enumerate(crops)]
    text = "Select crop:\n" + "\n".join(lines) + "\n\n0. Back"
    return text, True, 'disease_crop', state


def _handle_disease_result(choice, history, state, session, user):
    """Handle symptom description input via USSD.
    For USSD, we provide a simplified version since typing long descriptions is hard."""
    if choice == '0':
        return _handle_main_menu('', [], state, session, user)

    crop = state.get('crop', '')
    symptoms = choice

    results = analyze_symptoms(crop, symptoms)

    if results:
        top = results[0]
        confidence_pct = int(top['confidence'] * 100)
        text = (
            f"Diagnosis - {crop}\n\n"
            f"Likely: {top['disease_name']}\n"
            f"Confidence: {confidence_pct}%\n"
            f"Severity: {top['severity'].upper()}\n\n"
            f"Treatment:\n{top['treatment']}\n\n"
            f"Prevention:\n{top['prevention']}"
        )
        if len(results) > 1:
            other = results[1]
            text += f"\n\nAlso possible: {other['disease_name']} ({int(other['confidence']*100)}%)"
    else:
        text = (
            "Could not identify the disease.\n\n"
            "Tip: Be more specific about symptoms.\n"
            "Examples:\n"
            "- yellow leaves\n"
            "- holes in whorl\n"
            "- brown spots on pods\n\n"
            "Try again or visit a vet officer."
        )

    text += "\n\n1. Check another crop\n0. Main menu"
    return text, True, 'disease', state


def _handle_disease_menu(choice, history, state, session, user):
    if choice == '1':
        crops = ['Maize', 'Beans', 'Coffee', 'Banana', 'Cassava', 'Tomatoes', 'Irish Potato']
        lines = [f"{i+1}. {c}" for i, c in enumerate(crops)]
        text = "Select crop:\n" + "\n".join(lines) + "\n\n0. Back"
        state['crops'] = crops
        return text, True, 'disease_crop', state
    else:
        return _handle_main_menu('', [], state, session, user)


def _handle_vet_menu(choice, history, state, session, user):
    if choice == '0':
        return _handle_main_menu('', [], state, session, user)

    vet_topics = {
        '1': ("Cattle Diseases\n\n"
              "Common diseases in Uganda:\n\n"
              "1. East Coast Fever\n"
              "2. Foot & Mouth Disease\n"
              "3. Tick-borne diseases\n\n"
              "Prevention:\n"
              "- Regular tick dipping\n"
              "- Vaccination schedule\n"
              "- Quarantine new animals\n\n"
              "SMS: VET [animal] [symptom]\ne.g. VET COW FEVER"),
        '2': ("Goat/Sheep Diseases\n\n"
              "Common diseases:\n\n"
              "1. PPR (Peste des petits)\n"
              "2. Foot rot\n"
              "3. Internal parasites\n\n"
              "Prevention:\n"
              "- Deworming every 3 months\n"
              "- Hoof trimming\n"
              "- Vaccination"),
        '3': ("Poultry Diseases\n\n"
              "Common diseases:\n\n"
              "1. Newcastle Disease\n"
              "2. Gumboro Disease\n"
              "3. Coccidiosis\n\n"
              "Prevention:\n"
              "- Vaccinate on schedule\n"
              "- Keep brooder warm\n"
              "- Good hygiene"),
        '4': ("Emergency Report\n\n"
              "For immediate vet help:\n\n"
              "1. Call your District Vet\n"
              "2. SMS: VET EMERGENCY [details]\n\n"
              "National hotline:\n"
              "MAAIF: 0800-320-320"),
    }

    text = vet_topics.get(choice, "Invalid option. Choose 1-4.\n0. Back")
    return text, True, 'vet_topic', state


def _handle_vet_topic(choice, history, state, session, user):
    if choice == '0':
        return _handle_main_menu('', [], state, session, user)
    return _handle_vet_menu('', [], state, session, user)


def _handle_account_menu(choice, history, state, session, user):
    return _handle_main_menu('', [], state, session, user)


def send_sms(phone_number, message):
    """Send SMS via Africa's Talking API."""
    try:
        import africastalking
        africastalking.initialize(
            username='MuyinzaSolomon10',
            api_key=getattr(settings, 'AT_API_KEY', ''),
        )
        sms = africastalking.SMS
        response = sms.send(message, [phone_number])
        return True
    except Exception as e:
        print(f"[SMS] Failed to send to {phone_number}: {e}")
        return False
