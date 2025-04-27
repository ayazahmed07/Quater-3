import streamlit as st
import json
import re


# File load/save functions
def load_users():
    try:
        with open("users.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    
def save_users(users):
    with open("users.json", "w") as file:
        json.dump(users, file, indent=4)

# Authentication functions
def register(username, password, confirm_password):
    if password != confirm_password:
        return False, "Passwords do not match."
    
    password_valid, password_msg = password_check(password)
    if not password_valid:
        return False, password_msg
    
    users = load_users()
    if username in users:
        return False, "Username already exists."
    
    users[username] = {"password": password}
    save_users(users)
    return True, "Registration successful! You can now login."

def login(username, password):
    users = load_users()
    if username in users and users[username]["password"] == password:
        return True
    return False

def reset_password(username, new_password):
    password_valid, password_msg = password_check(new_password)
    if not password_valid:
        return False, password_msg
    
    users = load_users()
    if username in users:
        users[username]["password"] = new_password
        save_users(users)
        return True, "Password reset successful!"
    return False, "Username not found."

# Password check function
def password_check(password):
    # Check if password is between 8 and 12 characters
    if not (8 <= len(password) <= 12):
        return False, "Password must be between 8 and 12 characters."
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    
    # Check for at least one digit
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit."
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character."
    
    return True, "Password is valid."

# Main app
def main():
    st.title("🔒 Login/Register")

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None

    if not st.session_state.authenticated:
        tabs = st.tabs(["Login", "Register", "Forgot Password"])

        with tabs[0]:  # Login tab
            st.subheader("Login")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login"):
                if login(username, password):
                    st.success("Logged in successfully!")
                    st.session_state.authenticated = True
                    st.session_state.current_user = username
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        with tabs[1]:  # Register tab
            st.subheader("Register")
            new_username = st.text_input("New Username", key="register_username")
            new_password = st.text_input("New Password", type="password", key="register_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
            if st.button("Register"):
                success, message = register(new_username, new_password, confirm_password)
                if success:
                    st.success(message)
                else:
                    st.error(message)

        with tabs[2]:  # Forgot Password tab
            st.subheader("Forgot Password")
            reset_username = st.text_input("Username", key="forgot_username")
            new_password = st.text_input("New Password", type="password", key="forgot_new_password")
            if st.button("Reset Password"):
                success, message = reset_password(reset_username, new_password)
                if success:
                    st.success(message)
                else:
                    st.error(message)

    else:
        st.success(f"Welcome, {st.session_state.current_user}!")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.rerun()

if __name__ == "__main__":
    main()
