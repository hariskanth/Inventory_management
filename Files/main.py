"""
main.py
------------------------------------------------------------
Application entry point. Combines the UI-building mixins
(ui.py) with the event-handling mixins (app.py) into the
final LoginWindow and MainWindow classes, and launches the
QApplication.
"""

import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow

from database import db
from ui import APP_STYLE, LoginUI, MainWindowUI
from app import LoginApp, MainWindowApp


# ============================================================
# LOGIN WINDOW
# ============================================================

class LoginWindow(LoginUI, LoginApp, QWidget):

    def __init__(self):
        super().__init__()
        self.main_window = None
        self.setWindowTitle("StockPro - Inventory Management")
        self.setFixedSize(440, 560)
        self.setObjectName("loginWindow")

        self.setStyleSheet("""
            QWidget#loginWindow {
                background: #f1f5f9;
            }
            QLabel, QFrame {
                background: transparent;
                font-family: "Segoe UI";
            }
            QFrame#loginCard {
                background: white;
                border: none;
                border-radius: 18px;
            }
            QLabel#brand {
                font-size: 30px;
                font-weight: bold;
                color: #2563eb;
            }
            QLabel#subtitle {
                color: #64748b;
                font-size: 13px;
            }
            QLabel#field {
                font-weight: bold;
                color: #334155;
            }
            QLineEdit {
                background: #f8fafc;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #2563eb;
                background: white;
            }
            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 13px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #1d4ed8;
            }
        """)

        self.build_ui()


# ============================================================
# MAIN WINDOW
# ============================================================

class MainWindow(MainWindowUI, MainWindowApp, QMainWindow):

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.current_page = None
        self.pages = {}
        self.setWindowTitle("StockPro - Inventory Management System")
        self.resize(1400, 850)
        self.setMinimumSize(1150, 700)
        self.setStyleSheet(APP_STYLE)
        self.build_ui()
        self.show_dashboard()
        self.showMaximized()


# ============================================================
# APPLICATION START
# ============================================================

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("StockPro Inventory Management")
    app.setFont(QFont("Segoe UI", 10))

    login = LoginWindow()
    login.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
