import streamlit as st
import json

# Custom CSS to make all text green
custom_css = """
<style>
   
    /* Buttons */
    .stButton > button {
        background-color: #ff5722 !important; /* Orange button */
        color: #00FF00 !important; /* Green text */
        border-radius: 8px;
        border: none;
    }

    .stButton > button:hover {
        background-color: #e64a19 !important; /* Darker orange */
    }
 
</style>
"""

# Inject CSS into Streamlit
st.markdown(custom_css, unsafe_allow_html=True)


# load and save the library data

def load_library():
    try: 
        with open("library.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    

def save_library():
    with open("library.json", "w") as file:
        json.dump(library, file, indent=4)

library = load_library()

st.title("Perosnal Library Manager")

menu = st.sidebar.radio("Select an option", ["Add Book", "View Library", "Remove Book", "Search Book", "Edit/Update Book", "Save and Exit" ])

# add book

if menu == "Add Book":
    st.sidebar.title("Add a new Book")
    title = st.text_input("Title")
    author = st.text_input("Author")
    year = st.number_input("Year", min_value=1990, max_value=2100, step=1)
    genre = st.text_input("Genre")
    read_status = st.checkbox("Mark as Read")

    if st.button("Add Your Book"):
        
        if not title.strip():
            st.error("Title is required!!")
        elif not author.strip():
            st.error("Author is required!")
        elif any(book["title"].lower() == title.lower() for book in library):
            st.error("A Book with this title is already exists!!")

        else:
            library.append({"title": title, "author": author, "year": year, "genre": genre, "read_status": read_status})
            save_library()
            st.success("Book Added Successfuly!")
            st.session_state["book added"] = True
            st.experimental_rerun()

elif menu == "View Library":

    st.sidebar.title("Your Library")

    if library:
        st.table(library)
    else:
        st.error("No Books in your library... Add books now!!")


# remove book

elif menu == "Remove Book":
    st.sidebar.title("Remove a book")
    
    if library:
        book_titles = [book["title"] for book in library]
        selected_books = st.multiselect("Select books to remove", book_titles)

        if st.button("Remove Selected Books"):
            library = [book for book in library if book["title"] not in selected_books]
            save_library()
            st.success("Selected Books removed successfuly!")
            st.rerun()
    else:
        st.warning("No books in the library to remove... Add a book!")


#search book

elif menu == "Search Book":
    st.sidebar.title("Search a book")
    search_term = st.text_input("Enter title or author name")
    
    if st.button("Search") and search_term.strip():
        results = [book for book in library if search_term.lower() in book["title"].lower() or search_term.lower() in book["author"].lower()]
        if results:
            st.table(results)
        else:
            st.warning("No book found!")

    elif not search_term.strip():
        st.warning("Please enter a search term")
        

#Edit/Update
        
elif menu == "Edit/Update Book":
    st.sidebar.title("Edit/Update a Book")
    book_titles = [book["title"] for book in library]

    if book_titles:
        selected_book = st.selectbox("Select a book to edit", ["Select a book"] + book_titles)

        if selected_book != "Select a book":
            book_to_edit = next((book for book in library if book["title"] == selected_book), None)

            if book_to_edit:
                new_title = st.text_input("Title", book_to_edit["title"])
                new_author = st.text_input("Author", book_to_edit["author"])
                new_year = st.number_input("Year", min_value=1900, max_value=2100, step=1, value=book_to_edit["year"])
                new_genre = st.text_input("Genre", book_to_edit["genre"])  # ✅ Fixed key
                new_read_status = st.checkbox("Mark as Read", book_to_edit["read_status"])

                if st.button("Update Book"):
                    book_to_edit.update({"title": new_title, "author": new_author, "year": new_year, "genre": new_genre, "read_status": new_read_status})
                    save_library()
                    st.success(f"'{selected_book}' updated successfully!")  # ✅ Message now displays
                    st.rerun()
    else:
        st.warning("No books available to edit.")


#save and exit

elif menu == "Save and Exit":
    save_library()
    st.success("Library Saved Successfuly!!")