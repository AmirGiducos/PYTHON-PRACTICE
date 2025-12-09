"""
Digital Wallet Mobile App - Pure Python
Built with Flet for cross-platform mobile deployment (iOS, Android, Web)

Installation:
pip install flet

Run:
python wallet_app.py

Deploy to mobile:
flet build apk  # For Android
flet build ipa  # For iOS
"""

import flet as ft
from datetime import datetime
from decimal import Decimal
import json
import hashlib
import uuid

# ==================== DATA STORAGE ====================
class WalletDatabase:
    """Simple in-memory database (use SQLite or Firebase in production)"""
    
    def __init__(self):
        self.users = {
            'alice@example.com': {
                'id': '1',
                'email': 'alice@example.com',
                'password_hash': self._hash_password('password123'),
                'full_name': 'Alice Smith',
                'balance': Decimal('1000.00')
            },
            'bob@example.com': {
                'id': '2',
                'email': 'bob@example.com',
                'password_hash': self._hash_password('password123'),
                'full_name': 'Bob Johnson',
                'balance': Decimal('500.00')
            }
        }
        self.transactions = []
        
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, email, password, full_name):
        if email in self.users:
            return None, "Email already registered"
        
        user = {
            'id': str(uuid.uuid4()),
            'email': email,
            'password_hash': self._hash_password(password),
            'full_name': full_name,
            'balance': Decimal('0.00')
        }
        self.users[email] = user
        return user, None
    
    def login_user(self, email, password):
        user = self.users.get(email)
        if not user or user['password_hash'] != self._hash_password(password):
            return None, "Invalid email or password"
        return user, None
    
    def get_balance(self, user_id):
        for user in self.users.values():
            if user['id'] == user_id:
                return user['balance']
        return Decimal('0.00')
    
    def add_money(self, user_id, amount):
        for user in self.users.values():
            if user['id'] == user_id:
                user['balance'] += Decimal(str(amount))
                transaction = {
                    'id': str(uuid.uuid4()),
                    'user_id': user_id,
                    'type': 'credit',
                    'amount': float(amount),
                    'description': 'Added money to wallet',
                    'timestamp': datetime.now().isoformat(),
                    'balance_after': float(user['balance'])
                }
                self.transactions.append(transaction)
                return user['balance'], transaction, None
        return None, None, "User not found"
    
    def send_money(self, sender_id, recipient_email, amount, description):
        sender = None
        recipient = None
        
        for user in self.users.values():
            if user['id'] == sender_id:
                sender = user
            if user['email'] == recipient_email:
                recipient = user
        
        if not sender:
            return None, None, "Sender not found"
        if not recipient:
            return None, None, "Recipient not found"
        if sender['email'] == recipient_email:
            return None, None, "Cannot send money to yourself"
        if sender['balance'] < Decimal(str(amount)):
            return None, None, "Insufficient balance"
        
        # Process transfer
        sender['balance'] -= Decimal(str(amount))
        recipient['balance'] += Decimal(str(amount))
        
        # Create transactions
        sender_tx = {
            'id': str(uuid.uuid4()),
            'user_id': sender_id,
            'type': 'transfer_out',
            'amount': float(amount),
            'description': description or f'Sent to {recipient_email}',
            'recipient_email': recipient_email,
            'timestamp': datetime.now().isoformat(),
            'balance_after': float(sender['balance'])
        }
        
        recipient_tx = {
            'id': str(uuid.uuid4()),
            'user_id': recipient['id'],
            'type': 'transfer_in',
            'amount': float(amount),
            'description': f'Received from {sender["email"]}',
            'sender_email': sender['email'],
            'timestamp': datetime.now().isoformat(),
            'balance_after': float(recipient['balance'])
        }
        
        self.transactions.extend([sender_tx, recipient_tx])
        return sender['balance'], sender_tx, None
    
    def get_transactions(self, user_id, limit=10):
        user_txs = [tx for tx in self.transactions if tx['user_id'] == user_id]
        user_txs.sort(key=lambda x: x['timestamp'], reverse=True)
        return user_txs[:limit]

# Initialize database
db = WalletDatabase()

