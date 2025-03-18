from .supabase_client import supabase
from .helper_functions import get_access_token, sanitize, wants_json_response
from .models import (
    UserRole,
    User,
    Item,
    PreviousOffer
)
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import JsonResponse
import datetime
import csv
import logging
import json
logger = logging.getLogger(__name__)

# --------------------------------
# User Service
# --------------------------------
def get_current_user():
    try:
        session = supabase.auth.get_session()
        if session:
            user = session.user
            return user
        else:
            return None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def get_role_by_id(request):
    user_authenticated, user_data = get_access_token(request)

    user_id = user_data.id
    # Get Role of the user
    user_roles = UserRole.objects.filter(user_id=user_id).select_related('role')
    # Get the name of the role
    roles = [user_role.role.name for user_role in user_roles]
    return user_authenticated, user_data, roles, 



# --------------------------------
# Login Service
# --------------------------------
def perform_login(request, email, password):
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
        logger.error(f"Authentication failed: {str(e)}")
        return JsonResponse({'error': f'Authentication failed: {str(e)}'}, status=500)

def process_login_request(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    email = sanitize(data.get('email'))
    password = sanitize(data.get('password'))

    if not email or not password:
        return JsonResponse({'error': 'Email and password are required'}, status=400)

    return perform_login(request, email, password)

# --------------------------------
# Admin Service
# --------------------------------
def get_all_users(request):
    # Check the role of the user
    user = get_current_user()
    user_id = user.id
    user_roles = UserRole.objects.filter(user_id=user_id).select_related('role')
    roles = [user_role.role.name for user_role in user_roles]
    if "admin" in roles:
            all_users = User.objects.all()
            user_data = []

            for u in all_users:
                user_roles_data = UserRole.objects.filter(user_id=u.id).select_related('role')
                roles_data = [{"id": ur.role.id, "name": ur.role.name} for ur in user_roles_data]
                user_data.append({
                    "id": u.id,
                    "email": u.email,
                    "roles": roles_data,
                })
            return user_data
    else:
        request.session.flush()
        if wants_json_response(request):
            return JsonResponse({'error': 'Not authorized'}, status=403) 
        return render(request, '404.html', status=403) 


def get_all_items(request):
    # Check the role of the user
    user = get_current_user()
    if not user:
        if wants_json_response(request):
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        else:
            return render(request, '401.html', status=401)

    user_id = user.id
    user_roles = UserRole.objects.filter(user_id=user_id).select_related('role')
    roles = [user_role.role.name for user_role in user_roles]
    if "admin" in roles:
        all_items = Item.objects.all()
        item_data = []
        for item in all_items:
            item_data.append({
                "serial_number": item.serial_number,
                "provider": item.provider,
                "name": item.name,
                "category": item.category,
                "price": float(item.price),  
            })
        return item_data
    else:
        if wants_json_response(request):
            return JsonResponse({'error': 'Not authorized'}, status=403)
        else:
            return render(request, '404.html', status=403)