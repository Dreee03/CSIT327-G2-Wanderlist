from wanderlist.supabase_client import supabase
from datetime import date
# ✅ IMPORT CENTRAL QUOTES
from wanderlist.quotes import QUOTES

# -------------------
# EXISTING SUPABASE CODE (UNCHANGED)
# -------------------

def register_user(email, password, username, first_name, last_name, age):
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name,
                    "age": age
                }
            }
        })

        print(f"Supabase Sign-up Response: {response}")

        if response.user:
            return {"success": True, "message": "Check your email for a confirmation link."}
        else:
            error_message = (
                response.error.message
                if hasattr(response, "error") and response.error
                else "Registration failed."
            )
            return {"success": False, "message": error_message}

    except Exception as e:
        print(f"*** CRITICAL SUPABASE ERROR: {type(e).__name__} - {e}")
        return {"success": False, "message": "Could not connect to the authentication server. Please try again."}


def login_user(username, password):
    try:
        lookup_response = (
            supabase.table("user")
            .select("email, auth_id, userID, username")
            .eq("username", username)
            .execute()
        )

        if not lookup_response.data:
            return {"success": False, "message": "Invalid username or password."}

        print(f"Supabase Lookup Response: {lookup_response}")
        user_data = lookup_response.data[0]
        user_email = user_data["email"]

        response = supabase.auth.sign_in_with_password({
            "email": user_email,
            "password": password
        })

        print(f"Supabase Login Response: {response}")

        if response.session:
            return {
                "success": True,
                "message": "Login successful.",
                "user": response.user,
                "token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "custom_user_id": user_data["userID"],
                "supabase_auth_id": user_data["auth_id"],
                "username": user_data["username"],
            }

        return {"success": False, "message": "Invalid credentials or unconfirmed account."}

    except Exception as e:
        print(f"*** CRITICAL SUPABASE ERROR: {type(e).__name__} - {e}")
        return {"success": False, "message": f"An error occurred: {e}"}


def supabase_sign_out():
    """Sign out from Supabase auth."""
    try:
        supabase.auth.sign_out()
        return True
    except Exception as e:
        print(f"Error during sign out: {e}")
        return False


# -------------------
# ✅ DAILY QUOTE FEATURE (UPDATED)
# -------------------

def get_daily_quote():
    """
    Returns one quote per day using the central list.
    """
    if not QUOTES:
        return "Travel is the only thing you buy that makes you richer."
        
    today = date.today()
    index = today.toordinal() % len(QUOTES)
    return QUOTES[index]