# ==================== MAIN APP ====================
def main(page: ft.Page):
    page.title = "Digital Wallet"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = "#f0f4f8"
    
    # Current user state
    current_user = {'data': None}
    
    # ==================== AUTH SCREEN ====================
    def show_auth_screen():
        # Tab state
        is_login = {'value': True}
        
        # Input fields
        login_email = ft.TextField(
            label="Email",
            hint_text="your@email.com",
            keyboard_type=ft.KeyboardType.EMAIL,
            autofocus=True
        )
        login_password = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True
        )
        
        register_name = ft.TextField(label="Full Name", hint_text="John Doe")
        register_email = ft.TextField(
            label="Email",
            hint_text="your@email.com",
            keyboard_type=ft.KeyboardType.EMAIL
        )
        register_password = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True
        )
        
        error_text = ft.Text(color=ft.colors.RED, visible=False)
        
        def handle_login(e):
            if not login_email.value or not login_password.value:
                error_text.value = "Please fill in all fields"
                error_text.visible = True
                page.update()
                return
            
            user, error = db.login_user(login_email.value, login_password.value)
            if error:
                error_text.value = error
                error_text.visible = True
                page.update()
                return
            
            current_user['data'] = user
            show_wallet_screen()
        
        def handle_register(e):
            if not register_name.value or not register_email.value or not register_password.value:
                error_text.value = "Please fill in all fields"
                error_text.visible = True
                page.update()
                return
            
            if len(register_password.value) < 6:
                error_text.value = "Password must be at least 6 characters"
                error_text.visible = True
                page.update()
                return
            
            user, error = db.register_user(
                register_email.value,
                register_password.value,
                register_name.value
            )
            if error:
                error_text.value = error
                error_text.visible = True
                page.update()
                return
            
            current_user['data'] = user
            show_wallet_screen()
        
        login_form = ft.Column([
            login_email,
            login_password,
            ft.ElevatedButton(
                "Login",
                width=300,
                on_click=handle_login,
                style=ft.ButtonStyle(
                    bgcolor=ft.colors.INDIGO,
                    color=ft.colors.WHITE,
                    padding=15
                )
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("Demo Accounts:", weight=ft.FontWeight.BOLD, size=12),
                    ft.Text("alice@example.com / password123", size=11),
                    ft.Text("bob@example.com / password123", size=11),
                ]),
                bgcolor=ft.colors.BLUE_50,
                padding=10,
                border_radius=8,
                width=300
            )
        ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        register_form = ft.Column([
            register_name,
            register_email,
            register_password,
            ft.ElevatedButton(
                "Create Account",
                width=300,
                on_click=handle_register,
                style=ft.ButtonStyle(
                    bgcolor=ft.colors.INDIGO,
                    color=ft.colors.WHITE,
                    padding=15
                )
            )
        ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER, visible=False)
        
        def switch_tab(e):
            if e.control.text == "Login":
                is_login['value'] = True
                login_form.visible = True
                register_form.visible = False
                login_tab.bgcolor = ft.colors.WHITE
                register_tab.bgcolor = None
            else:
                is_login['value'] = False
                login_form.visible = False
                register_form.visible = True
                login_tab.bgcolor = None
                register_tab.bgcolor = ft.colors.WHITE
            error_text.visible = False
            page.update()
        
        login_tab = ft.TextButton("Login", on_click=switch_tab, style=ft.ButtonStyle(bgcolor=ft.colors.WHITE))
        register_tab = ft.TextButton("Register", on_click=switch_tab)
        
        auth_screen = ft.Container(
            content=ft.Column([
                ft.Container(height=50),
                ft.Icon(ft.icons.ACCOUNT_BALANCE_WALLET, size=80, color=ft.colors.INDIGO),
                ft.Text("Digital Wallet", size=32, weight=ft.FontWeight.BOLD),
                ft.Text("Secure & Simple Payments", size=14, color=ft.colors.GREY_700),
                ft.Container(height=30),
                ft.Row([login_tab, register_tab], alignment=ft.MainAxisAlignment.CENTER),
                error_text,
                login_form,
                register_form
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.colors.WHITE,
            padding=30,
            border_radius=20,
            margin=20,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.GREY_300)
        )
        
        page.controls.clear()
        page.add(auth_screen)
        page.update()
    
    # ==================== WALLET SCREEN ====================
    def show_wallet_screen():
        balance_text = ft.Text(
            f"${float(current_user['data']['balance']):.2f}",
            size=48,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.WHITE
        )
        
        transactions_list = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        
        def update_balance():
            balance = db.get_balance(current_user['data']['id'])
            balance_text.value = f"${float(balance):.2f}"
            current_user['data']['balance'] = balance
            page.update()
        
        def update_transactions():
            txs = db.get_transactions(current_user['data']['id'])
            transactions_list.controls.clear()
            
            if not txs:
                transactions_list.controls.append(
                    ft.Text("No transactions yet", color=ft.colors.GREY_500)
                )
            else:
                for tx in txs:
                    is_credit = tx['type'] in ['credit', 'transfer_in']
                    icon_color = ft.colors.GREEN if is_credit else ft.colors.RED
                    amount_color = ft.colors.GREEN_700 if is_credit else ft.colors.RED_700
                    
                    transactions_list.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(
                                    ft.icons.ARROW_DOWNWARD if is_credit else ft.icons.ARROW_UPWARD,
                                    color=icon_color,
                                    size=24
                                ),
                                ft.Column([
                                    ft.Text(tx['description'], weight=ft.FontWeight.BOLD, size=14),
                                    ft.Text(
                                        datetime.fromisoformat(tx['timestamp']).strftime('%b %d, %I:%M %p'),
                                        size=11,
                                        color=ft.colors.GREY_600
                                    )
                                ], spacing=2, expand=True),
                                ft.Text(
                                    f"{'+' if is_credit else '-'}${tx['amount']:.2f}",
                                    weight=ft.FontWeight.BOLD,
                                    color=amount_color
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            bgcolor=ft.colors.GREY_50,
                            padding=15,
                            border_radius=10
                        )
                    )
            page.update()
        
        def handle_logout(e):
            current_user['data'] = None
            show_auth_screen()
        
        def show_add_money_dialog(e):
            amount_field = ft.TextField(
                label="Amount",
                hint_text="0.00",
                keyboard_type=ft.KeyboardType.NUMBER,
                prefix_text="$"
            )
            
            def add_money(e):
                if not amount_field.value:
                    return
                
                try:
                    amount = float(amount_field.value)
                    if amount <= 0:
                        raise ValueError("Amount must be positive")
                    
                    balance, tx, error = db.add_money(current_user['data']['id'], amount)
                    if error:
                        page.snack_bar = ft.SnackBar(ft.Text(error), bgcolor=ft.colors.RED)
                        page.snack_bar.open = True
                    else:
                        update_balance()
                        update_transactions()
                        page.snack_bar = ft.SnackBar(
                            ft.Text(f"Added ${amount:.2f} successfully!"),
                            bgcolor=ft.colors.GREEN
                        )
                        page.snack_bar.open = True
                    
                    dialog.open = False
                    page.update()
                except ValueError as e:
                    page.snack_bar = ft.SnackBar(ft.Text(str(e)), bgcolor=ft.colors.RED)
                    page.snack_bar.open = True
                    page.update()
            
            dialog = ft.AlertDialog(
                title=ft.Text("Add Money"),
                content=amount_field,
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: close_dialog(dialog)),
                    ft.ElevatedButton("Add Money", on_click=add_money)
                ]
            )
            
            page.dialog = dialog
            dialog.open = True
            page.update()
        
        def show_send_money_dialog(e):
            recipient_field = ft.TextField(
                label="Recipient Email",
                hint_text="recipient@email.com",
                keyboard_type=ft.KeyboardType.EMAIL
            )
            amount_field = ft.TextField(
                label="Amount",
                hint_text="0.00",
                keyboard_type=ft.KeyboardType.NUMBER,
                prefix_text="$"
            )
            description_field = ft.TextField(
                label="Description (Optional)",
                hint_text="What's this for?"
            )
            
            def send_money(e):
                if not recipient_field.value or not amount_field.value:
                    return
                
                try:
                    amount = float(amount_field.value)
                    if amount <= 0:
                        raise ValueError("Amount must be positive")
                    
                    balance, tx, error = db.send_money(
                        current_user['data']['id'],
                        recipient_field.value,
                        amount,
                        description_field.value or "Money transfer"
                    )
                    
                    if error:
                        page.snack_bar = ft.SnackBar(ft.Text(error), bgcolor=ft.colors.RED)
                        page.snack_bar.open = True
                    else:
                        update_balance()
                        update_transactions()
                        page.snack_bar = ft.SnackBar(
                            ft.Text(f"Sent ${amount:.2f} successfully!"),
                            bgcolor=ft.colors.GREEN
                        )
                        page.snack_bar.open = True
                    
                    dialog.open = False
                    page.update()
                except ValueError as e:
                    page.snack_bar = ft.SnackBar(ft.Text(str(e)), bgcolor=ft.colors.RED)
                    page.snack_bar.open = True
                    page.update()
            
            dialog = ft.AlertDialog(
                title=ft.Text("Send Money"),
                content=ft.Column([
                    recipient_field,
                    amount_field,
                    description_field
                ], tight=True, spacing=10),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: close_dialog(dialog)),
                    ft.ElevatedButton("Send Money", on_click=send_money)
                ]
            )
            
            page.dialog = dialog
            dialog.open = True
            page.update()
        
        def close_dialog(dialog):
            dialog.open = False
            page.update()
        
        # Build wallet screen
        wallet_screen = ft.Column([
            # Header with balance
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Column([
                            ft.Text("Welcome back,", size=12, color=ft.colors.GREY_600),
                            ft.Text(
                                current_user['data']['full_name'],
                                size=20,
                                weight=ft.FontWeight.BOLD
                            )
                        ], expand=True),
                        ft.IconButton(
                            icon=ft.icons.LOGOUT,
                            on_click=handle_logout,
                            icon_color=ft.colors.RED_400
                        )
                    ]),
                    ft.Container(height=20),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Current Balance", size=14, color=ft.colors.WHITE70),
                            balance_text
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=ft.colors.INDIGO,
                        padding=30,
                        border_radius=15,
                        gradient=ft.LinearGradient([ft.colors.INDIGO, ft.colors.PURPLE])
                    )
                ]),
                bgcolor=ft.colors.WHITE,
                padding=20,
                border_radius=20,
                margin=ft.margin.only(left=20, right=20, top=20),
                shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.GREY_300)
            ),
            
            # Action buttons
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.ADD_CIRCLE, color=ft.colors.GREEN, size=40),
                        ft.Text("Add Money", weight=ft.FontWeight.BOLD)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    bgcolor=ft.colors.WHITE,
                    padding=20,
                    border_radius=15,
                    expand=True,
                    on_click=show_add_money_dialog,
                    shadow=ft.BoxShadow(blur_radius=5, color=ft.colors.GREY_300)
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.SEND, color=ft.colors.BLUE, size=40),
                        ft.Text("Send Money", weight=ft.FontWeight.BOLD)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    bgcolor=ft.colors.WHITE,
                    padding=20,
                    border_radius=15,
                    expand=True,
                    on_click=show_send_money_dialog,
                    shadow=ft.BoxShadow(blur_radius=5, color=ft.colors.GREY_300)
                )
            ], spacing=15, alignment=ft.MainAxisAlignment.CENTER),
            
            # Transactions
            ft.Container(
                content=ft.Column([
                    ft.Text("Recent Transactions", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(height=10),
                    transactions_list
                ]),
                bgcolor=ft.colors.WHITE,
                padding=20,
                border_radius=20,
                margin=ft.margin.only(left=20, right=20, bottom=20),
                shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.GREY_300),
                expand=True
            )
        ], spacing=15, scroll=ft.ScrollMode.AUTO, expand=True)
        
        page.controls.clear()
        page.add(wallet_screen)
        update_transactions()
        page.update()
    
    # Start with auth screen
    show_auth_screen()

# Run the app
if __name__ == "__main__":
    ft.app(target=main)