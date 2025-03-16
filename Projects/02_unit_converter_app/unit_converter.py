import streamlit as st # streamlit is a library for building web apps

# function to convert units based on predefined conversions factors

def convert_units(value, unit_from, unit_to):

    conversions = {
        "meters_kilometers": 0.001, # 1 meter = 0.001 Kilometer
        "kilometers_meters": 1000,  # 1 Kilometer = 1000 meter
        "grams_kilograms": 0.001,  # 1 gram = 0.001 Kilogram
        "kilograms_grams": 1000,   # 1 Kilogram = 1000 gram
        
    }

    key = f"{unit_from}_{unit_to}" # Generate a unique key for the conversion based on the unit from and unit to

    # logic to convert units
    if key in conversions:
        conversion = conversions[key]
        return value * conversion
    else: 
        return("Conversion not supported") # if the conversion is not supported, return this message

# streamlit app
st.title("Unit Converter") # set the title of the app

value = st.number_input("Enter the value:", min_value=1.0, step=1.0) # create a number input for the value

unit_from = st.selectbox("Convert from:", ["meters", "kilometers", "grams", "kilograms"]) # dropdown menu for the unit from

unit_to = st.selectbox("Convert to:", ["meters", "kilometers", "grams", "kilograms"]) # dropdown menu for the unit to

if st.button("Convert Now"): # create a button to convert the value
    result = convert_units(value, unit_from, unit_to) # call the convert_units function
    st.success(f"The converted value is: {result}") # display the result