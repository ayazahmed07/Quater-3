import streamlit as st
import random


def high_low_game(number_rounds):
    score = 0
    st.title("🎯 Welcome to the High-Low Game!")

    st.write("--" * 50)

    for rounds in range(1, number_rounds + 1):

        user_number: int = random.randint(1, 100)
        computer_number: int = random.randint(1,100)


        st.write("--" * 50)

        st.write(f"🔁 Round {rounds} ")

        st.write("--" * 50)
  
        st.write(f"Your number is {user_number}")
        

        user_input: str = st.radio("Do you think your number is higher or lower than the computer's?", ["higher", "lower"], key=rounds)

        if (
            (user_input == "higher" and computer_number < user_number) 
            or
            (user_input == "lower" and computer_number > user_number)
           ):
            st.title(f"✅You were right your score is +1.! The computer's number was {computer_number}")
      
            score += 1

        else:
            st.title(f"❌ you are wrong! The computer's guess is {computer_number}")


    st.write("--" * 50)
    st.write(f"🏁 Your final score is: {score}")
    st.write("--" * 50)

    if (score == number_rounds):
        st.write("Wow! You played perfectly!")
    elif (score < number_rounds and score > 2):
        st.write("Good job, you played really well!")
    else:
        st.write("Better luck next time!")

number_rounds = st.sidebar.slider("🎮 Select Number of Rounds", 1, 10, 5)

high_low_game(number_rounds)
