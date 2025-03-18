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
    



