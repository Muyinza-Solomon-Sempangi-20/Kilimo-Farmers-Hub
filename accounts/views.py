from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    if request.method == 'POST':
        phone_or_user = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=phone_or_user, password=password)
        if user:
            login(request, user)
            # Set language from profile
            profile = getattr(user, 'farmer_profile', None)
            if profile and profile.preferred_language != 'en':
                request.session['django_language'] = profile.preferred_language
            return redirect(request.GET.get('next', '/'))
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    return render(request, 'accounts/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        username   = request.POST.get('username', '').strip()
        phone      = request.POST.get('phone', '').strip()
        district   = request.POST.get('district', '').strip()
        password1  = request.POST.get('password1', '').strip()
        password2  = request.POST.get('password2', '').strip()

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'That username is already taken.')
        elif len(password1) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
        else:
            user = User.objects.create_user(
                username=username,
                password=password1,
                first_name=first_name,
                last_name=last_name,
            )
            from core.models import FarmerProfile
            FarmerProfile.objects.create(user=user, phone=phone, district=district)
            login(request, user)
            messages.success(request, f'Welcome, {first_name}! Your account has been created.')
            return redirect('core:dashboard')
    return render(request, 'accounts/register.html')


@login_required
def profile_view(request):
    from core.models import FarmerProfile
    profile, created = FarmerProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        district = request.POST.get('district', '').strip()
        village = request.POST.get('village', '').strip()
        preferred_language = request.POST.get('preferred_language', 'en').strip()
        farm_size = request.POST.get('farm_size_acres', '1.0').strip()
        password1 = request.POST.get('password1', '').strip()
        password2 = request.POST.get('password2', '').strip()

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()

        profile.phone = phone
        profile.district = district
        profile.village = village
        profile.preferred_language = preferred_language
        try:
            profile.farm_size_acres = float(farm_size)
        except (ValueError, TypeError):
            pass
        profile.save()

        if password1:
            if password1 != password2:
                messages.error(request, 'Passwords do not match.')
            elif len(password1) < 6:
                messages.error(request, 'Password must be at least 6 characters.')
            else:
                request.user.set_password(password1)
                request.user.save()
                login(request, request.user)
                messages.success(request, 'Password updated successfully.')
        else:
            messages.success(request, 'Profile updated successfully.')
        return redirect('accounts:profile')

    return render(request, 'accounts/profile.html', {'profile': profile})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')
