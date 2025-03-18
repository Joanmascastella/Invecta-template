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
    """
    Initial page that is accessed. If no user is logged in then user is redirected
    to login page. If logged in it checks the role of the user to redirect them to the correct page. 
    """
    try:
        if request.method == 'GET':
            user_authenticated, user_data, roles = get_role_by_id(request)
        
            if not user_authenticated:
                if wants_json_response(request):
                    return JsonResponse({'error': 'Not authenticated'}, status=401)
                return redirect('/login')

            user_id = user_data.id

            if 'user' in roles:
                return render(request, 'main_page.html', {
                    'title': 'Briefly - Home',
                    'user_authenticated': user_authenticated,
                    'user': user_data,
                    'roles': roles,
                    'navbar_partial': 'partials/authenticated_navbar.html',
                })

            elif 'admin' in roles:
                return redirect('/custom-admin/dashboard/')
            else:
                if wants_json_response(request):
                    return JsonResponse({'error': str(e)}, status=500)
                return render(request, '404.html', status=500) 
    except Exception as e:
        if wants_json_response(request):
            return JsonResponse({'error': str(e)}, status=500)
        return render(request, '404.html', status=500) 



# --------------------------------
# Admin View
# --------------------------------
def admin_page(request):
    """
    Admin dashboard allowing users to navigate to user and stock management
    """
    try:
        if request.method == "GET": 
            user_authenticated, user_data, roles = get_role_by_id(request=request)

            # Check if user is authenticated 
            if not user_authenticated:
                if wants_json_response(request):
                    return JsonResponse({'error': 'Not authenticated'}, status=401)
                return redirect('/login')
            
            # Check the role of the user to verify it's an admin
            if "admin" in roles: 
                return render(request, 'admin_dashboard.html', {
                    'title': 'Invecta - Admin',
                    'user_authenticated': user_authenticated,
                    'user': user_data,
                    'roles': roles,
                    'navbar_partial': 'partials/admin_authenticated_navbar.html',
                }) 
            else:
                request.session.flush()
                if wants_json_response(request):
                    return JsonResponse({'error': 'Not authorized'}, status=403) 
                return render(request, '404.html', status=403) 

    except Exception as e:
        if wants_json_response(request):
            return JsonResponse({'error': str(e)}, status=500)
        return render(request, '404.html', status=500) 

def user_management_page(request):
    """
    User Management page allowing users to edit users roles, and delete users 
    """
    try:
        if request.method == "GET": 
            user_authenticated, user_data, roles = get_role_by_id(request=request)

            # Check if user is authenticated 
            if not user_authenticated:
                if wants_json_response(request):
                    return JsonResponse({'error': 'Not authenticated'}, status=401)
                return redirect('/login')
            
            # Check the role of the user to verify it's an admin
            if "admin" in roles: 
                 # Get all users from database
                all_users = get_all_users(request=request)

                # Pagination
                paginator = Paginator(all_users, 5)  # Show 5 users per page
                page = request.GET.get('page')

                try:
                    users = paginator.page(page)
                except PageNotAnInteger:
                    users = paginator.page(1)
                except EmptyPage:
                    users = paginator.page(paginator.num_pages)

                return render(request, 'user_management.html', {
                    'title': 'Invecta - User Management',
                    'user_authenticated': user_authenticated,
                    'user': user_data,
                    'roles': roles,
                    'navbar_partial': 'partials/admin_authenticated_navbar.html',
                    'users': users,  # Pass paginated users
                }) 
            else:
                request.session.flush()
                if wants_json_response(request):
                    return JsonResponse({'error': 'Not authorized'}, status=403) 
                return render(request, '404.html', status=403) 

    except Exception as e:
        if wants_json_response(request):
            return JsonResponse({'error': str(e)}, status=500)
        return render(request, '404.html', status=500)


def item_management_page(request):
    """
    Item management page allowing users to edit, add, view and delete stock items. 
    """
    try:
        if request.method == "GET": 
            user_authenticated, user_data, roles = get_role_by_id(request=request)

            # Check if user is authenticated 
            if not user_authenticated:
                if wants_json_response(request):
                    return JsonResponse({'error': 'Not authenticated'}, status=401)
                return redirect('/login')
            
            # Check the role of the user to verify it's an admin
            if "admin" in roles: 
                 # Get all items from database
                all_items = get_all_items(request=request)

                # Pagination
                paginator = Paginator(all_items, 5)  # Show 5 items per page
                page = request.GET.get('page')

                try:
                    items = paginator.page(page)
                except PageNotAnInteger:
                    items = paginator.page(1)
                except EmptyPage:
                    items = paginator.page(paginator.num_pages)

                return render(request, 'item_management.html', {
                    'title': 'Invecta - Stock Management',
                    'user_authenticated': user_authenticated,
                    'user': user_data,
                    'roles': roles,
                    'navbar_partial': 'partials/admin_authenticated_navbar.html',
                    'items': items,  # Pass paginated items
                }) 
            else:
                request.session.flush()
                if wants_json_response(request):
                    return JsonResponse({'error': 'Not authorized'}, status=403) 
                return render(request, '404.html', status=403) 

    except Exception as e:
        if wants_json_response(request):
            return JsonResponse({'error': str(e)}, status=500)
        return render(request, '404.html', status=500)

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
        if wants_json_response(request):
            return JsonResponse({'error': str(e)}, status=500)
        return render(request, '404.html', status=500) 


# --------------------------------
# Authentication Views
# --------------------------------
@csrf_protect
def login_view(request):
    """
    Renders login page.
    
    Handles POST requests to login user. 
    """
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
        if wants_json_response(request):
            return JsonResponse({'error': str(e)}, status=500)
        return render(request, '404.html', status=500) 

def logout_view(request):
    """
    Logs out the current user by clearing the session.
    """
    try:
        if request.method == 'GET':
            request.session.flush()
        return redirect('/login/')
    except Exception as e:
        if wants_json_response(request):
            return JsonResponse({'error': str(e)}, status=500)
        return render(request, '404.html', status=500) 

