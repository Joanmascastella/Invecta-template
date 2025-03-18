import json
import datetime
import csv
from django.conf import settings
from django.utils.translation import gettext as _  # For language handling
from datetime import time
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import pytz
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .supabase_client import supabase
from .helper_functions import get_access_token, sanitize, wants_json_response
from .models import (
    UserRole,
    User,
    Item,
    PreviousOffer
)
import csv
import os
import logging
from .supabase_client import supabase

logger = logging.getLogger(__name__)

# --------------------------------
# Public / Landing Views
# --------------------------------
def get_current_user():
    try:
        session = supabase.auth.get_session()
        if session:
            user = session.user
            print(f"Supabase Response: user={user} session={session}")
            return user
        else:
            print("No active session.")
            return None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None



def landing_page(request):
    try:
        if request.method == 'GET':
            user_authenticated, user_data = get_access_token(request)
        
            if not user_authenticated:
                if wants_json_response(request):
                    return JsonResponse({'error': 'Not authenticated'}, status=401)
                return redirect('/login')

            user_id = user_data.id
            user_roles = UserRole.objects.filter(user_id=user_id).select_related('role')
            roles = [user_role.role.name for user_role in user_roles]
            user = get_current_user()
            print(user)
            print("\n")
            print(f"User ID: {user_id}, Roles: {roles}")

            if 'user' in roles:
                context = {
                    'title': 'Briefly - Home',
                    'user_authenticated': user_authenticated,
                    'user': user_data,
                    'roles': roles,
                    'navbar_partial': 'partials/authenticated_navbar.html',
                    'LANGUAGES': settings.LANGUAGES,

                }
                return render(request, 'main_page.html', context)

            elif 'admin' in roles:
                return redirect('/custom-admin/dashboard/')
            else:
                if wants_json_response(request):
                    return JsonResponse({'error': 'Role not allowed'}, status=403)
                return redirect('/error/page/')
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



# --------------------------------
# Error View
# --------------------------------
def error_page(request):
    """
    Renders a generic error (404) page.
    """
    try:
        user_authenticated, user_data = get_access_token(request)

        if user_data:
            user_id = user_data.id
            user_roles = UserRole.objects.filter(user_id=user_id).select_related('role')
            roles = [user_role.role.name for user_role in user_roles]

        return render(request, '404.html')
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# --------------------------------
# Authentication Views
# --------------------------------
@csrf_protect
def login_view(request):
    try:
        if request.method == 'GET':
            return render(request, 'loginForm.html', {
                'title': 'Invecta - Login',
                'navbar_partial': 'partials/not_authenticated_navbar.html'
            })

        elif request.method == 'POST':
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON body'}, status=400)

            email = sanitize(data.get('email'))
            password = sanitize(data.get('password'))

            logger.info(f"Attempting login with email: {email}") # added logging
            logger.info(f"Attempting login with password: {password}") # added logging

            if not email or not password:
                return JsonResponse({'error': 'Email and password are required'}, status=400)

            try:
                response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                if response.user:
                    request.session['access_token'] = response.session.access_token
                    request.session['user'] = {
                        "id": response.user.id,
                        "email": response.user.email,
                    }
                    return JsonResponse({'success': True, 'redirect_url': '/en-us/home/'}, status=200)

                return JsonResponse({'error': 'Invalid email or password'}, status=400)
            except Exception as e:
                logger.error(f"Authentication failed: {str(e)}") # added logging
                return JsonResponse({'error': f'Authentication failed: {str(e)}'}, status=500)

        return JsonResponse({'error': 'Invalid request method'}, status=405)
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}") # added logging
        return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)


def logout_view(request):
    """
    Logs out the current user by clearing the session.
    """
    try:
        if request.method == 'GET':
            request.session.flush()
        return redirect('/login/')
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

