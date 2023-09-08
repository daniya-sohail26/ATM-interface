import sys  #provides functions and variables to interact with the Python runtime environment
import json #provides methods to work with JSON data
# importing libraries necessary for interface
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                             QLineEdit, QVBoxLayout, QFormLayout, QDialog, QTextEdit, 
                             QComboBox, QWidget, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor

DATA_FILE = 'user_data.json' # path to the file where the user data is stored

# Load existing user data or initialize to default
try:
    with open(DATA_FILE, 'r') as file: #procedure for loading registered users data
        data = json.load(file)
        users = data['users']
        pins = data['pins']
        amounts = data['amounts']
        transaction_history = data['transaction_history']
except (FileNotFoundError, json.JSONDecodeError):
    users = []
    pins = []
    amounts = []
    transaction_history = {}

DEFAULT_AMOUNT = 5000 #constant that represents the initial deposit amount when a new user registers
current_user = None #a global variable that will store the currently logged-in user's username

class TransactionHistoryDialog(QDialog): #displays transaction history of the current user

    def __init__(self, transactions, parent=None):
        super(TransactionHistoryDialog, self).__init__(parent) #QDialog derived class that displays a user's transaction history
        self.setWindowTitle("Transactions History")
        self.setGeometry(400, 250, 700, 400)#setting dimensions of the window
        
        layout = QVBoxLayout()
        self.transactionDisplay = QTextEdit(self) #widget used to display transactions in read-only mode
        self.transactionDisplay.setFont(QFont('Eras Light ITC', 14)) #style properties of the transaction history to be displayed
        self.transactionDisplay.setReadOnly(True)
        self.transactionDisplay.setText(transactions or "No transactions available.") #sets the text of the transactionDisplay widget
        layout.addWidget(self.transactionDisplay)

        closeButton = QPushButton("Close", self)#CLOSE button initialied to close the dialog 
        closeButton.clicked.connect(self.close)
        layout.addWidget(closeButton, alignment=Qt.AlignCenter)

        self.setLayout(layout)#button added to main layout

def save_data(): # saves user data to defined to defined DATA_FILE
    with open(DATA_FILE, 'w') as file: #opens the DATA_FILE in write mode and writes user data (users, pins, amounts, and transaction histories)
                                       #in JSON format.
        json.dump({
            'users': users,
            'pins': pins,
            'amounts': amounts,
            'transaction_history': transaction_history
        }, file)

# Create a main window class for ATM operations
class TransactionWindow(QMainWindow):

    # Constructor for the main window
    def __init__(self):
        super().__init__()
        self.initTransactionUI()  # Call the UI initialization method

    # Method to initialize the UI components
    def initTransactionUI(self):
        # Setting the window's title and geometry
        self.setWindowTitle("ATM Dashboard")
        self.setGeometry(350, 200, 800, 500)

        # Setting a color palette for the UI
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(45, 45, 45))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(50, 50, 50))
        palette.setColor(QPalette.Button, QColor(85, 85, 85))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        self.setPalette(palette)

        # Creating a central widget for the window
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        layout = QVBoxLayout()  # Main vertical layout for the central widget
        self.centralWidget.setLayout(layout)

        # Welcome label displaying the current user's name
        self.label = QLabel(f"Welcome, {current_user}", self)
        self.label.setFont(QFont('Eras Light ITC', 24, QFont.Bold))
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        # Layout for the operation options/buttons
        self.optionsLayout = QVBoxLayout()
        options = ["Transactions History", "Withdraw", "Deposit", "Transfer", "Check Balance", "Logout"]
        for option in options:
            btn = QPushButton(option, self)
            btn.setFont(QFont('Eras Light ITC', 20))
            btn.setStyleSheet("""
                QPushButton {
                    border-radius: 30px;
                    background-color: #3A9BF4;
                    color: white;
                    padding: 15px 0;
                    margin: 10px;
                }
                QPushButton:hover {
                    background-color: #6FB6F4;
                }
            """)
            btn.clicked.connect(self.createHandleTransaction(option))  # Connect button to respective handlers
            self.optionsLayout.addWidget(btn)
        layout.addLayout(self.optionsLayout)  # Add the options layout to the main layout

    # Method to handle ATM operations
    def createHandleTransaction(self, choice):
        def handle():
            idx = users.index(current_user)  # Find the index of the current user

            # Handle based on the choice
            if choice == "Transactions History":
                transactions = '\n'.join(transaction_history.get(current_user, []))
                self.historyDialog = TransactionHistoryDialog(transactions, self)
                self.historyDialog.show()
            elif choice == "Withdraw":
                amount, _ = QInputDialog.getInt(self, "Withdraw", "Enter amount to withdraw:")
                if amount <= amounts[idx]:
                    amounts[idx] -= amount
                    transaction_history[current_user].append(f"Withdrawn: {amount}")
                    save_data()
                    self.label.setText(f"Withdrawn: {amount}")
                else:
                    self.label.setText("Insufficient funds!")
            elif choice == "Deposit":
                amount, _ = QInputDialog.getInt(self, "Deposit", "Enter amount to deposit:")
                amounts[idx] += amount
                transaction_history[current_user].append(f"Deposited: {amount}")
                save_data()
                self.label.setText(f"Deposited: {amount}")
            elif choice == "Transfer":
                recipient, ok = QInputDialog.getItem(self, "Transfer", "Select user to transfer to:", users, editable=False)
                if ok and recipient != current_user:
                    amount, ok = QInputDialog.getInt(self, "Transfer", "Enter amount to transfer:")
                    if ok and amount <= amounts[idx]:
                        amounts[idx] -= amount
                        amounts[users.index(recipient)] += amount
                        transaction_history[current_user].append(f"Transferred {amount} to {recipient}")
                        transaction_history[recipient].append(f"Received {amount} from {current_user}")
                        save_data()
                        self.label.setText(f"Transferred {amount} to {recipient}")
                    else:
                        self.label.setText("Insufficient funds!")
                else:
                    self.label.setText("Invalid recipient!")
            elif choice == "Check Balance":
                self.label.setText(f"Your balance: {amounts[idx]}")
            elif choice == "Logout":
                self.close()
        return handle


