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

st.title("Welcome to your Perosnal Library Manager")

menu = st.sidebar.radio("Select an option", ["Add Book", "View Library", "Remove Book", "Search Book", "View Statistics", "Edit/Update Book", "Save and Exit" ])

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
            st.session_state["success_message"] = "Book Added Successfuly!"
            st.rerun()
            
if "success_message" in st.session_state:
    st.success(st.session_state["success_message"])
    del st.session_state["success_message"]  # Remove message after displaying

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
        
        
# view stats
        
elif menu == "View Statistics":
    st.sidebar.title("View Statistics")
    
    if library:
             
        total_books = len(library)
        read_books = sum(1 for book in library if book ["read_status"])
        read_percentage = (read_books / total_books) * 100 if total_books > 0 else 0
        
        st.markdown("###  Library Statistics")
        st.write(f" **Total Books:** {total_books}")
        st.write(f" **Books Read:** {read_books} ({read_percentage:.2f}%)")
    
    else:
        st.error("No Books in your library... Add books now!!")


#Edit/Update
        
elif menu == "Edit/Update Book":
    st.sidebar.title("Edit/Update a Book")

    search_term = st.text_input("Enter book title or author name to search the book")

    if search_term.strip():
        results = [book for book in library if search_term.lower() in book["title"].lower() or search_term.lower() in book["author"].lower()]
        if results:
            selected_book_title = st.selectbox("Select a book to edit", [book["title"] for book in results])

            # Get the selected book's index and object
            book_index = next((i for i, book in enumerate(library) if book["title"] == selected_book_title), None)
            book_to_edit = library[book_index] if book_index is not None else None

            if book_to_edit:
                new_title = st.text_input("Title", book_to_edit["title"])
                new_author = st.text_input("Author", book_to_edit["author"])
                new_year = st.number_input("Year", min_value=1900, max_value=2100, step=1, value=book_to_edit["year"])
                new_genre = st.text_input("Genre", book_to_edit["genre"])
                new_read_status = st.checkbox("Mark as Read", book_to_edit["read_status"])

                if st.button("Update Book"):
                    # 🔹 Check if the new title already exists in another book (excluding the one being edited)
                    if new_title.lower() != book_to_edit["title"].lower() and any(book["title"].lower() == new_title.lower() for book in library if book != book_to_edit):
                        st.error("A book with this title already exists! Choose a different title.")
                    else:
                        # 🔥 Update book in place to keep the order unchanged
                        library[book_index] = {
                            "title": new_title,
                            "author": new_author,
                            "year": new_year,
                            "genre": new_genre,
                            "read_status": new_read_status
                        }

                        save_library()
                        st.session_state["success_message"] = f"'{selected_book_title}' updated successfully!"
                        st.rerun()

        else:
            st.warning("No matching book found!")

    # Display success message
    if "success_message" in st.session_state:
        st.success(st.session_state["success_message"])
        del st.session_state["success_message"]
        
#save and exit

elif menu == "Save and Exit":
    save_library()
    st.success("Library Saved Successfuly!!")