import streamlit as st
import json
import base64
import hashlib
from cryptography.fernet import Fernet
import re
from datetime import datetime
import time

# File load/save functions
def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

def load_stored_data():
    try:
        with open("data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
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

def save_logs(logs):
    with open("logs.json", "w") as f:
        json.dump(logs, f, indent=4)

# Password validation
def password_check(password):
    if not (8 <= len(password) <= 12):
        return False, "Password: Must be at least 8-12 chars!"
    if not re.search(r'[a-z]', password):
        return False, "Need 1 lowercase!"
    if not re.search(r'[0-9]', password):
        return False, "Need 1 digit!"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Need 1 special char!"
    return True, ""

# Lockout function
def is_locked_out():
    if "lockout_time" in st.session_state and st.session_state.lockout_time:
        elapsed = time.time() - st.session_state.lockout_time
        if elapsed < 30:
            st.warning(f"Locked out. Wait for {30 - int(elapsed)} seconds.")
            return True
        st.session_state.lockout_time = 0
        st.session_state.pin_attempts = 0
    return False

# Authentication functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_fernet_key(pin):
    if not pin:
        return None
    hashed_pin = hashlib.sha256(pin.encode()).hexdigest()
    key = hashed_pin[:32].encode()
    return Fernet(base64.urlsafe_b64encode(key))

def register(username, password, confirm_password):
    valid, msg = password_check(password)
    if not valid:
        return False, msg
    if password != confirm_password:
        return False, "Passwords don't match!"
    users = load_users()
    if username in users:
        return False, "Username exists!"
    users[username] = {"hashed_password": hash_password(password)}
    save_users(users)
    log_action(username, "Register", "Account created Successfuly")
    return True, "Registered! Please login Now."

def login(username, password):
    users = load_users()
    if username in users and users[username]["hashed_password"] == hash_password(password):
        log_action(username, "Login", "Successfully Login")
        return True
    log_action(username or "unknown", "Failed Login", "Invalid credentials")
    return False

# Logging function
def log_action(user, action, details=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logs = load_logs()
    logs.setdefault(user, []).append({"action": action, "timestamp": timestamp, "details": details})
    save_logs(logs)

# Data functions
def store_data_page():
    st.title("Store Data")
    if "pin_attempts" not in st.session_state:
        st.session_state.pin_attempts = 0
    name = st.text_input("Data Name")
    data = st.text_area("Data")
    pin = st.text_input("PIN for Encryption", type="password")
    if st.button("Encrypt Data"):
        if name and data and pin:
            user = st.session_state.current_user
            if user not in st.session_state.stored_data:
                st.session_state.stored_data[user] = []
            fernet = get_fernet_key(pin)
            if not fernet:
                st.error("Invalid PIN!")
                return
            try:
                encrypted_data = fernet.encrypt(data.encode()).decode()
                st.session_state.stored_data[user].append({"name": name, "encrypted_data": encrypted_data})
                save_stored_data(st.session_state.stored_data)
                log_action(user, "Store Data", f"Stored '{name}'")
                st.success("Data stored!")
                st.session_state.pin_attempts = 0
            except:
                st.session_state.pin_attempts += 1
                log_action(user, "Failed Store", f"Wrong PIN attempt {st.session_state.pin_attempts}")
                st.error(f"Encryption failed! Attempts left: {3 - st.session_state.pin_attempts}")
                if st.session_state.pin_attempts >= 3:
                    log_action(user, "Lockout", "Logged out due to 3 wrong PINs")
                    st.session_state.authenticated = False
                    st.session_state.current_user = None
                    st.session_state.lockout_time = time.time()
                    st.error("Logged out due to 3 wrong PINs!")
                    st.rerun()
        else:
            st.error("Fill all fields!")

def retrieve_data_page():
    st.title("Retrieve Data")
    if "pin_attempts" not in st.session_state:
        st.session_state.pin_attempts = 0
    user = st.session_state.current_user
    if user not in st.session_state.stored_data or not st.session_state.stored_data[user]:
        st.info("No data stored.")
        return
    names = [entry["name"] for entry in st.session_state.stored_data[user]]
    selected = st.selectbox("Select data", names)
    pin = st.text_input("PIN for Decryption", type="password")
    if st.button("Decrypt"):
        if not pin:
            st.error("Enter PIN!")
            return
        fernet = get_fernet_key(pin)
        if not fernet:
            st.error("Invalid PIN!")
            return
        for entry in st.session_state.stored_data[user]:
            if entry["name"] == selected:
                try:
                    decrypted_data = fernet.decrypt(entry["encrypted_data"].encode()).decode()
                    st.success("Data retrieved!")
                    st.write("Data:", decrypted_data)
                    log_action(user, "Retrieve Data", f"Retrieved '{selected}'")
                    st.session_state.pin_attempts = 0
                    break
                except:
                    st.session_state.pin_attempts += 1
                    log_action(user, "Failed Retrieve", f"Wrong PIN attempt {st.session_state.pin_attempts}")
                    st.error(f"Decryption failed! Attempts left: {3 - st.session_state.pin_attempts}")
                    if st.session_state.pin_attempts >= 3:
                        log_action(user, "Lockout", "Logged out due to 3 wrong PINs")
                        st.session_state.authenticated = False
                        st.session_state.current_user = None
                        st.session_state.lockout_time = time.time()
                        st.sidebar.error("Logged out due to 3 wrong PINs!")
                        st.rerun()
                    break
        else:
            st.error("Data not found!")

def delete_data_page():
    st.title("Delete Data")
    if "pin_attempts" not in st.session_state:
        st.session_state.pin_attempts = 0
    user = st.session_state.current_user
    if user not in st.session_state.stored_data or not st.session_state.stored_data[user]:
        st.info("No data stored.")
        return
    names = [entry["name"] for entry in st.session_state.stored_data[user]]
    selected = st.selectbox("Select data to delete", names)
    pin = st.text_input("PIN for Verification", type="password")
    if st.button("Delete"):
        if not pin:
            st.error("Enter PIN!")
            return
        fernet = get_fernet_key(pin)
        if not fernet:
            st.error("Invalid PIN!")
            return
        for i, entry in enumerate(st.session_state.stored_data[user]):
            if entry["name"] == selected:
                try:
                    fernet.decrypt(entry["encrypted_data"].encode())
                    st.session_state.stored_data[user].pop(i)
                    if not st.session_state.stored_data[user]:
                        del st.session_state.stored_data[user]
                    save_stored_data(st.session_state.stored_data)
                    log_action(user, "Delete Data", f"Deleted '{selected}'")
                    st.success("Data deleted!")
                    st.session_state.pin_attempts = 0
                    break
                except:
                    st.session_state.pin_attempts += 1
                    log_action(user, "Failed Delete", f"Wrong PIN attempt {st.session_state.pin_attempts}")
                    st.error(f"Wrong PIN! Attempts left: {3 - st.session_state.pin_attempts}")
                    if st.session_state.pin_attempts >= 3:
                        log_action(user, "Lockout", "Logged out due to 3 wrong PINs")
                        st.session_state.authenticated = False
                        st.session_state.current_user = None
                        st.session_state.lockout_time = time.time()
                        st.error("Logged out due to 3 wrong PINs!")
                        st.rerun()
                    break
        else:
            st.error("Data not found!")

def view_history_page():
    st.title("View History")
    user = st.session_state.current_user
    logs = load_logs().get(user, [])
    if not logs:
        st.info("No activity logged.")
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

    if not st.session_state.authenticated:
        if is_locked_out():
            return
        tabs = st.tabs(["Login", "Register"])

        with tabs[0]:  # Login tab
            st.subheader("Login")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login"):
                if login(username, password):
                    st.success("Logged in!")
                    st.session_state.authenticated = True
                    st.session_state.current_user = username
                    st.session_state.pin_attempts = 0
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        with tabs[1]:  # Register tab
            st.subheader("Register")
            username = st.text_input("Username", key="register_username")
            password = st.text_input("Password", type="password", key="register_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
            if st.button("Register"):
                success, message = register(username, password, confirm_password)
                if success:
                    st.success(message)
                else:
                    st.error(message)
        
    else:
        st.success(f"Welcome, {st.session_state.current_user}!")
        menu = ["Home", "Store Data", "Retrieve Data", "Delete Data", "View History", "Logout"]
        choice = st.sidebar.radio("Select option", menu)

        if choice == "Home":
            st.title("🔒 Secure Data Encryption System")
            st.write("Use the sidebar to manage your data.")

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
            st.session_state.pin_attempts = 0
            st.success("Logged out!")
            st.rerun()

if __name__ == "__main__":
    main()