import supabase

# Replace with your Supabase credentials
url = "https://rcxipzhhksdjnustcliu.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJjeGlwemhoa3Nkam51c3RjbGl1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDIyMDc3MjYsImV4cCI6MjA1Nzc4MzcyNn0.1hShw7z3AJrOZeMsppbKYqmM4Q2LGI5vv6wA0d4pPZk"

supabase_client = supabase.create_client(url, key)

def test_login(email, password):
    try:
        response = supabase_client.auth.sign_in_with_password({"email": email, "password": password})
        print(f"Supabase Response: {response}")
        if response.user:
            print(f"Supabase User ID: {response.user.id}")
        else:
            print("Login Failed")

    except Exception as e:
        print(f"Error: {e}")

# Test with different user credentials
test_login("user1@example.com", "password1")
test_login("user2@example.com", "password2")