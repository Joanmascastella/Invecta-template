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
from .helper_functions import wants_json_response
import csv
import os
import logging
from .service import *

logger = logging.getLogger(__name__)

# --------------------------------
# User - Pages
# --------------------------------
def landing_page(request):
    try:
        if request.method == 'GET':
            user_authenticated, user_data, roles = get_role_by_id(request)
        
            if not user_authenticated:
                if wants_json_response(request):
                    return JsonResponse({'error': 'Not authenticated'}, status=401)
                return redirect('/login')

            user_id = user_data.id
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
# Admin View
# --------------------------------
def admin_page(request):
    
    return


# --------------------------------
# Error View
# --------------------------------
def error_page(request):
    """
    Renders a generic error (404) page.
    """
    try:
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
            return process_login_request(request)

        return JsonResponse({'error': 'Invalid request method'}, status=405)
    except Exception as e:
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

