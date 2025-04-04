import json
import datetime
import csv
from django.conf import settings
from django.utils.translation import gettext as _  # For language handling
from datetime import time
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import pytz
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .supabase_client import supabase
from .helper_functions import wants_json_response
import csv
import os
import logging
from .service import *
from io import StringIO  

logger = logging.getLogger(__name__)

# --------------------------------
# User - Pages
# --------------------------------
def landing_page(request):
    """
    Initial page accessed. If no user is logged in then user is redirected
    to the login page. If logged in, it checks the role of the user to redirect them accordingly.
    """
    try:
        user_authenticated, user_data, roles = get_role_by_id(request)
    
        if not user_authenticated:
            if wants_json_response(request):
                return JsonResponse({'error': 'Not authenticated'}, status=401)
            return redirect('/login')

        # For a "user" role, only GET is supported
        if 'user' in roles:
            if request.method == 'GET':
                return render(request, 'main_page.html', {
                    'title': 'Briefly - Home',
                    'user_authenticated': user_authenticated,
                    'user': user_data,
                    'roles': roles,
                    'navbar_partial': 'partials/authenticated_navbar.html',
                })
            else:
                return JsonResponse({'error': 'Method not allowed'}, status=405)

        # For an "admin" role, redirect to the admin dashboard
        elif 'admin' in roles:
            if request.method == 'GET':
                return redirect('/custom-admin/dashboard/')
            else:
                return JsonResponse({'error': 'Method not allowed'}, status=405)
        else:
            if wants_json_response(request):
                return JsonResponse({'error': 'User role not recognized'}, status=500)
            return render(request, '404.html', status=500)
    except Exception as e:
        # In case of unexpected errors, return a 500 error.
        if wants_json_response(request):
            return JsonResponse({'error': str(e)}, status=500)
        return render(request, '404.html', status=500)


# --------------------------------
# Admin View
# --------------------------------
def admin_page(request):
    """
    Admin dashboard allowing navigation to user and stock management.
    """
    try:
        user_authenticated, user_data, roles = get_role_by_id(request=request)

        if not user_authenticated:
            if wants_json_response(request):
                return JsonResponse({'error': 'Not authenticated'}, status=401)
            return redirect('/login')
        
        if "admin" in roles: 
            if request.method == "GET": 
                return render(request, 'admin_dashboard.html', {
                    'title': 'Invecta - Admin',
                    'user_authenticated': user_authenticated,
                    'user': user_data,
                    'roles': roles,
                    'navbar_partial': 'partials/admin_authenticated_navbar.html',
                })
            else:
                return JsonResponse({'error': 'Method not allowed'}, status=405)
        else:
            if wants_json_response(request):
                return JsonResponse({'error': 'Not authorized'}, status=403)
            return render(request, '404.html', status=403)
    except Exception as e:
        if wants_json_response(request):
            return JsonResponse({'error': str(e)}, status=500)
        return render(request, '404.html', status=500)


def user_management_page(request, id=None):
    """
    User Management page allowing admins to edit user roles and delete users.
    """
    try:
        user_authenticated, user_data, roles = get_role_by_id(request=request)

        if not user_authenticated:
            if wants_json_response(request):
                return JsonResponse({'error': 'Not authenticated'}, status=401)
            return redirect('/login')

        if "admin" in roles:
            if request.method == "GET":
                all_users = get_all_users(request=request)
                paginator = Paginator(all_users, 5)
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
                    'users': users,
                })
            elif request.method == "PUT":
                return update_role(request=request, id=id)
            elif request.method == "DELETE":
                return delete_user(id=id)
            else:
                return JsonResponse({'error': 'Method not allowed'}, status=405)
        else:
            if wants_json_response(request):
                return JsonResponse({'error': 'Not authorized'}, status=403)
            return render(request, '404.html', status=403)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def item_management_page(request, id=None):
    """
    Item management page allowing admins to edit, add, view, and delete stock items.
    Handles GET, PUT, DELETE, and POST requests.
    """
    try:
        user_authenticated, user_data, roles = get_role_by_id(request=request)

        if not user_authenticated:
            if wants_json_response(request):
                return JsonResponse({'error': 'Not authenticated'}, status=401)
            return redirect('/login')

        if "admin" not in roles:
            # Instead of flushing the session, return a 403 error.
            if wants_json_response(request):
                return JsonResponse({'error': 'Not authorized'}, status=403)
            return render(request, '404.html', status=403)

        if request.method == "GET":
            all_items = get_all_items(request=request)
            paginator = Paginator(all_items, 5)
            page = request.GET.get('page')
            try:
                items = paginator.page(page)
            except PageNotAnInteger:
                items = paginator.page(1)
            except EmptyPage:
                items = paginator.page(paginator.num_pages)
            return render(request, 'stock_management.html', {
                'title': 'Invecta - Stock Management',
                'user_authenticated': user_authenticated,
                'user': user_data,
                'roles': roles,
                'navbar_partial': 'partials/admin_authenticated_navbar.html',
                'items': items,
            })
        elif request.method == "PUT":
            if id is None:
                return JsonResponse({'error': 'Item ID is required for PUT requests'}, status=400)
            return update_item(request, id=id)
        elif request.method == "DELETE":
            if id is None:
                return JsonResponse({'error': 'Item ID is required for DELETE requests'}, status=400)
            return delete_item(id=id)
        elif request.method == "POST":
            return create_item(request)
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
    except Exception as e:
        if wants_json_response(request):
            return JsonResponse({'error': str(e)}, status=500)
        return render(request, '404.html', status=500)


def download_csv(request):
    """
    Generates a CSV file to download.
    """
    try:
        user_authenticated, user_data, roles = get_role_by_id(request=request)

        if not user_authenticated:
            if wants_json_response(request):
                return JsonResponse({'error': 'Not authenticated'}, status=401)
            return redirect('/login')

        if "admin" not in roles:
            if wants_json_response(request):
                return JsonResponse({'error': 'Not authorized'}, status=403)
            return render(request, '404.html', status=403)

        if request.method == "GET":
            items = get_download_all_items(request=request)

            def rows(items):
                yield ["Serial Number", "Provider", "Name", "Category", "Price"]
                for item in items:
                    yield [item.serial_number, item.provider, item.name, item.category, item.price]

            def generate_csv(rows_generator):
                output = StringIO()
                writer = csv.writer(output)
                for row in rows_generator:
                    writer.writerow(row)
                    yield output.getvalue()
                    output.seek(0)
                    output.truncate(0)

            response = StreamingHttpResponse(
                generate_csv(rows(items)),
                content_type='text/csv'
            )
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            response['Content-Disposition'] = f'attachment; filename="exported_stock_item_data_{date_str}.csv"'
            return response

        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
    except Exception as e:
        if wants_json_response(request):
            return JsonResponse({'error': str(e)}, status=500)
        return render(request, '404.html', status=500)

def upload_csv(request):
    """
    Imports a CSV file.
    """
    try:
        user_authenticated, user_data, roles = get_role_by_id(request=request)

        if not user_authenticated:
            if wants_json_response(request):
                return JsonResponse({'error': 'Not authenticated'}, status=401)
            return redirect('/login')

        if "admin" not in roles:
            if wants_json_response(request):
                return JsonResponse({'error': 'Not authorized'}, status=403)
            return render(request, '404.html', status=403)

        if request.method == "POST":
            response = import_csv(request=request)
            return response

        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
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

