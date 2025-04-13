import streamlit as st
from cryptography.fernet import Fernet
import json
import hashlib

Key = Fernet.generate_key()
cipher = Fernet(Key)

stored_data = {}
failed_attempts = 0

def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

# Function to encrypt data
def encrypt_data(text, passkey):
    return cipher.encrypt(text.encode()).decode()

# Function to decrypt data
def decrypt_data(encrypted_text, passkey):
    global failed_attempts
    hashed_passkey = hash_passkey(passkey)

    for key, value in stored_data.items():
        if value["encrypted_text"] == encrypted_text and value["passkey"] == hashed_passkey:
            failed_attempts = 0
            return cipher.decrypt(encrypted_text.encode()).decode()
    
    failed_attempts += 1
    return None


# Streamlit UI

st.title("Secure Data Encryption System")

# Navigation
menu = ["Home", "Store Data", "Retrieve Data", "Login"]
choice = st.sidebar.selectbox("Navigation", menu)

if choice == "Home":    
    st.subheader("🏠 Welcome to the Secure Data System")
    st.write("Use this app to **securely store and retrieve data** using unique passkeys.")

elif choice == "Store Data":
    st.subheader("Store Your Data")
    user_data = st.text_area("Enter Your Data")
    passkey = st.text_input("Enter your pass key:", type="password")

    if st.button("Encrypt & Save"):
        if user_data and passkey:
            hashed_passkey = hash_passkey(passkey)
            encrypted_data = encrypt_data(user_data, passkey)
            st.success("Data Stored Successfuly!")
        else:
            st.error("Please enter both data and passkey")

    
