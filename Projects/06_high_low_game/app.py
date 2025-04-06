import streamlit as st
import random

# Initialize session state
if "round" not in st.session_state:
    st.session_state.round = 1
if "score" not in st.session_state:
    st.session_state.score = 0
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "user_number" not in st.session_state:
    st.session_state.user_number = random.randint(1, 100)
if "computer_number" not in st.session_state:
    st.session_state.computer_number = random.randint(1, 100)

# Select number of rounds
number_rounds = st.sidebar.slider("🎮 Select Number of Rounds", 1, 10, 5)

st.title("🎯 Welcome to the High-Low Game!")
st.write("--" * 50)

if not st.session_state.game_over:

    st.subheader(f"🔁 Round {st.session_state.round}")
    st.write(f"Your number is: {st.session_state.user_number}")

    user_input = st.radio("Do you think your number is higher or lower than the computer's?",
                          ["higher", "lower"], key=st.session_state.round)

    if st.button("Submit Guess"):
        user_number = st.session_state.user_number
        computer_number = st.session_state.computer_number

        if (
            (user_input == "higher" and user_number > computer_number) or
            (user_input == "lower" and user_number < computer_number)
        ):
            st.success(f"✅ Correct! The computer's number was {computer_number}")
            st.session_state.score += 1
        else:
            st.error(f"❌ Wrong! The computer's number was {computer_number}")

        st.session_state.round += 1

        if st.session_state.round > number_rounds:
            st.session_state.game_over = True
        else:
            # Prepare next round
            st.session_state.user_number = random.randint(1, 100)
            st.session_state.computer_number = random.randint(1, 100)

else:
    st.write("--" * 50)
    st.subheader(f"🏁 Game Over! Your final score is: {st.session_state.score}/{number_rounds}")
    st.write("--" * 50)

    if st.session_state.score == number_rounds:
        st.balloons()
        st.write("🎉 Wow! You played perfectly!")
    elif st.session_state.score > 2:
        st.write("👏 Good job, you played really well!")
    else:
        st.write("😅 Better luck next time!")

    if st.button("Play Again"):
        # Reset session state
        for key in st.session_state.keys():
            del st.session_state[key]
