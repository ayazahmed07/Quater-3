import streamlit as st # streamlit is a library for building web apps
import requests  # requests is a library for making HTTP requests


# function to convert units based on predefined conversions factors

def convert_units(value, unit_from, unit_to):

    conversions = {
        "meters_kilometers": 0.001, # 1 meter = 0.001 Kilometer
        "kilometers_meters": 1000,  # 1 Kilometer = 1000 meter
        "grams_kilograms": 0.001,  # 1 gram = 0.001 Kilogram
        "kilograms_grams": 1000,   # 1 Kilogram = 1000 gram
        "inches_centimeters": 2.54,
        "centimeters_inches": 0.3937,
              
    }

    key = f"{unit_from}_{unit_to}" # Generate a unique key for the conversion based on the unit from and unit to

    # logic to convert units
    if key in conversions:
        conversion = conversions[key]
        return value * conversion
    else: 
        return("Conversion not supported") # if the conversion is not supported, return this message
    


def currency_converter(amount, currency_from, currency_to):
    url = f"https://v6.exchangerate-api.com/v6/85957b0d4ae5be335d2963dd/latest/{currency_from}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        rate = data["conversion_rates"][currency_to]
        if rate:
            return amount * rate
        return "Conversion rate not found"
    else:
        return "Failed to fetch data from API"
    
# streamlit app
st.title("Multi Purpose Converter") # set the title of the app

options = st.radio("Select conversion type:", ["Unit Conversion", "Currency Conversion"]) # create a radio button for the conversion type

if options == "Currency Conversion":
    st.subheader("Currency Conversion")
    amount = st.number_input("Enter the amount:", min_value=1.0,) # create a number input for the amount
    currency_from = st.selectbox("Convert from:", ["USD", "EUR", "GBP", "INR", "PKR", "AED",]) # dropdown menu for the currency from
    currency_to = st.selectbox("Convert to:", ["USD", "EUR", "GBP", "INR", "PKR", "AED"]) # dropdown menu for the currency to

    if st.button("Convert Currency"): # create a button to convert the value
        result = currency_converter(amount, currency_from, currency_to) # call the currency_converter function
        st.success(f"The converted value is: {result}") # display the result


if options == "Unit Conversion":
    st.subheader("Unit Conversion")
    value = st.number_input("Enter the value:", min_value=1.0, step=1.0) # create a number input for the value

    unit_from = st.selectbox("Convert from:", ["Meters", "Kilometers", "Grams", "Kilograms", "Inches", "Centimeters",]) # dropdown menu for the unit from

    unit_to = st.selectbox("Convert to:", ["Meters", "Kilometers", "Grams", "Kilograms", "Inches", "Centimeters",]) # dropdown menu for the unit to

    if st.button("Convert Units"): # create a button to convert the value
        result = convert_units(value, unit_from, unit_to) # call the convert_units function
        st.success(f"The converted value is: {result}") # display the result