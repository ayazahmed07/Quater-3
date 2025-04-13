import streamlit as st
from cryptography.fernet import Fernet
import json
import hashlib

Furnet = Fernet.generate_key()

def passkey


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
            encrypted_data = encrypt_data(data)
            st.success("Data Stored Successfuly!")
        else:
            st.error("Please enter both data and passkey")

    
