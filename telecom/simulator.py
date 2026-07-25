"""
Test simulator for USSD and SMS.
Lets you test the full USSD menu and SMS commands from a web browser
WITHOUT needing Africa's Talking.
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .handlers import handle_ussd
from .sms_handler import handle_incoming_sms
from .models import UssdSession


def simulator(request):
    """Render the USSD/SMS simulator page."""
    return render(request, 'telecom/simulator.html')


@csrf_exempt
@require_POST
def test_ussd(request):
    """Simulate an Africa's Talking USSD callback."""
    session_id = request.POST.get('sessionId', 'test-session-1')
    phone_number = request.POST.get('phoneNumber', '+256700000000')
    text = request.POST.get('text', '')

    user = None
    if request.user.is_authenticated:
        user = request.user

    response_text, continue_session = handle_ussd(
        phone_number=phone_number,
        session_id=session_id,
        text=text,
        user=user,
    )

    prefix = 'CON' if continue_session else 'END'
    return JsonResponse({
        'response': f'{prefix} {response_text}',
        'continue': continue_session,
        'raw': response_text,
    })


@csrf_exempt
@require_POST
def test_sms(request):
    """Simulate an incoming SMS."""
    message = request.POST.get('message', '')
    phone_number = request.POST.get('phoneNumber', '+256700000000')

    user = None
    if request.user.is_authenticated:
        user = request.user

    response = handle_incoming_sms(
        phone_number=phone_number,
        message=message,
        user=user,
    )

    return JsonResponse({'response': response})
