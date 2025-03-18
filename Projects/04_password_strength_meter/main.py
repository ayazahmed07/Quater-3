import streamlit as st
import random
import string  #provide specific letters
import pandas as pd

st.title("PASSWORD GENERATOR")

def password_generator(length, use_digits, use_special):
    characters = string.ascii_letters
    if use_digits:
        characters += string.digits
        
    if use_special:
        characters += string.punctuation
    
    return ''.join(random.choice(characters) for _ in range(length))

length = st.slider("Select Password Length", min_value=8, max_value=14, value=12)

use_digits = st.checkbox("Include Digits")

use_special = st.checkbox("Include Specail Characters")

if st.button("Generate Password"):

    password = password_generator(length, use_digits, use_special)
    st.subheader(f"Generated Password: {password}")
    
st.write("-------------------------------------")

st.write("Build with love by Ayaz Ahmed")




