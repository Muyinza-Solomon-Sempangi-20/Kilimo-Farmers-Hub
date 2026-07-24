import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .service import translate_text, SUPPORTED_LANGUAGES


@login_required
@require_POST
def translate_view(request):
    """
    AJAX endpoint: POST {text, target_lang, source_lang}
    Returns {translated, source_lang, target_lang, target_name}
    """
    try:
        data = json.loads(request.body)
        text        = data.get('text', '').strip()
        target_lang = data.get('target_lang', 'lug')
        source_lang = data.get('source_lang', 'en')

        if not text:
            return JsonResponse({'error': 'No text provided'}, status=400)
        if target_lang not in SUPPORTED_LANGUAGES:
            return JsonResponse({'error': f'Unsupported language: {target_lang}'}, status=400)

        translated = translate_text(text, source_lang, target_lang)
        return JsonResponse({
            'translated': translated,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'target_name': SUPPORTED_LANGUAGES[target_lang],
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@login_required
@require_POST
def save_language(request):
    """
    Save user's preferred language to their profile.
    POST {language: 'lug'}
    """
    try:
        data = json.loads(request.body)
        lang = data.get('language', 'en')
        if lang not in SUPPORTED_LANGUAGES:
            return JsonResponse({'error': f'Unsupported language: {lang}'}, status=400)

        profile = getattr(request.user, 'farmer_profile', None)
        if profile:
            profile.preferred_language = lang
            profile.save()
            return JsonResponse({'status': 'ok', 'language': lang, 'language_name': SUPPORTED_LANGUAGES[lang]})
        return JsonResponse({'error': 'No profile found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


def language_options(request):
    """Return supported language list as JSON."""
    return JsonResponse({'languages': SUPPORTED_LANGUAGES})
