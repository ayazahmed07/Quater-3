import streamlit as st
from cryptography.fernet import Fernet
import hashlib
import uuid
import json
import os
import base64
import time
from datetime import datetime

# Initialize session state
if 'stored_data' not in st.session_state:
    st.session_state.stored_data = {}
if 'failed_attempts' not in st.session_state:
    st.session_state.failed_attempts = 0
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'users' not in st.session_state:
    st.session_state.users = {}
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'lockout_time' not in st.session_state:
    st.session_state.lockout_time = 0
if 'logs' not in st.session_state:
    st.session_state.logs = {}

# Load persisted data
def load_data():
    def load_json_file(file_path, default):
        if not os.path.exists(file_path):
            return default
        try:
            with open(file_path, "r") as f:
                content = f.read().strip()
                if not content:
                    st.warning(f"{file_path} is empty. Initializing with default value.")
                    return default
                return json.loads(content)
        except json.JSONDecodeError as e:
            st.warning(f"Invalid JSON in {file_path}: {e}. Initializing with default value.")
            return default
        except Exception as e:
            st.warning(f"Error reading {file_path}: {e}. Initializing with default value.")
            return default

    st.session_state.users = load_json_file("users.json", {})
    serializable_data = load_json_file("data.json", {})
    st.session_state.stored_data = {}
    for user, entries in serializable_data.items():
        if not isinstance(entries, dict):
            st.warning(f"Invalid data format for user {user} in data.json. Skipping.")
            continue
        st.session_state.stored_data[user] = {}
        for data_id, entry in entries.items():
            if not isinstance(entry, dict):
                st.warning(f"Invalid entry format for data ID {data_id} of user {user}. Skipping.")
                continue
            try:
                st.session_state.stored_data[user][data_id] = {
                    "name": entry.get("name", "Unnamed"),
                    "encrypted_data": base64.b64decode(entry["encrypted_data"]),
                    "key": base64.b64decode(entry["key"]),
                    "passkey": entry["passkey"]
                }
            except (KeyError, ValueError) as e:
                st.warning(f"Error processing entry {data_id} for user {user}: {e}. Skipping.")
    st.session_state.logs = load_json_file("logs.json", {})

# Save data to JSON
def save_data():
    with open("users.json", "w") as f:
        json.dump(st.session_state.users, f)
    with open("data.json", "w") as f:
        serializable_data = {}
        for user, entries in st.session_state.stored_data.items():
            serializable_data[user] = {}
            for data_id, entry in entries.items():
                serializable_data[user][data_id] = {
                    "name": entry["name"],
                    "encrypted_data": base64.b64encode(entry["encrypted_data"]).decode(),
                    "key": base64.b64encode(entry["key"]).decode(),
                    "passkey": entry["passkey"]
                }
        json.dump(serializable_data, f)
    with open("logs.json", "w") as f:
        json.dump(st.session_state.logs, f)

# Load data on app start
load_data()

def hash_passkey(passkey):
    """Hash the passkey or password using SHA-256."""
    return hashlib.sha256(passkey.encode()).hexdigest()

def encrypt_data(data, passkey):
    """Encrypt data using a generated Fernet key."""
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data.encode())
    return encrypted_data, key

def decrypt_data(encrypted_data, key):
    """Decrypt data using the provided key."""
    try:
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data).decode()
        return decrypted_data
    except:
        return None

