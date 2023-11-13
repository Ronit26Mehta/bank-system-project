import mysql.connector


db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ronit",
    database="bank"
)


cursor = db.cursor()


create_table_sql = '''
    CREATE TABLE IF NOT EXISTS account (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        account_number INT NOT NULL,
        initial_balance INT,
        rate_of_interest INT,
        contact_number VARCHAR(255),
        address_field VARCHAR(255)
    )
'''
cursor.execute(create_table_sql)


create_transaction_table_sql = '''
    CREATE TABLE IF NOT EXISTS transaction_history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        account_id INT,
        transaction_type VARCHAR(255) NOT NULL,
        amount INT NOT NULL,
        transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (account_id) REFERENCES accounts(id)
    )
'''
cursor.execute(create_transaction_table_sql)

def create_account(n):
    for i in range(n):
        username = input("Enter the name of the user: ")
        password = input("Enter the password: ")  
        balance = int(input("Enter the balance of the user: "))
        account = int(input("Enter the account number of the user: "))
        rate_of_interest = int(input("Enter the rate of interest: "))
        contact_number = input("Enter the contact number: ")
        address_field = input("Enter address field: ")

        insert_sql = '''
            INSERT INTO account(username, password, account_number, initial_balance, rate_of_interest, contact_number, address_field)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        '''
        values = (username, password, account, balance, rate_of_interest, contact_number, address_field)
        try:

            cursor.execute(insert_sql, values)
          
            db.commit()
            print("Details inserted.")
        except Exception as e:
            print("Error:", e)
        
            db.rollback()

def delete_account():
    username = input("Enter the username to delete: ")


    delete_sql = '''
        DELETE FROM account
        WHERE username = %s
    '''
    values = (username,)
    try:
        cursor.execute(delete_sql, values)
        db.commit()
        print("Account deleted successfully.")
    except Exception as e:
        print("Error:", e)
        db.rollback()

def generate_receipt():
    username = input("Enter your username: ")


    select_sql = '''
        SELECT *
        FROM account
        WHERE username = %s
    '''
    values = (username,)
    try:
        cursor.execute(select_sql, values)
        result = cursor.fetchone()
        if result:

            user_id, username, password, account_number, initial_balance, rate_of_interest, contact_number, address_field = result


            receipt = f'''
                Receipt for User: {username}
                Account Number: {account_number}
                Initial Balance: {initial_balance}
                Rate of Interest: {rate_of_interest}%
                Contact Number: {contact_number}
                Address: {address_field}
            '''


            with open(f"{username}_receipt.txt", 'w') as file:
                file.write(receipt)

            print("Receipt generated successfully.")
        else:
            print("User not found.")
    except Exception as e:
        print("Error:", e)

def retrieve_password(username):

    select_password_sql = '''
        SELECT password
        FROM account
        WHERE username = %s
    '''
    values = (username,)
    try:
        cursor.execute(select_password_sql, values)
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
    except Exception as e:
        print("Error:", e)
        return None

def authenticate():
    username = input("Enter your username: ")
    entered_password = input("Enter your password: ")

    
    correct_password = retrieve_password(username)


    return correct_password is not None and entered_password == correct_password

def deposit():
    if authenticate():
        username = input("Enter your username: ")
        amount = int(input("Enter the amount to deposit: "))

     
        update_sql = '''
            UPDATE account
            SET initial_balance = initial_balance + %s
            WHERE username = %s
        '''
        values = (amount, username)
        try:
            cursor.execute(update_sql, values)

   
            transaction_sql = '''
                INSERT INTO transaction_history(account_id, transaction_type, amount)
                SELECT id, 'Deposit', %s FROM account WHERE username = %s
            '''
            transaction_values = (amount, username)
            cursor.execute(transaction_sql, transaction_values)

            db.commit()
            print("Deposit successful.")
        except Exception as e:
            print("Error:", e)
            db.rollback()
    else:
        print("Authentication failed.")

def withdraw():
    if authenticate():
        username = input("Enter your username: ")
        amount = int(input("Enter the amount to withdraw: "))

 
        update_sql = '''
            UPDATE account
            SET initial_balance = initial_balance - %s
            WHERE username = %s
        '''
        values = (amount, username)
        try:
            cursor.execute(update_sql, values)

 
            transaction_sql = '''
                INSERT INTO transaction_history(account_id, transaction_type, amount)
                SELECT id, 'Withdrawal', %s FROM account WHERE username = %s
            '''
            transaction_values = (amount, username)
            cursor.execute(transaction_sql, transaction_values)

            db.commit()
            print("Withdrawal successful.")
        except Exception as e:
            print("Error:", e)
            db.rollback()
    else:
        print("Authentication failed.")

def compute_interest():
    if authenticate():
        username = input("Enter your username: ")
        

        select_sql = '''
            SELECT initial_balance, rate_of_interest
            FROM account
            WHERE username = %s
        '''
        values = (username,)
        try:
            cursor.execute(select_sql, values)
            result = cursor.fetchone()
            if result:
                initial_balance, rate_of_interest = result
                interest = (initial_balance * rate_of_interest) / 100
                print("Interest: ", interest)
            else:
                print("User not found.")
        except Exception as e:
            print("Error:", e)
    else:
        print("Authentication failed.")

def dispbalance():
    if authenticate():
        username = input("Enter your username: ")


        select_sql = '''
            SELECT initial_balance
            FROM account
            WHERE username = %s
        '''
        values = (username,)
        try:
            cursor.execute(select_sql, values)
            result = cursor.fetchone()
            if result:
                balance = result[0]
                print("Balance: ", balance)
            else:
                print("User not found.")
        except Exception as e:
            print("Error:", e)
    else:
        print("Authentication failed.")

def display_transaction_history():
    if authenticate():
        username = input("Enter your username: ")


        select_transaction_sql = '''
            SELECT t.transaction_date, t.transaction_type, t.amount
            FROM transaction_history t
            JOIN account a ON t.account_id = a.id
            WHERE a.username = %s
        '''
        values = (username,)
        try:
            cursor.execute(select_transaction_sql, values)
            result = cursor.fetchall()
            if result:
                print("Transaction History:")
                for row in result:
                    print(f"Date: {row[0]}, Type: {row[1]}, Amount: {row[2]}")
            else:
                print("No transactions found.")
        except Exception as e:
            print("Error:", e)
    else:
        print("Authentication failed.")

def main():
    while True:
        print("\n1. Create Account\n2. Delete Account\n3. Deposit\n4. Withdraw\n5. Compute Interest\n6. Display Balance\n7. Generate Receipt\n8. Transaction History\n9. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            num = int(input("Enter the number of accounts to create: "))
            create_account(num)
        elif choice == '2':
            delete_account()
        elif choice == '3':
            deposit()
        elif choice == '4':
            withdraw()
        elif choice == '5':
            compute_interest()
        elif choice == '6':
            dispbalance()
        elif choice == '7':
            generate_receipt()
        elif choice == '8':
            display_transaction_history()
        elif choice == '9':
            break
        else:
            print("Enter a valid choice.")

if __name__ == "__main__":
    main()

db.close()
