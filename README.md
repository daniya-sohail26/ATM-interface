# ATM-interface
This application simulates a basic ATM interface using PyQt5, providing users a graphical interface to perform common banking operations.

Key Features:

User Registration: New users can register by providing a username and PIN. Each new user starts with a default balance.
User Login: Registered users can log in using their username and PIN to access their account.
Transactions: After login, users can perform multiple operations:
  1. View Transaction History: Display a list of past transactions.
  2. Withdraw: Deduct an amount from the user's balance.
  3. Deposit: Add an amount to the user's balance.
  4. Transfer: Transfer an amount to another user.
  5. Check Balance: View the current balance.
Logout: Log out of the current user session.
The application uses a local JSON file (user_data.json) to store user data, such as usernames, PINs, balances, and transaction histories.
