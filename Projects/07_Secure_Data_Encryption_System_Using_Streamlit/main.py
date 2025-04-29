import streamlit as st
import json
import os
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from datetime import datetime
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

def load_stored_data():
    try:
        with open("data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        st.warning("data.json is corrupted. Starting with empty data.")
        return {}

def save_stored_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

def load_logs():
    try:
        with open("logs.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        st.warning("logs.json is corrupted. Starting with empty logs.")
        return {}

def save_logs(logs):
    with open("logs.json", "w") as f:
        json.dump(logs, f, indent=4)

# Password validation
def password_check(password):
    if not (8 <= len(password) <= 12):
        return False, "Password must be between 8 and 12 characters."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character."
    return True, "Password is valid."

# Authentication functions
def hash_password(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    return base64.urlsafe_b64encode(key).decode('utf-8')

def register(username, password, confirm_password):
    valid, msg = password_check(password)
    if not valid:
        return False, msg
    if password != confirm_password:
        return False, "Passwords do not match."
    
    salt = os.urandom(16)
    hashed_password = hash_password(password, salt)
    users = load_users()
    if username in users:
        return False, "Username already exists."
    
    users[username] = {"salt": base64.b64encode(salt).decode('utf-8'), "hashed_password": hashed_password}
    save_users(users)
    log_action(username, "Register", "Account created")
    return True, "Registration successful! You can now login."

def login(username, password):
    users = load_users()
    if username in users:
        stored_salt = base64.b64decode(users[username]["salt"])
        stored_hashed_password = users[username]["hashed_password"]
        provided_hashed_password = hash_password(password, stored_salt)
        if provided_hashed_password == stored_hashed_password:
            st.session_state.fernet = Fernet(stored_hashed_password)
            log_action(username, "Login", "Success")
            return True
    log_action(username or "unknown", "Failed Login", "Invalid credentials")
    return False

def reset_password(username, new_password):
    valid, msg = password_check(new_password)
    if not valid:
        return False, msg
    users = load_users()
    if username not in users:
        return False, "Username not found."
    
    salt = os.urandom(16)
    hashed_password = hash_password(new_password, salt)
    users[username] = {"salt": base64.b64encode(salt).decode('utf-8'), "hashed_password": hashed_password}
    save_users(users)
    log_action(username, "Reset Password", "Password reset")
    return True, "Password reset successful!"

# Logging function
def log_action(user, action, details=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logs = load_logs()
    logs.setdefault(user, []).append({"action": action, "timestamp": timestamp, "details": details})
    save_logs(logs)

# Data functions
def store_data_page():
    st.title("Store Data")
    name = st.text_input("Data Name")
    data = st.text_area("Data")
    if st.button("Store"):
        if name and data:
            user = st.session_state.current_user
            if user not in st.session_state.stored_data:
                st.session_state.stored_data[user] = {}
            max_id = max([int(id) for id in st.session_state.stored_data[user].keys()] + [0])
            new_id = str(max_id + 1)
            fernet = st.session_state.fernet
            encrypted_data = fernet.encrypt(data.encode('utf-8')).decode('utf-8')
            st.session_state.stored_data[user][new_id] = {"name": name, "encrypted_data": encrypted_data}
            save_stored_data(st.session_state.stored_data)
            log_action(user, "Store Data", f"Stored '{name}' (ID: {new_id})")
            st.success(f"Data stored with ID {new_id}")
        else:
            st.error("Please enter name and data.")

def retrieve_data_page():
    st.title("Retrieve Data")
    user = st.session_state.current_user
    if user not in st.session_state.stored_data or not st.session_state.stored_data[user]:
        st.info("No data stored yet.")
        return
    entries = [(id, entry["name"]) for id, entry in st.session_state.stored_data[user].items()]
    options = [f"{name} (ID: {id})" for id, name in entries]
    selected = st.selectbox("Select data", options)
    id = next(i for i, n in entries if f"{n} (ID: {i})" == selected)
    if st.button("Retrieve"):
        stored = st.session_state.stored_data[user][id]
        fernet = st.session_state.fernet
        try:
            decrypted_data = fernet.decrypt(stored["encrypted_data"].encode('utf-8')).decode('utf-8')
            st.success("Data retrieved!")
            st.write("Data:", decrypted_data)
            log_action(user, "Retrieve Data", f"Retrieved '{stored['name']}' (ID: {id})")
        except:
            st.error("Decryption failed. Data may be corrupted.")

def delete_data_page():
    st.title("Delete Data")
    user = st.session_state.current_user
    if user not in st.session_state.stored_data or not st.session_state.stored_data[user]:
        st.info("No data stored yet.")
        return
    entries = [(id, entry["name"]) for id, entry in st.session_state.stored_data[user].items()]
    options = [f"{name} (ID: {id})" for id, name in entries]
    selected = st.selectbox("Select data to delete", options)
    id = next(i for i, n in entries if f"{n} (ID: {i})" == selected)
    if st.button("Delete"):
        del st.session_state.stored_data[user][id]
        if not st.session_state.stored_data[user]:
            del st.session_state.stored_data[user]
        save_stored_data(st.session_state.stored_data)
        log_action(user, "Delete Data", f"Deleted '{selected.split(' (ID: ')[0]}' (ID: {id})")
        st.success("Data deleted!")

def view_history_page():
    st.title("View History")
    user = st.session_state.current_user
    logs = load_logs().get(user, [])
    if not logs:
        st.info("No activity logged yet.")
        return
    st.subheader("Activity Log")
    for log in logs:
        st.write(f"{log['timestamp']}: {log['action']} - {log['details']}")

# Main app
def main():
    # Load data at start
    st.session_state.users = load_users()
    st.session_state.stored_data = load_stored_data()

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "fernet" not in st.session_state:
        st.session_state.fernet = None

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
            st.warning("Note: Resetting your password will make your existing data inaccessible.")
            if st.button("Reset Password"):
                success, message = reset_password(reset_username, new_password)
                if success:
                    st.success(message)
                else:
                    st.error(message)

    else:
        st.success(f"Welcome, {st.session_state.current_user}!")
        menu = ["Home", "Store Data", "Retrieve Data", "Delete Data", "View History", "Logout"]
        choice = st.sidebar.selectbox("Select an option", menu)

        if choice == "Home":
            st.write("You are logged in. Use the sidebar to manage your data.")

        elif choice == "Store Data":
            store_data_page()

        elif choice == "Retrieve Data":
            retrieve_data_page()

        elif choice == "Delete Data":
            delete_data_page()

        elif choice == "View History":
            view_history_page()

        elif choice == "Logout":
            log_action(st.session_state.current_user, "Logout", "Logged out")
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.fernet = None
            st.success("Logged out successfully!")
            st.rerun()

if __name__ == "__main__":
    main()