def log_action(username, action, details=""):
    """Log a user action with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if username not in st.session_state.logs:
        st.session_state.logs[username] = []
    st.session_state.logs[username].append({
        "action": action,
        "timestamp": timestamp,
        "details": details
    })
    save_data()

def is_locked_out():
    """Check if the user is locked out and display countdown."""
    if st.session_state.failed_attempts >= 3:
        elapsed = time.time() - st.session_state.lockout_time
        if elapsed < 30:
            remaining = int(30 - elapsed)
            st.warning(f"Too many failed attempts. Please wait {remaining} seconds.")
            return True
        else:
            st.session_state.failed_attempts = 0
            st.session_state.lockout_time = 0
    return False

def main():
    if not st.session_state.authenticated:
        menu = ["Login", "Register"]
        choice = st.sidebar.selectbox("Select an option", menu)
        if choice == "Login":
            login_page()
        elif choice == "Register":
            register_page()
        return
    
    st.title("Secure Data Storage System")
    # Admin menu if user is admin
    menu = ["Home", "Store Data", "Retrieve Data", "Delete Data", "View History", "Logout"]
    if st.session_state.current_user == "admin":
        menu.insert(-1, "Admin Panel")
    choice = st.sidebar.selectbox("Select an option", menu)

    if choice == "Home":
        st.write(f"Welcome, {st.session_state.current_user}! Use the sidebar to manage your data.")
    
    elif choice == "Store Data":
        store_data_page()
    
    elif choice == "Retrieve Data":
        retrieve_data_page()
    
    elif choice == "Delete Data":
        delete_data_page()
    
    elif choice == "View History":
        view_history_page()
    
    elif choice == "Admin Panel" and st.session_state.current_user == "admin":
        admin_panel_page()
    
    elif choice == "Logout":
        log_action(st.session_state.current_user, "Logout", "User logged out")
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.session_state.failed_attempts = 0
        st.success("Logged out successfully!")
        st.rerun()

def register_page():
    st.title("Register")
    st.markdown("Create a new account to start storing data securely.")
    with st.form(key="register_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Register")
    
    if submit:
        if not username or not password or not confirm_password:
            st.error("Please fill all fields.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        elif username in st.session_state.users:
            st.error("Username already exists.")
        else:
            hashed_password = hash_passkey(password)
            st.session_state.users[username] = hashed_password
            log_action(username, "Register", "User account created")
            save_data()
            st.success("Registration successful! Please log in.")

def login_page():
    st.title("Login")
    st.markdown("Enter your credentials to access your data.")
    if is_locked_out():
        return
    
    with st.form(key="login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
    
    if submit:
        if username in st.session_state.users:
            hashed_password = hash_passkey(password)
            if hashed_password == st.session_state.users[username]:
                st.session_state.authenticated = True
                st.session_state.current_user = username
                st.session_state.failed_attempts = 0
                st.session_state.lockout_time = 0
                log_action(username, "Login", "Successful login")
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.session_state.failed_attempts += 1
                st.error(f"Invalid password. Attempts left: {3 - st.session_state.failed_attempts}")
                log_action(username, "Failed Login", "Invalid password")
                if st.session_state.failed_attempts >= 3:
                    st.session_state.lockout_time = time.time()
                    st.warning("Too many failed attempts. Locked out for 30 seconds.")
        else:
            st.session_state.failed_attempts += 1
            st.error(f"Username not found. Attempts left: {3 - st.session_state.failed_attempts}")
            log_action(username, "Failed Login", "Username not found")
            if st.session_state.failed_attempts >= 3:
                st.session_state.lockout_time = time.time()
                st.warning("Too many failed attempts. Locked out for 30 seconds.")

def store_data_page():
    st.title("Store Data")
    st.markdown("Enter a name and data to encrypt with a passkey.")
    with st.form(key="store_data_form"):
        data_name = st.text_input("Data Name (e.g., My Note)")
        data = st.text_area("Enter data to store")
        passkey = st.text_input("Enter your passkey", type="password")
        submit = st.form_submit_button("Store Data")
    
    if submit:
        if data and passkey and data_name:
            data_id = str(uuid.uuid4())
            username = st.session_state.current_user
            hashed_passkey = hash_passkey(passkey)
            encrypted_data, key = encrypt_data(data, passkey)
            if username not in st.session_state.stored_data:
                st.session_state.stored_data[username] = {}
            st.session_state.stored_data[username][data_id] = {
                "name": data_name,
                "encrypted_data": encrypted_data,
                "key": key,
                "passkey": hashed_passkey
            }
            log_action(username, "Store Data", f"Stored data '{data_name}' with ID {data_id}")
            save_data()
            st.success("Data stored successfully!")
        else:
            st.error("Please enter data name, data, and passkey.")

def retrieve_data_page():
    st.title("Retrieve Data")
    st.markdown("Select a data entry and enter its passkey to decrypt it.")
    if is_locked_out():
        return
    
    username = st.session_state.current_user
    if username not in st.session_state.stored_data or not st.session_state.stored_data[username]:
        st.info("No data stored yet.")
        return
    
    data_entries = [(data_id, entry["name"]) for data_id, entry in st.session_state.stored_data[username].items()]
    display_options = [f"{name} (ID: {data_id})" for data_id, name in data_entries]
    selected_option = st.selectbox("Select data entry", display_options)
    selected_data_id = next(data_id for data_id, name in data_entries if f"{name} (ID: {data_id})" == selected_option)
    passkey = st.text_input("Enter your passkey", type="password")
    
    if st.button("Retrieve Data"):
        stored = st.session_state.stored_data[username][selected_data_id]
        hashed_passkey = hash_passkey(passkey)
        if hashed_passkey == stored["passkey"]:
            decrypted_data = decrypt_data(stored["encrypted_data"], stored["key"])
            if decrypted_data:
                st.success("Data retrieved successfully!")
                st.write("Decrypted Data:", decrypted_data)
                log_action(username, "Retrieve Data", f"Retrieved data '{stored['name']}' with ID {selected_data_id}")
                st.session_state.failed_attempts = 0
                st.session_state.lockout_time = 0
            else:
                st.error("Failed to decrypt data.")
                log_action(username, "Failed Retrieve", f"Failed to decrypt data ID {selected_data_id}")
        else:
            st.session_state.failed_attempts += 1
            st.error(f"Wrong passkey. Attempts left: {3 - st.session_state.failed_attempts}")
            log_action(username, "Failed Retrieve", f"Wrong passkey for data ID {selected_data_id}")
            if st.session_state.failed_attempts >= 3:
                st.session_state.lockout_time = time.time()
                st.warning("Too many failed attempts. Locked out for 30 seconds.")

def delete_data_page():
    st.title("Delete Data")
    st.markdown("Select a data entry and enter its passkey to delete it permanently.")
    if is_locked_out():
        return
    
    username = st.session_state.current_user
    if username not in st.session_state.stored_data or not st.session_state.stored_data[username]:
        st.info("No data stored yet.")
        return
    
    data_entries = [(data_id, entry["name"]) for data_id, entry in st.session_state.stored_data[username].items()]
    display_options = [f"{name} (ID: {data_id})" for data_id, name in data_entries]
    selected_option = st.selectbox("Select data entry to delete", display_options)
    selected_data_id = next(data_id for data_id, name in data_entries if f"{name} (ID: {data_id})" == selected_option)
    passkey = st.text_input("Enter your passkey", type="password")
    confirm_delete = st.checkbox("Confirm deletion (this action cannot be undone)")
    
    if st.button("Delete Data", disabled=not confirm_delete):
        if not passkey:
            st.error("Please enter the passkey.")
            return
        stored = st.session_state.stored_data[username][selected_data_id]
        hashed_passkey = hash_passkey(passkey)
        if hashed_passkey == stored["passkey"]:
            data_name = stored["name"]
            del st.session_state.stored_data[username][selected_data_id]
            if not st.session_state.stored_data[username]:
                del st.session_state.stored_data[username]
            log_action(username, "Delete Data", f"Deleted data '{data_name}' with ID {selected_data_id}")
            save_data()
            st.success("Data deleted successfully!")
            st.session_state.failed_attempts = 0
            st.session_state.lockout_time = 0
        else:
            st.session_state.failed_attempts += 1
            st.error(f"Wrong passkey. Attempts left: {3 - st.session_state.failed_attempts}")
            log_action(username, "Failed Delete", f"Wrong passkey for data ID {selected_data_id}")
            if st.session_state.failed_attempts >= 3:
                st.session_state.lockout_time = time.time()
                st.warning("Too many failed attempts. Locked out for 30 seconds.")

def view_history_page():
    st.title("View History")
    st.markdown("View your activity log with timestamps.")
    username = st.session_state.current_user
    if username not in st.session_state.logs or not st.session_state.logs[username]:
        st.info("No activity logged yet.")
        return
    
    st.subheader("Your Activity Log")
    logs = st.session_state.logs[username]
    log_data = [{"Timestamp": log["timestamp"], "Action": log["action"], "Details": log["details"]} for log in logs]
    st.table(log_data)

def admin_panel_page():
    st.title("Admin Panel")
    st.markdown("View activity logs for all users.")
    if not st.session_state.logs:
        st.info("No user activity logged yet.")
        return
    
    st.subheader("All User Activity Logs")
    all_logs = []
    for username, user_logs in st.session_state.logs.items():
        for log in user_logs:
            all_logs.append({
                "Username": username,
                "Timestamp": log["timestamp"],
                "Action": log["action"],
                "Details": log["details"]
            })
    if all_logs:
        st.table(all_logs)
    else:
        st.info("No logs available.")

if __name__ == "__main__":
    main()