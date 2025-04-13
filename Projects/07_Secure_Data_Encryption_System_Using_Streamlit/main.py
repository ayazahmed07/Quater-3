import streamlit as st

import json
import hashlib

st.title("Secure Data Encryption System")

menu = ["Home Page", "Store Data", "Retrieve Data", "Login"]
choice = st.sidebar._selectbox("Navigation", menu)