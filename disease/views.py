from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.contrib import messages
from core.models import Alert
from .models import Disease, DiseaseReport
from .forms import DiseaseReportForm
from .service import analyze_symptoms, get_general_recommendation


@login_required
def disease_list(request):
    diseases = Disease.objects.all()
    crop_filter = request.GET.get('crop')
    if crop_filter:
        diseases = diseases.filter(crop_affected__icontains=crop_filter)

    # Get location-specific alerts
    profile = getattr(request.user, 'farmer_profile', None)
    user_district = profile.district if profile else ''
    alerts = Alert.objects.filter(is_active=True, category='disease')
    if user_district:
        alerts = alerts.filter(
            models.Q(district__iexact=user_district) | models.Q(district='')
        )
    else:
        alerts = alerts.filter(district='')

    return render(request, 'disease/list.html', {
        'diseases': diseases,
        'alerts': alerts,
        'user_district': user_district,
    })


def report_disease(request):
    DISTRICTS = [
        'kampala', 'mukono', 'wakiso', 'jinja', 'gulu', 'mbarara',
        'arua', 'lira', 'soroti', 'masaka', 'mbale', 'fort portal',
        'kabale', 'tororo', 'hoima',
    ]
    profile = getattr(request.user, 'farmer_profile', None) if request.user.is_authenticated else None
    user_district = profile.district if profile else ''

    # Get local alerts
    local_alerts = Alert.objects.filter(is_active=True, category='disease')
    if user_district:
        local_alerts = local_alerts.filter(
            models.Q(district__iexact=user_district) | models.Q(district='')
        )
    else:
        local_alerts = local_alerts.filter(district='')

    if request.method == 'POST':
        form = DiseaseReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save()

            crop_name = report.crop_name or ''
            description = report.description or ''
            photo_name = ''
            if report.photo:
                photo_name = report.photo.name

            results = analyze_symptoms(crop_name, description, photo_name)

            if results:
                best = results[0]
                report.ai_diagnosis = (
                    f"{best['disease_name']} ({best['scientific_name']}) "
                    f"- Detected in {best['crop']}. "
                    f"Confidence: {best['confidence']*100:.0f}%.\n\n"
                    f"Treatment: {best['treatment']}\n\n"
                    f"Prevention: {best['prevention']}"
                )
                report.ai_confidence = best['confidence']
                if best['confidence'] >= 0.4:
                    report.status = 'identified'
                else:
                    report.status = 'pending'
            else:
                fallback = get_general_recommendation(crop_name, description)
                report.ai_diagnosis = (
                    f"{fallback['disease_name']} - {fallback['crop']}\n\n"
                    f"Recommendation: {fallback['treatment']}\n\n"
                    f"Prevention: {fallback['prevention']}"
                )
                report.ai_confidence = fallback['confidence']
                report.status = 'pending'

            report.save()
            messages.success(request, 'Your report has been submitted. AI diagnosis below.')
            return redirect('disease:report_result', pk=report.pk)
    else:
        form = DiseaseReportForm()
    return render(request, 'disease/report.html', {
        'form': form,
        'districts': [d.title() for d in DISTRICTS],
        'user_district': user_district,
        'local_alerts': local_alerts,
    })


def report_result(request, pk):
    report = get_object_or_404(DiseaseReport, pk=pk)

    # Get alerts for the report's district
    report_district = report.district or ''
    alerts = Alert.objects.filter(is_active=True, category='disease')
    if report_district:
        alerts = alerts.filter(
            models.Q(district__iexact=report_district) | models.Q(district='')
        )
    else:
        alerts = alerts.filter(district='')

    return render(request, 'disease/result.html', {
        'report': report,
        'alerts': alerts,
    })
