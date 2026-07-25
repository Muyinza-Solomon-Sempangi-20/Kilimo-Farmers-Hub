"""
Views for USSD and SMS callbacks from Africa's Talking.
These endpoints receive POST requests from the Africa's Talking gateway
when users dial *217# or send SMS to 8217.
"""
import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from .handlers import handle_ussd, send_sms
from .sms_handler import handle_incoming_sms
from .models import UssdSession, SmsLog


@csrf_exempt
@require_POST
def ussd_callback(request):
    """
    Africa's Talking USSD callback endpoint.
    Receives: sessionId, phoneNumber, text
    Returns: Plain text response (CON <text> or END <text>)
    """
    session_id = request.POST.get('sessionId', '')
    phone_number = request.POST.get('phoneNumber', '')
    text = request.POST.get('text', '')

    if not session_id or not phone_number:
        return HttpResponse("END Invalid request. Please try again.", content_type='text/plain')

    # Try to find user by phone number
    user = _find_user_by_phone(phone_number)

    try:
        response_text, continue_session = handle_ussd(
            phone_number=phone_number,
            session_id=session_id,
            text=text,
            user=user,
        )

        if continue_session:
            return HttpResponse(f"CON {response_text}", content_type='text/plain')
        else:
            return HttpResponse(f"END {response_text}", content_type='text/plain')

    except Exception as e:
        print(f"[USSD] Error: {e}")
        return HttpResponse(
            "END Sorry, an error occurred. Please try again later.",
            content_type='text/plain'
        )


@csrf_exempt
@require_POST
def sms_callback(request):
    """
    Africa's Talking SMS callback endpoint.
    Receives: from, to, text, date, id
    """
    phone_number = request.POST.get('from', '')
    message = request.POST.get('text', '')

    if not phone_number or not message:
        return JsonResponse({'status': 'error', 'message': 'Missing parameters'}, status=400)

    # Find user
    user = _find_user_by_phone(phone_number)

    try:
        response = handle_incoming_sms(
            phone_number=phone_number,
            message=message,
            user=user,
        )

        # Send response SMS
        if response:
            send_sms(phone_number, response)

        return JsonResponse({'status': 'ok'})

    except Exception as e:
        print(f"[SMS] Error: {e}")
        send_sms(phone_number, "Sorry, an error occurred. SMS HELP for commands.")
        return JsonResponse({'status': 'error'}, status=500)


@require_POST
def sms_send(request):
    """
    Internal API to send SMS (for web dashboard use).
    Requires auth and JSON body with phone and message.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)

    try:
        data = json.loads(request.body)
        phone = data.get('phone', '')
        message = data.get('message', '')

        if not phone or not message:
            return JsonResponse({'status': 'error', 'message': 'Missing phone or message'}, status=400)

        success = send_sms(phone, message)
        if success:
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Failed to send SMS'}, status=500)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)


def _find_user_by_phone(phone_number):
    """Try to find a Django User by phone number from their FarmerProfile."""
    from core.models import FarmerProfile

    # Clean phone number (remove +, spaces, etc.)
    clean = phone_number.replace('+', '').replace(' ', '').replace('-', '')

    # Try exact match
    profile = FarmerProfile.objects.filter(phone=clean).first()
    if profile:
        return profile.user

    # Try with country code variants
    if clean.startswith('256'):
        local = clean[3:]
        profile = FarmerProfile.objects.filter(phone=local).first()
        if profile:
            return profile.user

    return None
