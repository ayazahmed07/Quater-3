import streamlit as st
from cryptography.fernet import Fernet
import hashlib
import json
import os

# --------------- Session Initialization ---------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "logged_user" not in st.session_state:
    st.session_state.logged_user = ""

if "cipher" not in st.session_state:
    st.session_state.cipher_key = Fernet.generate_key()
    st.session_state.cipher = Fernet(st.session_state.cipher_key)

if "stored_data" not in st.session_state:
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            st.session_state.stored_data = json.load(f)
    else:
        st.session_state.stored_data = {}

cipher = st.session_state.cipher
stored_data = st.session_state.stored_data

# --------------- Streamlit UI -------------------------
st.title("🔐 Secure Data Encryption System")

menu = st.sidebar.radio("Select an option", ["Home", "Encrypt Data", "Decrypt Data", "Login"])

if menu == "Home":
    st.write("Welcome to the Secure Data Encryption System! Choose an option from the sidebar.")

# --------------- Encrypt Data -------------------------
elif menu == "Encrypt Data":
    user_name = st.text_input("Enter your user name")
    user_data = st.text_area("Enter the data you want to encrypt:")
    passkey = st.text_input("Enter a passkey:", type="password")

    if st.button("Encrypt Data"):
        if not user_name or not user_data or not passkey:
            st.warning("All fields are required.")
        else:
            hashed_passkey = hashlib.sha256(passkey.encode()).hexdigest()
            encrypted_data = cipher.encrypt(user_data.encode()).decode()

            stored_data[user_name] = {
                "encrypted_data": encrypted_data,
                "hashed_passkey": hashed_passkey,
                "attempts": 0
            }

            # Save to file
            with open("data.json", "w") as datafile:
                json.dump(stored_data, datafile)

            st.success("✅ Data encrypted and stored successfully!")

# --------------- Decrypt Data -------------------------
elif menu == "Decrypt Data":
    user_name = st.text_input("Enter your user name")
    passkey = st.text_input("Enter your passkey:", type="password")

    if st.button("Decrypt Data"):
        if user_name in stored_data:
            if stored_data[user_name]["attempts"] >= 3:
                st.sidebar.error(f"Too many failed attempts. Access denied for user '{user_name}'. Please login again.")
            else:
                hashed = hashlib.sha256(passkey.encode()).hexdigest()
                if hashed == stored_data[user_name]["hashed_passkey"]:
                    decrypted_data = cipher.decrypt(stored_data[user_name]["encrypted_data"].encode()).decode()
                    st.success(f"🔓 Decrypted data: {decrypted_data}")
                    stored_data[user_name]["attempts"] = 0

                    # Optional: Save after success
                    with open("data.json", "w") as datafile:
                        json.dump(stored_data, datafile)
                else:
                    stored_data[user_name]["attempts"] += 1
                    st.error("❌ Wrong passkey!")
                    st.sidebar.info(f"Attempts: {stored_data[user_name]['attempts']} / 3")

                    # Optional: Save after failed attempt
                    with open("data.json", "w") as datafile:
                        json.dump(stored_data, datafile)
        else:
            st.error("❌ User not found.")

# --------------- Login Page -------------------------
elif menu == "Login":
    st.header("🔐 Reauthorization Required")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in stored_data and hashlib.sha256(password.encode()).hexdigest() == stored_data[username]["hashed_passkey"]:
            stored_data[username]["attempts"] = 0
            st.session_state.logged_in = True
            st.session_state.logged_user = username

            # Save reset attempts
            with open("data.json", "w") as datafile:
                json.dump(stored_data, datafile)

            st.success("🔓 Login successful! Go to 'Decrypt Data'")
        else:
            st.error("❌ Invalid login.")
