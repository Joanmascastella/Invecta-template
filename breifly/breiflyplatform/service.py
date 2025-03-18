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
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseForbidden
import datetime
import csv
import logging
import json
logger = logging.getLogger(__name__)

# --------------------------------
# User Service
# --------------------------------
def get_current_user():
    """
    Gets the current user from the active session 
    """
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
    """
    Gets the role of the user by id 
    """
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
    """
    Performs login 
    """
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
    """
    Processes login request 
    """
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
    """
    Gets all active users.
    """
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
    """
    Gets all items.
    """
    # Check the role of the user
    user = get_current_user()
    if not user:
        if wants_json_response(request):
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        else:
            return render(request, '404.html', status=401)

    user_id = user.id
    user_roles = UserRole.objects.filter(user_id=user_id).select_related('role')
    roles = [user_role.role.name for user_role in user_roles]
    if "admin" in roles:
        item_data = []
        all_items = Item.objects.order_by('serial_number')
        for i in all_items:
            item_data.append({
                'item_id': i.id,
                'serial_number': i.serial_number,
                'provider': i.provider,
                'name': i.name,
                'category': i.category,
                'price': i.price
            })
        return item_data
    else:
        if wants_json_response(request):
            return JsonResponse({'error': 'Not authorized'}, status=403)
        else:
            return render(request, '404.html', status=403)

# --------------------------------
# User Management
# --------------------------------
def delete_user(id):
    """
    Deletes a user by id. 
    """
    user = get_current_user()
    if not user:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    user_id = user.id
    user_roles = UserRole.objects.filter(user_id=user_id).select_related('role')
    roles = [user_role.role.name for user_role in user_roles]

    if "admin" in roles:
        if User.objects.filter(id=id).exists():
            User.objects.filter(id=id).delete()
            return JsonResponse({'message': 'User deleted successfully'})
        else:
            return JsonResponse({'error': 'User does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
def update_role(request, id):
    """
    Updates the user's role (using integer IDs for roles).
    """
    user = get_current_user()
    if not user:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    user_id = user.id
    user_roles = UserRole.objects.filter(user_id=user_id).select_related('role')
    roles = [user_role.role.name for user_role in user_roles]

    if "admin" in roles:
        try:
            
            data = json.loads(request.body)
            user_to_update = User.objects.get(id=id)
            new_role_name = sanitize(data.get('new_role'))

            if new_role_name not in ['user', 'admin']:
                return JsonResponse({'error': 'Invalid role provided'}, status=400)

            new_role_id = 1 if new_role_name == 'admin' else 2  

            # Delete existing UserRoles and create the new one
            UserRole.objects.filter(user_id=user_to_update.id).delete()
            UserRole.objects.create(user_id=user_to_update.id, role_id=new_role_id) 

            return JsonResponse({'message': 'User role updated successfully'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User does not exist'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Not authorized'}, status=403)


# --------------------------------
# Item Management
# --------------------------------
def delete_item(id):
    """
    Deletes an item by id.
    """
    user = get_current_user()  
    if not user:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    user_id = user.id
    user_roles = UserRole.objects.filter(user_id=user_id).select_related('role')
    roles = [user_role.role.name for user_role in user_roles]

    if "admin" in roles:
        try:
            item = Item.objects.get(id=id)
            item.delete()
            return JsonResponse({'message': 'Item deleted successfully'})
        except Item.DoesNotExist:
            return JsonResponse({'error': 'Item does not exist'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Not authorized'}, status=403)


def update_item(request, id):
    user = get_current_user()
    if not user:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    user_id = user.id
    user_roles = UserRole.objects.filter(user_id=user_id).select_related('role')
    roles = [user_role.role.name for user_role in user_roles]

    if "admin" in roles:
        try:
            data = json.loads(request.body)

            # Delete the existing item
            Item.objects.filter(id=id).delete()

            # Create a new item with the updated data
            Item.objects.create(
                id=id, # use id not item_id
                serial_number=data.get('serial_number', ''),
                provider=data.get('provider', ''),
                name=data.get('name', ''),
                category=data.get('category', ''),
                price=float(data.get('price', 0)) if data.get('price') not in [None, ''] else 0,
            )

            return JsonResponse({'message': 'Item updated successfully'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except (ValueError, TypeError):  # Handle price conversion errors
            return JsonResponse({'error': 'Invalid price format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Not authorized'}, status=403)