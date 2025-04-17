import sqlite3
import streamlit as st
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
import os

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('bank_accounts.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS accounts 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  account_number TEXT, 
                  account_title TEXT, 
                  bank_name TEXT, 
                  branch_name TEXT, 
                  address TEXT,''')
                  
    conn.commit()
    conn.close()

# Add a new bank account
def add_account(account_number, account_title, bank_name, branch_name, address):
    conn = sqlite3.connect('bank_accounts.db')
    c = conn.cursor()
    c.execute('''INSERT INTO accounts (account_number, account_title, bank_name, branch_name, address) 
                 VALUES (?, ?, ?, ?, ?, ?)''', 
              (account_number, account_title, bank_name, branch_name, address))
    conn.commit()
    conn.close()

# Edit an existing bank account
def edit_account(account_id, account_number, account_title, bank_name, branch_name, address):
    conn = sqlite3.connect('bank_accounts.db')
    c = conn.cursor()
    c.execute('''UPDATE accounts 
                 SET account_number = ?, account_title = ?, bank_name = ?, branch_name = ?, address = ?, 
                 WHERE id = ?''', 
              (account_number, account_title, bank_name, branch_name, address, account_id))
    conn.commit()
    conn.close()

# Fetch accounts for dropdown
def get_accounts():
    try:
        conn = sqlite3.connect('bank_accounts.db')
        c = conn.cursor()
        c.execute("SELECT id, account_title, account_number, bank_name, branch_name, address, FROM accounts")
        accounts = c.fetchall()
        conn.close()
        return accounts
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return []

# Generate PDF letter
def generate_letter(account_id, selected_date, request_type, from_date=None, to_date=None, signature_name=""):
    conn = sqlite3.connect('bank_accounts.db')
    c = conn.cursor()
    c.execute("SELECT account_title, account_number, bank_name, branch_name, address, FROM accounts WHERE id = ?", (account_id,))
    account = c.fetchone()
    conn.close()
    
    if not account:
        st.error("Account not found")
        return None
    
    account_title, account_number, bank_name, branch_name, address, manager_name = account
    formatted_date = datetime.strptime(selected_date, '%Y-%m-%d').strftime('%d %B %Y')
    
    # Create PDF
    pdf_file = 'bank_letter.pdf'
    c = canvas.Canvas(pdf_file, pagesize=A4)
    
    # Date on the right
    c.setFont("Times-Roman", 12)
    c.drawRightString(19 * cm, 27 * cm, formatted_date)
    
    # Manager and bank details
    y = 25 * cm
    c.drawString(2 * cm, y, "The Manager")
    y -= 0.5 * cm
    c.drawString(2 * cm, y, bank_name)
    y -= 0.5 * cm
    c.drawString(2 * cm, y, branch_name)
    y -= 0.5 * cm
    c.drawString(2 * cm, y, address)
    
    # Subject (bold)
    y -= 1 * cm
    c.setFont("Times-Bold", 12)
    c.drawString(2 * cm, y, "Subject: Request for " + ("Bank Statement" if request_type == "Bank Statement" else "Cheque Book" if request_type == "Cheque Book" else "Bank Statement and Cheque Book"))
    
    # Greeting
    y -= 1 * cm
    c.setFont("Times-Roman", 12)
    c.drawString(2 * cm, y, "Dear Sir")
    
    # Body
    y -= 1 * cm
    c.drawString(2 * cm, y, f"I, {account_title}, hold an account in your branch, account details are as follows:")
    
    # Account details (left-aligned, bold)
    y -= 1 * cm
    c.setFont("Times-Bold", 12)
    c.drawString(2 * cm, y, f"Account Title: {account_title}")
    y -= 0.5 * cm
    c.drawString(2 * cm, y, f"Account Number: {account_number}")
    y -= 0.5 * cm
    c.drawString(2 * cm, y, f"Bank Name: {bank_name}")
    y -= 0.5 * cm
    c.drawString(2 * cm, y, f"Branch: {branch_name}")
    y -= 0.5 * cm
    c.drawString(2 * cm, y, f"Address: {address}")
    
    # Request details
    y -= 1 * cm
    c.setFont("Times-Roman", 12)
    if request_type == "Bank Statement":
        from_date_str = datetime.strptime(from_date, '%Y-%m-%d').strftime('%d %B %Y')
        to_date_str = datetime.strptime(to_date, '%Y-%m-%d').strftime('%d %B %Y')
        c.drawString(2 * cm, y, f"I kindly request you to provide the account statement for the period from {from_date_str} to {to_date_str}.")
        y -= 0.5 * cm
    elif request_type == "Cheque Book":
        c.drawString(2 * cm, y, "I kindly request you to issue a new cheque book for the above-mentioned account.")
        y -= 0.5 * cm
    else:  # Both
        from_date_str = datetime.strptime(from_date, '%Y-%m-%d').strftime('%d %B %Y')
        to_date_str = datetime.strptime(to_date, '%Y-%m-%d').strftime('%d %B %Y')
        c.drawString(2 * cm, y, f"I kindly request you to provide the account statement for the period from {from_date_str} to {to_date_str} and")
        y -= 0.5 * cm
        c.drawString(2 * cm, y, "issue a new cheque book for the above-mentioned account.")
        y -= 0.5 * cm
          
    # Closing
    y -= 1 * cm
    c.drawString(2 * cm, y, "Thank you for your assistance.")
    y -= 1 * cm
    c.drawString(2 * cm, y, "Sincerely,")
    
    # Signature line
    y -= 1 * cm
    c.line(2 * cm, y, 6 * cm, y)  # Signature line
    y -= 0.5 * cm
    c.drawString(2 * cm, y, signature_name if signature_name else account_title)
    
    c.showPage()
    c.save()
    return pdf_file

# Streamlit app
def main():
    st.title("Bank Letter Generator")
    
    # Initialize database
    init_db()
    
    # Tabs for Add, Edit, and Print
    tab1, tab2, tab3 = st.tabs(["Add Account", "Edit Account", "Print Letter"])
    
    # Add Account Tab
    with tab1:
        st.header("Add a New Bank Account")
        with st.form("add_account_form"):
            account_number = st.text_input("Account Number", placeholder="e.g., 1234567890")
            account_title = st.text_input("Account Title", placeholder="e.g., John Doe")
            bank_name = st.text_input("Bank Name", placeholder="e.g., ABC Bank")
            branch_name = st.text_input("Branch Name", placeholder="e.g., Main Branch")
            address = st.text_input("Address", placeholder="e.g., 123 Bank Street, City")
            submit_button = st.form_submit_button("Add Account")
            
            if submit_button:
                if all([account_number, account_title, bank_name, branch_name, address,]):
                    add_account(account_number, account_title, bank_name, branch_name, address, )
                    st.success("Bank account added successfully!")
                else:
                    st.error("All fields are required!")
    
    # Edit Account Tab
    with tab2:
        st.header("Edit Selected Account")
        accounts = get_accounts()
        account_options = [(f"{acc[1]} - {acc[2]} ({acc[3]})", acc[0]) for acc in accounts] if accounts else [("No accounts available", 0)]
        selected_account_id = st.selectbox("Select Account", options=account_options, format_func=lambda x: x[0], key="edit_select")
        
        if selected_account_id[1] != 0:
            conn = sqlite3.connect('bank_accounts.db')
            c = conn.cursor()
            c.execute("SELECT account_number, account_title, bank_name, branch_name, address, manager_name FROM accounts WHERE id = ?", (selected_account_id[1],))
            account = c.fetchone()
            conn.close()
            
            with st.form("edit_account_form"):
                edit_account_number = st.text_input("Account Number", value=account[0], placeholder="e.g., 1234567890")
                edit_account_title = st.text_input("Account Title", value=account[1], placeholder="e.g., John Doe")
                edit_bank_name = st.text_input("Bank Name", value=account[2], placeholder="e.g., ABC Bank")
                edit_branch_name = st.text_input("Branch Name", value=account[3], placeholder="e.g., Main Branch")
                edit_address = st.text_input("Address", value=account[4], placeholder="e.g., 123 Bank Street, City")
                edit_button = st.form_submit_button("Edit Account")
                
                if edit_button:
                    if all([edit_account_number, edit_account_title, edit_bank_name, edit_branch_name, edit_address]):
                        edit_account(selected_account_id[1], edit_account_number, edit_account_title, edit_bank_name, edit_branch_name, edit_address)
                        st.success("Bank account updated successfully!")
                    else:
                        st.error("All fields are required!")
    
    # Print Letter Tab
    with tab3:
        st.header("Select Bank Account and Print Letter")
        accounts = get_accounts()
        account_options = [(f"{acc[1]} - {acc[2]} ({acc[3]})", acc[0]) for acc in accounts] if accounts else [("No accounts available", 0)]
        selected_account_id = st.selectbox("Select Account", options=account_options, format_func=lambda x: x[0], key="print_select")
        
        letter_date = st.date_input("Letter Date", value=datetime.now())
        request_type = st.selectbox("Request Type", ["Cheque Book", "Bank Statement", "Both"])
        
        if request_type in ["Bank Statement", "Both"]:
            from_date = st.date_input("From Date", value=datetime.now())
            to_date = st.date_input("To Date", value=datetime.now())
        else:
            from_date = None
            to_date = None
        
        signature_name = st.text_input("Signature Name", placeholder="e.g., John Doe")
        
        if st.button("Print Letter"):
            if selected_account_id[1] == 0:
                st.error("Please select an account first!")
            elif not letter_date:
                st.error("Please select a letter date!")
            elif request_type in ["Bank Statement", "Both"] and (not from_date or not to_date):
                st.error("Please select From and To dates!")
            elif not signature_name:
                st.error("Please enter a signature name!")
            else:
                pdf_file = generate_letter(
                    selected_account_id[1], 
                    letter_date.strftime('%Y-%m-%d'), 
                    request_type, 
                    from_date.strftime('%Y-%m-%d') if from_date else None, 
                    to_date.strftime('%Y-%m-%d') if to_date else None, 
                    signature_name
                )
                if pdf_file:
                    with open(pdf_file, "rb") as f:
                        st.download_button("Download PDF", f, file_name="bank_letter.pdf")
                    st.success("PDF generated successfully!")

if __name__ == "__main__":
    main() 