class ATM_GUI(QMainWindow):

    def __init__(self):
        super().__init__()  # Initialize the superclass (QMainWindow)
        self.initUI()       #

    def initUI(self):
        # Set window size and title
        self.setGeometry(300, 150, 800, 500)
        self.setWindowTitle('ATM Interface')

        # Define a color palette for the application
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(45, 45, 45))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(50, 50, 50))
        palette.setColor(QPalette.Button, QColor(85, 85, 85))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        self.setPalette(palette)  # Set the defined palette to the application

        # Define a central widget for the main window
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        # Define a vertical layout for the central widget
        self.layout = QVBoxLayout()
        self.centralWidget.setLayout(self.layout)

        # Create and set a title label for the ATM interface
        self.label = QLabel("ATM Interface", self)
        self.label.setFont(QFont('Eras Light ITC', 28, QFont.Bold))
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        # Define a form layout for user input (login/registration)
        self.loginLayout = QFormLayout()
        self.layout.addLayout(self.loginLayout)

        # Create a line edit for user input (username)
        self.userInput = QLineEdit(self)
        self.userInput.setFont(QFont('Eras Light ITC', 14))
        self.userInput.setPlaceholderText("Enter User Name")
        self.loginLayout.addRow("Username:", self.userInput)

        # Create a line edit for PIN input (password)
        self.pinInput = QLineEdit(self)
        self.pinInput.setFont(QFont('Eras Light ITC', 14))
        self.pinInput.setEchoMode(QLineEdit.Password)  # Set to password mode
        self.pinInput.setPlaceholderText("Enter PIN")
        self.loginLayout.addRow("PIN:", self.pinInput)

        # Create a register button
        self.registerButton = QPushButton("Register", self)
        self.registerButton.setFont(QFont('Eras Light ITC', 16))
        self.registerButton.setFixedSize(250, 60)
        self.registerButton.setStyleSheet("""
            QPushButton {
                border-radius: 30px;
                background-color: #2A8BF2;
                color: white;
            }
            QPushButton:hover {
                background-color: #60A4F4;
            }
        """)
        # Connect the register button to the registration handler
        self.registerButton.clicked.connect(self.handleRegistration)
        self.layout.addWidget(self.registerButton, alignment=Qt.AlignCenter)

        # Create a login button
        self.loginButton = QPushButton("Login", self)
        self.loginButton.setFont(QFont('Eras Light ITC', 16))
        self.loginButton.setFixedSize(250, 60)
        self.loginButton.setStyleSheet("""
            QPushButton {
                border-radius: 30px;
                background-color: #2A8BF2;
                color: white;
            }
            QPushButton:hover {
                background-color: #60A4F4;
            }
        """)
        # Connect the login button to the login handler
        self.loginButton.clicked.connect(self.handleLogin)
        self.layout.addWidget(self.loginButton, alignment=Qt.AlignCenter)

    # Method to handle registration logic
    def handleRegistration(self):
        user = self.userInput.text().lower()  # Get username and convert to lowercase
        pin = self.pinInput.text()            # Get entered PIN

        # Check if user already exists
        if user not in users:
            users.append(user)                # Add new user
            pins.append(pin)                  # Add associated PIN
            amounts.append(DEFAULT_AMOUNT)    # Set default amount
            transaction_history[user] = []    # Initialize empty transaction history for the user

            # Save the updated data to a file
            with open(DATA_FILE, 'w') as f:
                json.dump({
                    'users': users,
                    'pins': pins,
                    'amounts': amounts,
                    'transaction_history': transaction_history
                }, f)

            self.label.setText(f"Registered {user}. Please login.")
        else:
            # Inform if the username is already taken
            self.label.setText("Username already exists.")

    # Method to handle login logic
    def handleLogin(self):
        global current_user
        user = self.userInput.text().lower()  # Get username and convert to lowercase
        pin = self.pinInput.text()            # Get entered PIN

        # Validate the entered username and PIN
        if user in users and pin == pins[users.index(user)]:
            current_user = user
            self.transWin = TransactionWindow()  # Open the transaction window for the user
            self.transWin.show()
            self.close()  # Close the login window

        else:
            # Inform if the entered username or PIN is invalid
            self.label.setText("Invalid User or PIN.")

# Define the main execution
if __name__ == '__main__':
    app = QApplication(sys.argv)  # Create a PyQt5 application
    mainWin = ATM_GUI()           # Create the main window
    mainWin.show()                # Show the main window
    sys.exit(app.exec_())         # Execute the application
