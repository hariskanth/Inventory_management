import sys
import mysql.connector
from datetime import datetime, timedelta
from functools import partial
import csv
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QTableWidget,
    QTableWidgetItem, QLineEdit, QComboBox, QMessageBox,
    QDialog, QFormLayout, QSpinBox, QDoubleSpinBox, QTextEdit,
    QFrame, QHeaderView, QAbstractItemView, QStackedWidget,
    QGraphicsDropShadowEffect, QSizePolicy, QFileDialog,
    QTabWidget, QGroupBox, QDateEdit, QCheckBox, QProgressBar,
    QSplitter
)

try:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_CONFIG = {
    "host": "localhost",
    "user": "Haris",
    "password": "1234",
    "database": "INVENTORY_DB"
}


# ============================================================
# DATABASE CLASS
# ============================================================

class Database:

    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
        except mysql.connector.Error as e:
            QMessageBox.critical(
                None,
                "Database Error",
                "Unable to connect to MySQL.\n\n" + str(e)
            )

    def execute(self, query, params=None, fetch=False):
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()

            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())

            if fetch:
                result = cursor.fetchall()
                cursor.close()
                return result

            self.connection.commit()
            cursor.close()
            return True

        except mysql.connector.Error as e:
            print("Database Error:", e)
            return None

    def scalar(self, query, params=None):
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()

            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            cursor.close()

            if result:
                return result[0]

            return 0

        except mysql.connector.Error as e:
            print("Database Error:", e)
            return 0


db = Database()


# ============================================================
# GLOBAL STYLE
# ============================================================

APP_STYLE = """
QMainWindow {
    background: #f4f7fb;
}

QWidget {
    font-family: "Segoe UI";
    font-size: 14px;
    color: #1e293b;
}

QFrame#sidebar {
    background: #111827;
    border: none;
}

QLabel#logo {
    color: white;
    font-size: 25px;
    font-weight: bold;
}

QLabel#roleLabel {
    color: #94a3b8;
    font-size: 12px;
}

QPushButton#navButton {
    background: transparent;
    color: #cbd5e1;
    border: none;
    text-align: left;
    padding: 14px 20px;
    border-radius: 8px;
    font-size: 14px;
}

QPushButton#navButton:hover {
    background: #1e293b;
    color: white;
}

QPushButton#navButton:checked {
    background: #2563eb;
    color: white;
    font-weight: bold;
}

QPushButton#logoutButton {
    background: #dc2626;
    color: white;
    border: none;
    padding: 13px;
    border-radius: 8px;
    font-weight: bold;
}

QPushButton#logoutButton:hover {
    background: #b91c1c;
}

QLabel#pageTitle {
    font-size: 27px;
    font-weight: bold;
    color: #0f172a;
}

QLabel#pageSubtitle {
    color: #64748b;
    font-size: 13px;
}

QFrame#card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}

QLabel#cardTitle {
    color: rgba(255,255,255,0.85);
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 1px;
}

QLabel#cardValue {
    color: white;
    font-size: 32px;
    font-weight: bold;
}

QLabel#cardSubValue {
    color: rgba(255,255,255,0.7);
    font-size: 13px;
    font-weight: normal;
}

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QDateEdit {
    background: white;
    border: 1px solid #cbd5e1;
    border-radius: 7px;
    padding: 8px;
    min-height: 20px;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
QDoubleSpinBox:focus, QTextEdit:focus, QDateEdit:focus {
    border: 1px solid #2563eb;
}

QPushButton#primary {
    background: #2563eb;
    color: white;
    border: none;
    padding: 10px 18px;
    border-radius: 7px;
    font-weight: bold;
}

QPushButton#primary:hover {
    background: #1d4ed8;
}

QPushButton#danger {
    background: #dc2626;
    color: white;
    border: none;
    padding: 10px 18px;
    border-radius: 7px;
    font-weight: bold;
}

QPushButton#secondary {
    background: #e2e8f0;
    color: #334155;
    border: none;
    padding: 10px 18px;
    border-radius: 7px;
}

QTableWidget {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    gridline-color: #e2e8f0;
    selection-background-color: #dbeafe;
    selection-color: #1e3a8a;
}

QHeaderView::section {
    background: #f8fafc;
    color: #475569;
    padding: 11px;
    border: none;
    border-bottom: 1px solid #e2e8f0;
    font-weight: bold;
}

QScrollBar:vertical {
    background: #f1f5f9;
    width: 8px;
}

QScrollBar::handle:vertical {
    background: #cbd5e1;
    border-radius: 4px;
}

QTabWidget::pane {
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    background: white;
}

QTabBar::tab {
    background: #f1f5f9;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}

QTabBar::tab:selected {
    background: #2563eb;
    color: white;
}

QGroupBox {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 10px 0 10px;
}

QPushButton#rowEdit {
    background: #eff6ff;
    color: #2563eb;
    border: 1px solid #bfdbfe;
    border-radius: 6px;
    font-size: 12px;
    padding: 0px;
}

QPushButton#rowEdit:hover {
    background: #2563eb;
    color: white;
    border: 1px solid #2563eb;
}

QPushButton#rowDelete {
    background: #fef2f2;
    color: #dc2626;
    border: 1px solid #fecaca;
    border-radius: 6px;
    font-size: 12px;
    padding: 0px;
}

QPushButton#rowDelete:hover {
    background: #dc2626;
    color: white;
    border: 1px solid #dc2626;
}

QLabel#sectionLabel {
    color: #1e293b;
    font-size: 14px;
    font-weight: bold;
}

QLabel#sectionCount {
    color: #64748b;
    font-size: 12px;
    background: #f1f5f9;
    border-radius: 9px;
    padding: 2px 9px;
}

QFrame#toolbarCard {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}

QFrame#vDivider {
    background: #e2e8f0;
    max-width: 1px;
    min-width: 1px;
}
"""

CARD_GRADIENTS = {
    "blue":   ("#3b82f6", "#1d4ed8"),
    "green":  ("#22c55e", "#15803d"),
    "orange": ("#f97316", "#c2410c"),
    "purple": ("#a855f7", "#7e22ce"),
}


# ============================================================
# LOGIN WINDOW
# ============================================================

class LoginWindow(QWidget):

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

    def build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(30, 30, 30, 30)

        card = QFrame()
        card.setObjectName("loginCard")

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 6)
        shadow.setColor(Qt.gray)
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(40, 45, 40, 40)
        layout.setSpacing(14)

        brand = QLabel("STOCKPRO")
        brand.setObjectName("brand")
        brand.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Inventory Management System")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        layout.addWidget(brand)
        layout.addWidget(subtitle)
        layout.addSpacing(25)

        user_label = QLabel("Username")
        user_label.setObjectName("field")
        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter username")

        password_label = QLabel("Password")
        password_label.setObjectName("field")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter password")
        self.password.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("SIGN IN")
        self.login_button.clicked.connect(self.login)
        self.password.returnPressed.connect(self.login)

        layout.addWidget(user_label)
        layout.addWidget(self.username)
        layout.addSpacing(6)
        layout.addWidget(password_label)
        layout.addWidget(self.password)
        layout.addSpacing(20)
        layout.addWidget(self.login_button)
        layout.addStretch()

        outer.addWidget(card)

    def login(self):
        username = self.username.text().strip()
        password = self.password.text()

        if not username or not password:
            QMessageBox.warning(self, "Login", "Please enter username and password.")
            return

        query = """
            SELECT USER_ID, USERNAME, FULL_NAME, ROLE, STATUS
            FROM USERS
            WHERE BINARY USERNAME = %s AND BINARY PASSWORD = %s
            LIMIT 1
        """

        result = db.execute(query, (username, password), fetch=True)

        if not result:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
            return

        user = result[0]

        if user["STATUS"] != "ACTIVE":
            QMessageBox.warning(self, "Account Disabled", "This user account is inactive.")
            return

        self.main_window = MainWindow(user)
        self.main_window.show()
        self.close()


# ============================================================
# MAIN WINDOW
# ============================================================

class MainWindow(QMainWindow):

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

    # --------------------------------------------------------
    # UI
    # --------------------------------------------------------

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # SIDEBAR
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(235)

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(5)

        logo = QLabel("STOCKPRO")
        logo.setObjectName("logo")
        logo.setAlignment(Qt.AlignCenter)

        role = QLabel(self.user["FULL_NAME"] + "\n" + self.user["ROLE"])
        role.setObjectName("roleLabel")
        role.setAlignment(Qt.AlignCenter)

        sidebar_layout.addWidget(logo)
        sidebar_layout.addWidget(role)
        sidebar_layout.addSpacing(25)

        self.dashboard_btn = self.create_nav_button("▣   Dashboard")
        self.products_btn = self.create_nav_button("▤   Products")
        self.stockin_btn = self.create_nav_button("↓   Stock In")
        self.stockout_btn = self.create_nav_button("↑   Stock Out")
        self.transactions_btn = self.create_nav_button("◷   Transactions")
        self.warehouse_btn = self.create_nav_button("🏢   Warehouse")
        self.supplier_btn = self.create_nav_button("📦   Suppliers")

        sidebar_layout.addWidget(self.dashboard_btn)
        sidebar_layout.addWidget(self.products_btn)
        sidebar_layout.addWidget(self.warehouse_btn)
        sidebar_layout.addWidget(self.supplier_btn)

        if self.user["ROLE"] != "STAFF":
            sidebar_layout.addWidget(self.stockin_btn)
            sidebar_layout.addWidget(self.stockout_btn)
            sidebar_layout.addWidget(self.transactions_btn)

        if self.user["ROLE"] == "ADMIN":
            sidebar_layout.addSpacing(20)
            users_label = QLabel("ADMINISTRATION")
            users_label.setStyleSheet("color:#64748b; padding:8px; font-size:11px; font-weight:bold;")
            sidebar_layout.addWidget(users_label)

            self.users_btn = self.create_nav_button("♙   Users")
            sidebar_layout.addWidget(self.users_btn)

        sidebar_layout.addStretch()

        logout = QPushButton("LOGOUT")
        logout.setObjectName("logoutButton")
        logout.clicked.connect(self.logout)
        sidebar_layout.addWidget(logout)

        # CONTENT
        self.content = QWidget()
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(30, 25, 30, 25)

        self.page_title = QLabel()
        self.page_title.setObjectName("pageTitle")

        self.page_subtitle = QLabel()
        self.page_subtitle.setObjectName("pageSubtitle")

        content_layout.addWidget(self.page_title)
        content_layout.addWidget(self.page_subtitle)
        content_layout.addSpacing(20)

        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content)

        # EVENTS
        self.dashboard_btn.clicked.connect(self.show_dashboard)
        self.products_btn.clicked.connect(self.show_products)
        self.warehouse_btn.clicked.connect(self.show_warehouse)
        self.supplier_btn.clicked.connect(self.show_suppliers)

        if self.user["ROLE"] != "STAFF":
            self.stockin_btn.clicked.connect(self.show_stock_in)
            self.stockout_btn.clicked.connect(self.show_stock_out)
            self.transactions_btn.clicked.connect(self.show_transactions)

        if self.user["ROLE"] == "ADMIN":
            self.users_btn.clicked.connect(self.show_users)

    def create_nav_button(self, text):
        button = QPushButton(text)
        button.setObjectName("navButton")
        button.setCheckable(True)
        button.setCursor(Qt.PointingHandCursor)
        return button

    def set_page_header(self, title, subtitle):
        self.page_title.setText(title)
        self.page_subtitle.setText(subtitle)

    def clear_navigation(self):
        for widget in self.sidebar.findChildren(QPushButton):
            if widget.objectName() == "navButton":
                widget.setChecked(False)

    def activate(self, button):
        self.clear_navigation()
        button.setChecked(True)

    def goto_page(self, key, page):
        if key not in self.pages:
            self.stack.addWidget(page)
            self.pages[key] = page
        self.stack.setCurrentWidget(self.pages[key])

    def export_table_to_csv(self, table, title="Export"):
        if table.rowCount() == 0:
            QMessageBox.information(self, "Export", "No data to export.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"Export {title}", "", "CSV Files (*.csv)"
        )
        if not file_path:
            return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                headers = []
                for col in range(table.columnCount()):
                    header_item = table.horizontalHeaderItem(col)
                    headers.append(header_item.text() if header_item else f"Column{col+1}")
                writer.writerow(headers)

                for row in range(table.rowCount()):
                    row_data = []
                    for col in range(table.columnCount()):
                        item = table.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)

            QMessageBox.information(self, "Export", f"Data exported successfully to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    # --------------------------------------------------------
    # CHART HELPERS
    # --------------------------------------------------------

    def make_chart_canvas(self, height=230, width=5):
        if not MATPLOTLIB_AVAILABLE:
            placeholder = QLabel("Install matplotlib to see charts here\n(pip install matplotlib)")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("color:#94a3b8; font-size:12px;")
            placeholder.setFixedHeight(height)
            return placeholder, None, None

        figure = Figure(figsize=(width, height / 90), dpi=90)
        figure.subplots_adjust(left=0.08, right=0.92, top=0.92, bottom=0.08)
        canvas = FigureCanvas(figure)
        canvas.setFixedHeight(height)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        axis = figure.add_subplot(111)
        return canvas, figure, axis

    def make_chart_canvas_with_bottom_legend(self, height=230, width=5):
        if not MATPLOTLIB_AVAILABLE:
            placeholder = QLabel("Install matplotlib to see charts here\n(pip install matplotlib)")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("color:#94a3b8; font-size:12px;")
            placeholder.setFixedHeight(height)
            return placeholder, None, None

        figure = Figure(figsize=(width, height / 90), dpi=90)
        figure.subplots_adjust(left=0.10, right=0.90, top=0.90, bottom=0.15)
        canvas = FigureCanvas(figure)
        canvas.setFixedHeight(height)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        axis = figure.add_subplot(111)
        return canvas, figure, axis

    def draw_donut_chart(self, axis, figure, canvas, values, labels, title, colors=None):
        if axis is None or figure is None:
            return

        values = [float(v) if v is not None else 0.0 for v in values]
        axis.clear()

        if not values or sum(values) == 0:
            axis.text(0.5, 0.5, "No data yet", ha="center", va="center",
                     fontsize=10, color="#94a3b8", transform=axis.transAxes)
            axis.axis("off")
        else:
            if colors is None:
                colors = ['#3b82f6', '#22c55e', '#f97316', '#a855f7', '#ef4444', '#06b6d4']

            total = sum(values)
            percentages = [(v / total) * 100 if total else 0 for v in values]

            wedges = axis.pie(
                values, labels=None, autopct=None,
                startangle=90, colors=colors[:len(values)],
                wedgeprops={'width': 0.5, 'edgecolor': 'white', 'linewidth': 1.5}
            )[0]

            # Legend on the side showing each category's name and percentage
            legend_labels = [f"{label}  —  {pct:.0f}%" for label, pct in zip(labels, percentages)]

            axis.legend(
                wedges, legend_labels,
                loc='center left',
                bbox_to_anchor=(1.02, 0.5),
                fontsize=9,
                frameon=False,
                borderaxespad=0
            )

            if figure is not None:
                try:
                    figure.subplots_adjust(right=0.62)
                except Exception:
                    pass

            axis.set_title(title, fontsize=10, fontweight="bold", color="#334155", pad=8)
            axis.axis('equal')

        canvas.draw()

    def draw_donut_chart_bottom_legend(self, axis, figure, canvas, values, labels, title, colors=None):
        if axis is None or figure is None:
            return

        values = [float(v) if v is not None else 0.0 for v in values]
        axis.clear()

        if not values or sum(values) == 0:
            axis.text(0.5, 0.5, "No data yet", ha="center", va="center",
                     fontsize=10, color="#94a3b8", transform=axis.transAxes)
            axis.axis("off")
        else:
            if colors is None:
                colors = ['#3b82f6', '#22c55e', '#f97316', '#a855f7', '#ef4444', '#06b6d4']

            wedges = axis.pie(
                values, labels=None, autopct=None,
                startangle=90, colors=colors[:len(values)],
                wedgeprops={'width': 0.5, 'edgecolor': 'white', 'linewidth': 1.5}
            )[0]

            centre_circle = plt.Circle((0, 0), 0.35, fc='white')
            axis.add_artist(centre_circle)

            axis.legend(wedges, labels, title=title, loc='center', 
                       bbox_to_anchor=(0.5, -0.05), fontsize=7,
                       title_fontsize=8, frameon=False, ncol=len(labels))

            axis.set_title(title, fontsize=10, fontweight="bold", color="#334155", pad=8)
            axis.axis('equal')

        canvas.draw()

    def draw_bar_chart(self, axis, figure, canvas, categories, values, title, colors=None):
        if axis is None or figure is None:
            return

        values = [float(v) if v is not None else 0.0 for v in values]
        axis.clear()

        if not categories or not values or max(values) == 0:
            axis.text(0.5, 0.5, "No data yet", ha="center", va="center",
                     fontsize=10, color="#94a3b8", transform=axis.transAxes)
            axis.axis("off")
        else:
            if colors is None:
                colors = ['#22c55e', '#ef4444']
            
            bars = axis.bar(categories, values, color=colors[:len(categories)], width=0.5)
            
            for bar, val in zip(bars, values):
                height = bar.get_height()
                axis.text(bar.get_x() + bar.get_width()/2., height,
                         f'{val}', ha='center', va='bottom', fontsize=8)
            
            axis.set_title(title, fontsize=10, fontweight="bold", color="#334155")
            axis.tick_params(axis="x", labelsize=8)
            axis.tick_params(axis="y", labelsize=8)
            axis.spines["top"].set_visible(False)
            axis.spines["right"].set_visible(False)
            axis.spines["left"].set_color("#cbd5e1")
            axis.spines["bottom"].set_color("#cbd5e1")

        canvas.draw()

    # ========================================================
    # HELPER: CHECK CAPACITY
    # ========================================================

    def check_warehouse_capacity(self, warehouse_id, additional_quantity):
        """Check if adding stock to a warehouse would exceed its capacity."""
        result = db.execute(
            """
            SELECT W.CAPACITY, COALESCE(SUM(PWS.STOCK_QTY), 0) AS CURRENT_STOCK
            FROM WAREHOUSE W
            LEFT JOIN PRODUCT_WAREHOUSE_STOCK PWS ON PWS.WAREHOUSE_ID = W.WAREHOUSE_ID
            WHERE W.WAREHOUSE_ID = %s
            GROUP BY W.WAREHOUSE_ID, W.CAPACITY
            """,
            (warehouse_id,),
            fetch=True
        )

        if not result:
            return False, 0, 0, "Warehouse not found."

        capacity = result[0]["CAPACITY"]
        current_stock = result[0]["CURRENT_STOCK"]
        new_total = current_stock + additional_quantity

        if capacity > 0 and new_total > capacity:
            return False, capacity, current_stock, f"Cannot add {additional_quantity} units. Warehouse capacity is {capacity} units (currently {current_stock} units used)."
        
        return True, capacity, current_stock, "OK"

    def check_bin_capacity(self, bin_id, additional_quantity):
        """Check if adding stock to a bin would exceed its capacity."""
        result = db.execute(
            """
            SELECT B.CAPACITY, COALESCE(SUM(PWS.STOCK_QTY), 0) AS CURRENT_STOCK
            FROM BIN_LOCATION B
            LEFT JOIN PRODUCT_WAREHOUSE_STOCK PWS ON PWS.BIN_ID = B.BIN_ID
            WHERE B.BIN_ID = %s
            GROUP BY B.BIN_ID, B.CAPACITY
            """,
            (bin_id,),
            fetch=True
        )

        if not result:
            return False, 0, 0, "Bin not found."

        capacity = result[0]["CAPACITY"]
        current_stock = result[0]["CURRENT_STOCK"]
        new_total = current_stock + additional_quantity

        if capacity > 0 and new_total > capacity:
            return False, capacity, current_stock, f"Cannot add {additional_quantity} units. Bin capacity is {capacity} units (currently {current_stock} units used)."
        
        return True, capacity, current_stock, "OK"

    def get_total_warehouse_capacity(self):
        """Get total capacity of all warehouses."""
        result = db.scalar("SELECT COALESCE(SUM(CAPACITY), 0) FROM WAREHOUSE")
        return result

    def get_total_warehouse_stock(self):
        """Get total stock across all warehouses."""
        result = db.scalar("SELECT COALESCE(SUM(STOCK_QTY), 0) FROM PRODUCT_WAREHOUSE_STOCK")
        return result

    def get_bin_total_capacity(self, warehouse_id):
        """Get total capacity of all bins in a warehouse."""
        result = db.scalar(
            "SELECT COALESCE(SUM(CAPACITY), 0) FROM BIN_LOCATION WHERE WAREHOUSE_ID = %s",
            (warehouse_id,)
        )
        return result

    def get_warehouses_for_category(self, category):
        """Return warehouses that have at least one bin matching the given product category."""
        if not category:
            return []
        rows = db.execute(
            """
            SELECT DISTINCT W.WAREHOUSE_ID, W.WAREHOUSE_NAME, W.LOCATION
            FROM WAREHOUSE W
            JOIN BIN_LOCATION B ON B.WAREHOUSE_ID = W.WAREHOUSE_ID
            WHERE B.DESCRIPTION = %s
            ORDER BY W.WAREHOUSE_NAME
            """,
            (category,),
            fetch=True
        )
        return rows or []

    def get_bins_for_category(self, warehouse_id, category):
        """Return bins in a warehouse that match the given product category."""
        if not warehouse_id or not category:
            return []
        rows = db.execute(
            """
            SELECT BIN_ID, BIN_NAME, CAPACITY
            FROM BIN_LOCATION
            WHERE WAREHOUSE_ID = %s AND DESCRIPTION = %s
            ORDER BY BIN_NAME
            """,
            (warehouse_id, category),
            fetch=True
        )
        return rows or []

    def check_bin_capacity_within_warehouse(self, warehouse_id, bin_capacity, exclude_bin_id=None):
        """Check if bin capacities exceed warehouse capacity."""
        warehouse_capacity = db.scalar(
            "SELECT CAPACITY FROM WAREHOUSE WHERE WAREHOUSE_ID = %s",
            (warehouse_id,)
        )
        
        if warehouse_capacity <= 0:
            return True, "Warehouse has no capacity limit."
            
        current_bin_total = 0
        if exclude_bin_id:
            current_bin_total = db.scalar(
                "SELECT COALESCE(SUM(CAPACITY), 0) FROM BIN_LOCATION WHERE WAREHOUSE_ID = %s AND BIN_ID != %s",
                (warehouse_id, exclude_bin_id)
            )
        else:
            current_bin_total = db.scalar(
                "SELECT COALESCE(SUM(CAPACITY), 0) FROM BIN_LOCATION WHERE WAREHOUSE_ID = %s",
                (warehouse_id,)
            )
        
        new_total = current_bin_total + bin_capacity
        
        if new_total > warehouse_capacity:
            return False, f"Bin capacities would exceed warehouse capacity. Total: {new_total} / {warehouse_capacity} units."
        
        return True, f"OK. Total bin capacity: {new_total} / {warehouse_capacity} units."

    # ========================================================
    # DASHBOARD
    # ========================================================

    def show_dashboard(self):
        self.activate(self.dashboard_btn)
        self.set_page_header("Dashboard", "Inventory overview and business statistics")

        if "dashboard" in self.pages:
            self.refresh_dashboard()
            self.stack.setCurrentWidget(self.pages["dashboard"])
            return

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)

        top_section = QHBoxLayout()
        top_section.setSpacing(15)

        cards_widget = QWidget()
        cards_layout = QGridLayout(cards_widget)
        cards_layout.setSpacing(12)
        cards_layout.setContentsMargins(0, 0, 0, 0)

        card1, self.card_total_products, _ = self.create_card("TOTAL PRODUCTS", "blue")
        card2, self.card_total_stock, self.card_total_stock_sub = self.create_card("TOTAL STOCK", "green", show_sub=True)
        card3, self.card_low_stock, _ = self.create_card("LOW STOCK", "orange")
        card4, self.card_inventory_value, _ = self.create_card("INVENTORY VALUE", "purple")

        for card in [card1, card2, card3, card4]:
            card.setFixedSize(240, 140)

        cards_layout.addWidget(card1, 0, 0)
        cards_layout.addWidget(card2, 0, 1)
        cards_layout.addWidget(card3, 1, 0)
        cards_layout.addWidget(card4, 1, 1)

        chart_frame = QFrame()
        chart_frame.setObjectName("card")
        chart_frame.setMinimumWidth(550)
        chart_frame.setMinimumHeight(300)
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(8, 8, 8, 8)

        self.dash_canvas, self.dash_figure, self.dash_axis = self.make_chart_canvas(300, 6.5)
        chart_layout.addWidget(self.dash_canvas)

        top_section.addWidget(cards_widget, 1)
        top_section.addWidget(chart_frame, 2)

        layout.addLayout(top_section)

        bottom = QHBoxLayout()
        bottom.setSpacing(15)

        low_frame = QFrame()
        low_frame.setObjectName("card")
        low_layout = QVBoxLayout(low_frame)

        low_title = QLabel("Low Stock Alerts")
        low_title.setStyleSheet("font-size:16px;font-weight:bold;")

        self.dash_low_table = QTableWidget()
        self.dash_low_table.setColumnCount(4)
        self.dash_low_table.setHorizontalHeaderLabels(["Product", "Stock", "Minimum", "Bin"])
        self.dash_low_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.dash_low_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        low_export_btn = QPushButton("📥 Export")
        low_export_btn.setObjectName("secondary")
        low_export_btn.clicked.connect(lambda: self.export_table_to_csv(self.dash_low_table, "Low Stock"))

        low_layout.addWidget(low_title)
        low_layout.addWidget(self.dash_low_table)
        low_layout.addWidget(low_export_btn)

        trans_frame = QFrame()
        trans_frame.setObjectName("card")
        trans_layout = QVBoxLayout(trans_frame)

        trans_title = QLabel("Recent Transactions")
        trans_title.setStyleSheet("font-size:16px;font-weight:bold;")

        self.dash_trans_table = QTableWidget()
        self.dash_trans_table.setColumnCount(4)
        self.dash_trans_table.setHorizontalHeaderLabels(["Product", "Type", "Qty", ""])
        self.dash_trans_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.dash_trans_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        trans_export_btn = QPushButton("📥 Export")
        trans_export_btn.setObjectName("secondary")
        trans_export_btn.clicked.connect(lambda: self.export_table_to_csv(self.dash_trans_table, "Transactions"))

        trans_layout.addWidget(trans_title)
        trans_layout.addWidget(self.dash_trans_table)
        trans_layout.addWidget(trans_export_btn)

        bottom.addWidget(low_frame)
        bottom.addWidget(trans_frame)

        layout.addLayout(bottom)

        self.goto_page("dashboard", page)
        self.refresh_dashboard()

    def refresh_dashboard(self):
        total_products = db.scalar("SELECT COUNT(*) FROM PRODUCTS")
        total_stock = db.scalar("SELECT COALESCE(SUM(STOCK_QTY), 0) FROM PRODUCT_WAREHOUSE_STOCK")
        total_warehouse_stock = self.get_total_warehouse_stock()
        total_warehouse_capacity = self.get_total_warehouse_capacity()
        
        # Low stock from view
        low_stock = db.scalar("SELECT COUNT(*) FROM V_LOW_STOCK_PRODUCTS")
        
        inventory_value = db.scalar(
            "SELECT COALESCE(SUM(PWS.STOCK_QTY * P.UNIT_PRICE), 0) "
            "FROM PRODUCT_WAREHOUSE_STOCK PWS "
            "JOIN PRODUCTS P ON P.PRODUCT_ID = PWS.PRODUCT_ID"
        )

        self.card_total_products.setText(str(total_products))
        
        # Total Stock card - show overall stock / overall capacity
        if total_warehouse_capacity > 0:
            self.card_total_stock.setText(f"{total_stock:,}")
            self.card_total_stock_sub.setText(f"<b>Capacity: {total_warehouse_capacity:,} units</b>")
        else:
            self.card_total_stock.setText(f"{total_stock:,}")
            self.card_total_stock_sub.setText("<b>No capacity limit</b>")
        
        self.card_low_stock.setText(str(low_stock))
        self.card_inventory_value.setText("₹{:,.2f}".format(inventory_value))

        category_data = db.execute(
            """
            SELECT CATEGORY, SUM(STOCK_QTY) as TOTAL_STOCK
            FROM PRODUCT_WAREHOUSE_STOCK PWS
            JOIN PRODUCTS P ON P.PRODUCT_ID = PWS.PRODUCT_ID
            GROUP BY CATEGORY
            ORDER BY TOTAL_STOCK DESC
            LIMIT 6
            """,
            fetch=True
        )

        if category_data:
            categories = [row["CATEGORY"] for row in category_data]
            values = [row["TOTAL_STOCK"] for row in category_data]
            self.draw_donut_chart(
                self.dash_axis, self.dash_figure, self.dash_canvas,
                values, categories, "Stock Distribution by Category"
            )

        low_data = db.execute(
            """
            SELECT PRODUCT_NAME, STOCK_QTY, MIN_STOCK
            FROM V_LOW_STOCK_PRODUCTS
            ORDER BY STOCK_QTY ASC
            LIMIT 8
            """,
            fetch=True
        )

        if low_data:
            self.dash_low_table.setRowCount(len(low_data))
            for row, item in enumerate(low_data):
                values = [item["PRODUCT_NAME"], item["STOCK_QTY"], item["MIN_STOCK"], "-"]
                for col, value in enumerate(values):
                    self.dash_low_table.setItem(row, col, QTableWidgetItem(str(value)))
        else:
            self.dash_low_table.setRowCount(0)

        transactions = db.execute(
            """
            SELECT P.PRODUCT_NAME, T.TRANSACTION_TYPE, 
                   T.QUANTITY
            FROM STOCK_TRANSACTIONS T
            JOIN PRODUCTS P ON P.PRODUCT_ID = T.PRODUCT_ID
            ORDER BY T.TRANSACTION_ID DESC
            LIMIT 8
            """,
            fetch=True
        )

        if transactions:
            self.dash_trans_table.setRowCount(len(transactions))
            for row, item in enumerate(transactions):
                tx_type = item["TRANSACTION_TYPE"]
                
                color = QColor(255, 255, 255)
                if tx_type == 'STOCK IN':
                    color = QColor(200, 255, 200)
                else:
                    color = QColor(255, 200, 200)
                
                values = [
                    item["PRODUCT_NAME"], 
                    item["TRANSACTION_TYPE"], 
                    item["QUANTITY"], 
                    ""
                ]
                for col, value in enumerate(values):
                    cell = QTableWidgetItem(str(value))
                    cell.setBackground(color)
                    self.dash_trans_table.setItem(row, col, cell)
        else:
            self.dash_trans_table.setRowCount(0)

    def create_card(self, title, color_key, show_sub=False):
        start, end = CARD_GRADIENTS[color_key]

        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet(
            "QFrame#card {{"
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1,"
            " stop:0 {start}, stop:1 {end});"
            "border: none;"
            "border-radius: 12px;"
            "}}".format(start=start, end=end)
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 12, 15, 12)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)

        value_label = QLabel("0")
        value_label.setObjectName("cardValue")
        value_label.setAlignment(Qt.AlignCenter)

        if show_sub:
            sub_value_label = QLabel("")
            sub_value_label.setObjectName("cardSubValue")
            sub_value_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(title_label)
            layout.addStretch()
            layout.addWidget(value_label)
            layout.addWidget(sub_value_label)
            layout.addStretch()
            return card, value_label, sub_value_label
        else:
            layout.addWidget(title_label)
            layout.addStretch()
            layout.addWidget(value_label)
            layout.addStretch()
            return card, value_label, None

    # ========================================================
    # PRODUCTS
    # ========================================================

    def show_products(self):
        self.activate(self.products_btn)
        self.set_page_header("Products", "Manage your inventory products and stock levels")

        if "products" in self.pages:
            self.load_products()
            self.stack.setCurrentWidget(self.pages["products"])
            return

        page = QWidget()
        layout = QVBoxLayout(page)

        toolbar = QHBoxLayout()

        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("Search product, category...")

        add_btn = QPushButton("+  ADD PRODUCT")
        add_btn.setObjectName("primary")
        add_btn.clicked.connect(self.add_product)

        edit_btn = QPushButton("EDIT")
        edit_btn.setObjectName("secondary")
        edit_btn.clicked.connect(self.edit_product)

        delete_btn = QPushButton("DELETE")
        delete_btn.setObjectName("danger")
        delete_btn.clicked.connect(self.delete_product)

        export_btn = QPushButton("📥 EXPORT")
        export_btn.setObjectName("secondary")
        export_btn.clicked.connect(lambda: self.export_table_to_csv(self.products_table, "Products"))

        toolbar.addWidget(self.product_search)
        toolbar.addWidget(add_btn)
        toolbar.addWidget(edit_btn)
        toolbar.addWidget(delete_btn)
        toolbar.addWidget(export_btn)

        layout.addLayout(toolbar)

        self.products_table = QTableWidget()
        self.products_table.setColumnCount(7)
        self.products_table.setHorizontalHeaderLabels([
            "ID", "Product Name", "Category", "Unit",
            "Price", "Stock", "Min Stock"
        ])
        self.products_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.products_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.product_search.textChanged.connect(self.filter_products)
        layout.addWidget(self.products_table)

        self.goto_page("products", page)
        self.load_products()

    def load_products(self):
        data = db.execute(
            """
            SELECT 
                P.PRODUCT_ID, 
                P.PRODUCT_NAME, 
                P.CATEGORY, 
                P.UNIT,
                P.UNIT_PRICE, 
                P.MIN_STOCK,
                COALESCE(SUM(PWS.STOCK_QTY), 0) AS STOCK_QTY
            FROM PRODUCTS P
            LEFT JOIN PRODUCT_WAREHOUSE_STOCK PWS ON PWS.PRODUCT_ID = P.PRODUCT_ID
            GROUP BY P.PRODUCT_ID, P.PRODUCT_NAME, P.CATEGORY, P.UNIT, P.UNIT_PRICE, P.MIN_STOCK
            ORDER BY P.PRODUCT_ID DESC
            """,
            fetch=True
        )

        if data:
            self.products_table.setRowCount(len(data))
            for row, product in enumerate(data):
                row_color = QColor(255, 255, 255)
                if product["STOCK_QTY"] < product["MIN_STOCK"]:
                    row_color = QColor(255, 200, 200)
                elif product["STOCK_QTY"] >= product["MIN_STOCK"]:
                    row_color = QColor(200, 255, 200)
                
                values = [
                    product["PRODUCT_ID"],
                    product["PRODUCT_NAME"],
                    product["CATEGORY"],
                    product["UNIT"],
                    "₹{:,.2f}".format(product["UNIT_PRICE"]),
                    product["STOCK_QTY"],
                    product["MIN_STOCK"]
                ]
                for col, value in enumerate(values):
                    item = QTableWidgetItem(str(value))
                    item.setBackground(row_color)
                    self.products_table.setItem(row, col, item)
        else:
            self.products_table.setRowCount(0)

    def filter_products(self, text):
        text = text.lower().strip()
        for row in range(self.products_table.rowCount()):
            visible = False
            for col in range(self.products_table.columnCount()):
                item = self.products_table.item(row, col)
                if item and text in item.text().lower():
                    visible = True
                    break
            self.products_table.setRowHidden(row, not visible)

    def selected_product_id(self):
        rows = self.products_table.selectionModel().selectedRows()
        if not rows:
            return None
        row = rows[0].row()
        return int(self.products_table.item(row, 0).text())

    # ========================================================
    # PRODUCT DIALOG
    # ========================================================

    def product_dialog(self, product=None):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Product" if product else "Add Product")
        dialog.setMinimumWidth(550)

        form = QFormLayout(dialog)
        form.setContentsMargins(30, 30, 30, 30)
        form.setSpacing(12)

        name = QLineEdit()
        category = QLineEdit()
        unit = QComboBox()
        unit.addItem("-- Select Unit --", None)
        unit.addItems(["Piece", "Box", "Kg", "Litre", "Packet", "Set"])

        price = QDoubleSpinBox()
        price.setMaximum(99999999)
        price.setDecimals(2)
        price.setPrefix("₹ ")

        minimum = QSpinBox()
        minimum.setMaximum(999999999)

        if product:
            name.setText(product["PRODUCT_NAME"])
            category.setText(product["CATEGORY"])
            unit.setCurrentText(product["UNIT"])
            price.setValue(float(product["UNIT_PRICE"]))
            minimum.setValue(product["MIN_STOCK"])

        form.addRow("Product Name", name)
        form.addRow("Category", category)
        form.addRow("Unit", unit)
        form.addRow("Unit Price", price)
        form.addRow("Minimum Stock", minimum)

        buttons = QHBoxLayout()
        save = QPushButton("SAVE")
        save.setObjectName("primary")
        cancel = QPushButton("CANCEL")
        cancel.setObjectName("secondary")
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        form.addRow(buttons)

        cancel.clicked.connect(dialog.reject)

        def save_product():
            if not name.text().strip():
                QMessageBox.warning(dialog, "Validation", "Product name is required.")
                return
            if not category.text().strip():
                QMessageBox.warning(dialog, "Validation", "Category is required.")
                return
            if not unit.currentText().strip() or unit.currentIndex() == 0:
                QMessageBox.warning(dialog, "Validation", "Please select a unit.")
                return

            if product:
                query = """
                    UPDATE PRODUCTS
                    SET PRODUCT_NAME=%s, CATEGORY=%s, UNIT=%s,
                        UNIT_PRICE=%s, MIN_STOCK=%s
                    WHERE PRODUCT_ID=%s
                """
                params = (
                    name.text().strip(), category.text().strip(),
                    unit.currentText(), price.value(), minimum.value(),
                    product["PRODUCT_ID"]
                )
            else:
                query = """
                    INSERT INTO PRODUCTS
                    (PRODUCT_NAME, CATEGORY, UNIT, UNIT_PRICE, MIN_STOCK)
                    VALUES (%s,%s,%s,%s,%s)
                """
                params = (
                    name.text().strip(), category.text().strip(),
                    unit.currentText(), price.value(), minimum.value()
                )

            result = db.execute(query, params)
            if result:
                dialog.accept()
            else:
                QMessageBox.critical(dialog, "Database Error", "Unable to save product.")

        save.clicked.connect(save_product)
        return dialog

    def add_product(self):
        dialog = self.product_dialog()
        if dialog.exec_():
            self.load_products()
            QMessageBox.information(self, "Success", "Product added successfully.")

    def edit_product(self):
        product_id = self.selected_product_id()
        if not product_id:
            QMessageBox.warning(self, "Edit Product", "Please select a product.")
            return

        result = db.execute("SELECT * FROM PRODUCTS WHERE PRODUCT_ID=%s", (product_id,), fetch=True)
        if not result:
            return

        dialog = self.product_dialog(result[0])
        if dialog.exec_():
            self.load_products()
            QMessageBox.information(self, "Success", "Product updated successfully.")

    def delete_product(self):
        product_id = self.selected_product_id()
        if not product_id:
            QMessageBox.warning(self, "Delete Product", "Please select a product.")
            return

        answer = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this product?",
                                      QMessageBox.Yes | QMessageBox.No)
        if answer != QMessageBox.Yes:
            return

        result = db.execute("DELETE FROM PRODUCTS WHERE PRODUCT_ID=%s", (product_id,))
        if result:
            self.load_products()
            QMessageBox.information(self, "Deleted", "Product deleted successfully.")
        else:
            QMessageBox.critical(self, "Error", "Unable to delete product.")

    # ========================================================
    # WAREHOUSE WITH BIN LOCATIONS
    # ========================================================

    def show_warehouse(self):
        """Build (once) and display the Warehouse Management page."""
        self.activate(self.warehouse_btn)
        self.set_page_header("Warehouse Management", "View and manage warehouses with bin locations")

        if "warehouse" in self.pages:
            self.load_warehouse_data()
            self.stack.setCurrentWidget(self.pages["warehouse"])
            return

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(14)

        layout.addWidget(self.build_warehouse_control_bar())
        layout.addWidget(self.build_capacity_utilization_widget())
        layout.addWidget(self.build_warehouse_split_view(), 1)

        self.goto_page("warehouse", page)
        self.load_warehouse_data()

    # --------------------------------------------------------
    # Warehouse page builders
    # --------------------------------------------------------

    def vertical_divider(self):
        """A thin vertical rule used to visually group toolbar sections."""
        divider = QFrame()
        divider.setObjectName("vDivider")
        divider.setFixedWidth(1)
        divider.setMinimumHeight(30)
        return divider

    def build_warehouse_control_bar(self):
        """Single card holding the warehouse/bin selectors and every CRUD action."""
        bar = QFrame()
        bar.setObjectName("toolbarCard")
        bar.setFixedHeight(64)
        self.apply_soft_shadow(bar, blur=18, y_offset=4, alpha=25)

        row = QHBoxLayout(bar)
        row.setContentsMargins(18, 10, 18, 10)
        row.setSpacing(14)

        # --- Selectors ---------------------------------------------------
        selector_label = QLabel("🏢 WAREHOUSE")
        selector_label.setStyleSheet("font-weight:bold; font-size:12px; color:#475569;")

        self.warehouse_dropdown = QComboBox()
        self.warehouse_dropdown.setMinimumWidth(220)
        self.warehouse_dropdown.currentIndexChanged.connect(self.on_warehouse_dropdown_change)

        bin_label = QLabel("📍 BIN")
        bin_label.setStyleSheet("font-weight:bold; font-size:12px; color:#475569;")

        self.bin_filter_dropdown = QComboBox()
        self.bin_filter_dropdown.setMinimumWidth(180)
        self.bin_filter_dropdown.addItem("All Bins", None)
        self.bin_filter_dropdown.currentIndexChanged.connect(self.on_bin_filter_change)

        row.addWidget(selector_label)
        row.addWidget(self.warehouse_dropdown)
        row.addWidget(bin_label)
        row.addWidget(self.bin_filter_dropdown)

        row.addWidget(self.vertical_divider())
        row.addStretch()

        # --- Warehouse actions --------------------------------------------
        add_wh_btn = QPushButton("+  ADD WAREHOUSE")
        add_wh_btn.setObjectName("primary")
        add_wh_btn.setToolTip("Create a new warehouse")
        add_wh_btn.clicked.connect(self.add_warehouse)

        edit_wh_btn = QPushButton("EDIT")
        edit_wh_btn.setObjectName("secondary")
        edit_wh_btn.setToolTip("Edit the selected warehouse")
        edit_wh_btn.clicked.connect(self.edit_warehouse)

        delete_wh_btn = QPushButton("DELETE")
        delete_wh_btn.setObjectName("danger")
        delete_wh_btn.setToolTip("Delete the selected warehouse")
        delete_wh_btn.clicked.connect(self.delete_warehouse)

        row.addWidget(add_wh_btn)
        row.addWidget(edit_wh_btn)
        row.addWidget(delete_wh_btn)

        row.addWidget(self.vertical_divider())

        return bar

    def build_capacity_utilization_widget(self):
        """Professional capacity utilization widget with warehouse name and location at top."""
        widget = QFrame()
        widget.setObjectName("card")
        widget.setMinimumHeight(140)
        widget.setStyleSheet("""
            QFrame#card {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0f172a, stop:0.3 #1e3a8a, stop:0.7 #3730a3, stop:1 #4338ca);
                border: none;
                border-radius: 12px;
            }
        """)
        self.apply_soft_shadow(widget, blur=25, y_offset=8, alpha=55)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 18, 30, 18)
        layout.setSpacing(8)

        # Top row: Warehouse name and location
        top_layout = QHBoxLayout()
        top_layout.setSpacing(15)
        
        self.wh_hero_name = QLabel("Select a warehouse")
        self.wh_hero_name.setStyleSheet("color: white; font-size: 22px; font-weight: bold; background: transparent;")
        
        self.wh_hero_location = QLabel("")
        self.wh_hero_location.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 14px; background: transparent; padding-top: 4px;")
        
        top_layout.addWidget(self.wh_hero_name)
        top_layout.addWidget(self.wh_hero_location)
        top_layout.addStretch()
        
        layout.addLayout(top_layout)

        # Divider line
        divider_line = QFrame()
        divider_line.setStyleSheet("background: rgba(255,255,255,0.08); max-height: 1px; min-height: 1px;")
        layout.addWidget(divider_line)

        # Main content: Stock info and capacity bar (side by side)
        main_layout = QHBoxLayout()
        main_layout.setSpacing(30)
        
        # Left: Stock info
        left_layout = QVBoxLayout()
        left_layout.setSpacing(2)
        
        stock_label = QLabel("STOCK QUANTITY / CAPACITY")
        stock_label.setStyleSheet("color: rgba(255,255,255,0.5); font-size: 11px; font-weight: bold; letter-spacing: 1.5px; background: transparent;")
        
        stock_row = QHBoxLayout()
        stock_row.setSpacing(15)
        
        self.wh_stock_value = QLabel("0")
        self.wh_stock_value.setStyleSheet("color: white; font-size: 40px; font-weight: bold; background: transparent;")
        
        self.wh_capacity_value = QLabel("/ 0")
        self.wh_capacity_value.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 26px; font-weight: normal; background: transparent;")
        
        stock_row.addWidget(self.wh_stock_value)
        stock_row.addWidget(self.wh_capacity_value)
        stock_row.addStretch()
        
        left_layout.addWidget(stock_label)
        left_layout.addLayout(stock_row)
        
        main_layout.addLayout(left_layout, 2)

        # Center: Vertical divider
        divider = QFrame()
        divider.setStyleSheet("background: rgba(255,255,255,0.1); max-width: 2px; min-width: 2px;")
        main_layout.addWidget(divider)

        # Right side: Percentage and progress bar
        right_layout = QVBoxLayout()
        right_layout.setSpacing(6)
        right_layout.setAlignment(Qt.AlignCenter)
        
        # Percentage
        pct_layout = QHBoxLayout()
        pct_layout.addStretch()
        self.wh_capacity_pct_label = QLabel("0%")
        self.wh_capacity_pct_label.setStyleSheet("color: white; font-size: 44px; font-weight: bold; background: transparent;")
        self.wh_capacity_pct_label.setAlignment(Qt.AlignRight)
        pct_layout.addWidget(self.wh_capacity_pct_label)
        pct_layout.addStretch()
        right_layout.addLayout(pct_layout)
        
        # Progress bar
        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(12)
        
        self.wh_capacity_bar = QProgressBar()
        self.wh_capacity_bar.setRange(0, 100)
        self.wh_capacity_bar.setValue(0)
        self.wh_capacity_bar.setTextVisible(False)
        self.wh_capacity_bar.setFixedHeight(18)
        self.wh_capacity_bar.setMinimumWidth(250)
        self.wh_capacity_bar.setStyleSheet("""
            QProgressBar {
                background: rgba(255,255,255,0.12);
                border: none;
                border-radius: 9px;
            }
            QProgressBar::chunk {
                background: #4ade80;
                border-radius: 9px;
            }
        """)
        
        progress_layout.addWidget(self.wh_capacity_bar, 1)
        right_layout.addLayout(progress_layout)
        
        main_layout.addLayout(right_layout, 2)
        layout.addLayout(main_layout)

        return widget

    def build_warehouse_split_view(self):
        """Horizontal splitter: bin locations (left) and products (right)."""
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.build_bin_panel())
        splitter.addWidget(self.build_products_panel())
        splitter.setSizes([350, 750])
        return splitter

    def build_bin_panel(self):
        """Left panel: bin locations table with toolbar above."""
        bin_panel = QFrame()
        bin_panel.setObjectName("card")
        bin_panel.setMinimumWidth(320)
        bin_layout = QVBoxLayout(bin_panel)
        bin_layout.setContentsMargins(14, 14, 14, 14)
        bin_layout.setSpacing(10)

        # Header with title and count
        bin_header = QHBoxLayout()
        bin_title = QLabel("📦 BIN LOCATIONS")
        bin_title.setObjectName("sectionLabel")
        self.bin_count_badge = QLabel("0")
        self.bin_count_badge.setObjectName("sectionCount")
        bin_header.addWidget(bin_title)
        bin_header.addWidget(self.bin_count_badge)
        bin_header.addStretch()
        bin_layout.addLayout(bin_header)

        # Bin toolbar with Add, Edit, Delete, Export buttons
        bin_toolbar = QHBoxLayout()
        bin_toolbar.setSpacing(8)
        
        self.bin_add_btn = QPushButton("+  ADD BIN")
        self.bin_add_btn.setObjectName("primary")
        self.bin_add_btn.setCursor(Qt.PointingHandCursor)
        self.bin_add_btn.clicked.connect(self.add_bin_location)
        
        self.bin_edit_btn = QPushButton("✏️ EDIT")
        self.bin_edit_btn.setObjectName("secondary")
        self.bin_edit_btn.setCursor(Qt.PointingHandCursor)
        self.bin_edit_btn.clicked.connect(self.edit_bin_location)
        
        self.bin_delete_btn = QPushButton("🗑️ DELETE")
        self.bin_delete_btn.setObjectName("danger")
        self.bin_delete_btn.setCursor(Qt.PointingHandCursor)
        self.bin_delete_btn.clicked.connect(self.delete_bin_location)
        
        self.bin_export_btn = QPushButton("📥 EXPORT")
        self.bin_export_btn.setObjectName("secondary")
        self.bin_export_btn.setCursor(Qt.PointingHandCursor)
        self.bin_export_btn.clicked.connect(lambda: self.export_table_to_csv(self.bin_table, "Bin Locations"))
        
        bin_toolbar.addStretch()
        bin_toolbar.addWidget(self.bin_add_btn)
        bin_toolbar.addWidget(self.bin_edit_btn)
        bin_toolbar.addWidget(self.bin_delete_btn)
        bin_toolbar.addWidget(self.bin_export_btn)
        bin_layout.addLayout(bin_toolbar)

        # Bin table
        self.bin_table = QTableWidget()
        self.bin_table.setColumnCount(5)
        self.bin_table.setHorizontalHeaderLabels(["ID", "Bin Name", "Capacity", "Used", "Category"])
        self.bin_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.bin_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.bin_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.bin_table.setColumnHidden(0, True)
        self.bin_table.verticalHeader().setVisible(False)
        self.bin_table.verticalHeader().setDefaultSectionSize(40)
        self.bin_table.itemSelectionChanged.connect(self.on_bin_selected)

        bin_layout.addWidget(self.bin_table, 1)

        # Bin summary stats
        bin_stats = QHBoxLayout()
        self.bin_total_capacity_label = QLabel("Total Bin Capacity: 0")
        self.bin_used_capacity_label = QLabel("Used: 0")
        self.bin_available_capacity_label = QLabel("Available: 0")
        for lbl in (self.bin_total_capacity_label, self.bin_used_capacity_label,
                    self.bin_available_capacity_label):
            lbl.setStyleSheet("color:#64748b; font-size:12px;")
        bin_stats.addWidget(self.bin_total_capacity_label)
        bin_stats.addWidget(self.bin_used_capacity_label)
        bin_stats.addWidget(self.bin_available_capacity_label)
        bin_stats.addStretch()
        bin_layout.addLayout(bin_stats)

        return bin_panel

    def build_products_panel(self):
        """Right panel: products in the selected warehouse/bin."""
        products_panel = QFrame()
        products_panel.setObjectName("card")
        products_layout = QVBoxLayout(products_panel)
        products_layout.setContentsMargins(14, 14, 14, 14)
        products_layout.setSpacing(10)

        products_header = QHBoxLayout()
        products_title = QLabel("📋 PRODUCTS")
        products_title.setObjectName("sectionLabel")
        products_header.addWidget(products_title)
        products_header.addStretch()

        wh_export_btn = QPushButton("📥 Export")
        wh_export_btn.setObjectName("secondary")
        wh_export_btn.clicked.connect(lambda: self.export_table_to_csv(self.wh_products_table, "Warehouse Products"))

        products_header.addWidget(wh_export_btn)
        products_layout.addLayout(products_header)

        self.wh_products_table = QTableWidget()
        self.wh_products_table.setColumnCount(6)
        self.wh_products_table.setHorizontalHeaderLabels(["Product", "Category", "Unit", "Stock", "Unit Price", "Status"])
        self.wh_products_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.wh_products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.wh_products_table.verticalHeader().setVisible(False)

        products_layout.addWidget(self.wh_products_table, 1)

        return products_panel

    def apply_soft_shadow(self, widget, blur=25, y_offset=8, alpha=60):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur)
        shadow.setOffset(0, y_offset)
        shadow.setColor(QColor(15, 23, 42, alpha))
        widget.setGraphicsEffect(shadow)

    def load_warehouse_data(self):
        data = db.execute(
            """
            SELECT WAREHOUSE_ID, WAREHOUSE_NAME, LOCATION, CAPACITY
            FROM WAREHOUSE
            ORDER BY WAREHOUSE_NAME
            """,
            fetch=True
        )

        self.warehouse_dropdown.clear()
        self.warehouse_dropdown.addItem("-- Select Warehouse --", None)
        if data:
            for wh in data:
                self.warehouse_dropdown.addItem(wh["WAREHOUSE_NAME"], wh["WAREHOUSE_ID"])

        self.load_all_bins_dropdown()

    def load_all_bins_dropdown(self):
        data = db.execute(
            """
            SELECT B.BIN_ID, B.BIN_NAME, W.WAREHOUSE_NAME
            FROM BIN_LOCATION B
            JOIN WAREHOUSE W ON W.WAREHOUSE_ID = B.WAREHOUSE_ID
            ORDER BY W.WAREHOUSE_NAME, B.BIN_NAME
            """,
            fetch=True
        )

        previously_selected = self.bin_filter_dropdown.currentData() if self.bin_filter_dropdown.count() else None

        self.bin_filter_dropdown.blockSignals(True)
        self.bin_filter_dropdown.clear()
        self.bin_filter_dropdown.addItem("All Bins", None)
        if data:
            for b in data:
                label = f"{b['WAREHOUSE_NAME']} \u2022 {b['BIN_NAME']}"
                self.bin_filter_dropdown.addItem(label, b["BIN_ID"])

        if previously_selected:
            idx = self.bin_filter_dropdown.findData(previously_selected)
            if idx >= 0:
                self.bin_filter_dropdown.setCurrentIndex(idx)
        self.bin_filter_dropdown.blockSignals(False)

    def on_warehouse_dropdown_change(self, index):
        wh_id = self.warehouse_dropdown.currentData()
        if wh_id:
            self.load_bin_locations(wh_id)
            self.load_warehouse_details(wh_id)

            pending_bin_id = getattr(self, "_pending_bin_selection", None)
            if pending_bin_id:
                self._pending_bin_selection = None
                bin_info = db.execute(
                    "SELECT BIN_NAME FROM BIN_LOCATION WHERE BIN_ID=%s",
                    (pending_bin_id,),
                    fetch=True
                )
                self.apply_bin_selection(wh_id, pending_bin_id, bin_info[0] if bin_info else None)
            else:
                self.load_products_for_warehouse(wh_id, None)
                self.update_capacity_utilization(wh_id, None)
        else:
            self.clear_warehouse_details()
            self.bin_table.setRowCount(0)
            self.wh_products_table.setRowCount(0)
            self.clear_capacity_utilization()

    def apply_bin_selection(self, wh_id, bin_id, bin_info=None):
        self.load_products_for_warehouse(wh_id, bin_id)
        self.update_capacity_utilization(wh_id, bin_id)

        for row in range(self.bin_table.rowCount()):
            if int(self.bin_table.item(row, 0).text()) == bin_id:
                self.bin_table.selectRow(row)
                break

        idx = self.bin_filter_dropdown.findData(bin_id)
        if idx >= 0 and self.bin_filter_dropdown.currentIndex() != idx:
            self.bin_filter_dropdown.blockSignals(True)
            self.bin_filter_dropdown.setCurrentIndex(idx)
            self.bin_filter_dropdown.blockSignals(False)

    def on_bin_filter_change(self, index):
        bin_id = self.bin_filter_dropdown.currentData()
        wh_id = self.warehouse_dropdown.currentData()

        if bin_id is None:
            if wh_id:
                self.load_products_for_warehouse(wh_id, None)
                self.update_capacity_utilization(wh_id, None)
            return

        bin_info = db.execute(
            "SELECT WAREHOUSE_ID, BIN_NAME FROM BIN_LOCATION WHERE BIN_ID=%s",
            (bin_id,),
            fetch=True
        )
        if not bin_info:
            return
        bin_row = bin_info[0]
        bin_warehouse_id = bin_row["WAREHOUSE_ID"]

        if wh_id != bin_warehouse_id:
            self._pending_bin_selection = bin_id
            idx = self.warehouse_dropdown.findData(bin_warehouse_id)
            if idx >= 0:
                self.warehouse_dropdown.setCurrentIndex(idx)
            return

        self.apply_bin_selection(wh_id, bin_id, bin_row)

    def on_bin_selected(self):
        rows = self.bin_table.selectionModel().selectedRows()
        if rows:
            row = rows[0].row()
            bin_id = int(self.bin_table.item(row, 0).text())
            wh_id = self.warehouse_dropdown.currentData()
            if wh_id:
                bin_info = db.execute(
                    "SELECT BIN_NAME FROM BIN_LOCATION WHERE BIN_ID=%s",
                    (bin_id,),
                    fetch=True
                )
                self.apply_bin_selection(wh_id, bin_id, bin_info[0] if bin_info else None)

    def load_bin_locations(self, warehouse_id):
        data = db.execute(
            """
            SELECT 
                B.BIN_ID, 
                B.BIN_NAME, 
                B.CAPACITY,
                COALESCE(SUM(PWS.STOCK_QTY), 0) AS USED,
                B.DESCRIPTION AS CATEGORY,
                CASE 
                    WHEN COALESCE(SUM(PWS.STOCK_QTY), 0) = 0 THEN 'Empty'
                    WHEN COALESCE(SUM(PWS.STOCK_QTY), 0) < B.CAPACITY * 0.3 THEN 'Low Usage'
                    WHEN COALESCE(SUM(PWS.STOCK_QTY), 0) < B.CAPACITY * 0.7 THEN 'Medium Usage'
                    ELSE 'High Usage'
                END AS USAGE_STATUS
            FROM BIN_LOCATION B
            LEFT JOIN PRODUCT_WAREHOUSE_STOCK PWS ON PWS.BIN_ID = B.BIN_ID
            WHERE B.WAREHOUSE_ID = %s
            GROUP BY B.BIN_ID, B.BIN_NAME, B.CAPACITY, B.DESCRIPTION
            ORDER BY B.BIN_NAME
            """,
            (warehouse_id,),
            fetch=True
        )

        self.bin_table.setRowCount(0)

        if data:
            self.bin_table.setRowCount(len(data))
            total_capacity = 0
            total_used = 0
            for row, bin_data in enumerate(data):
                row_color = QColor(255, 255, 255)
                if bin_data["USAGE_STATUS"] == "Empty":
                    row_color = QColor(255, 200, 200)
                elif bin_data["USAGE_STATUS"] == "Low Usage":
                    row_color = QColor(255, 230, 180)
                elif bin_data["USAGE_STATUS"] == "High Usage":
                    row_color = QColor(200, 255, 200)
                
                values = [
                    bin_data["BIN_ID"],
                    bin_data["BIN_NAME"],
                    bin_data["CAPACITY"],
                    bin_data["USED"],
                    bin_data["CATEGORY"] or "General"
                ]
                for col, value in enumerate(values):
                    item = QTableWidgetItem(str(value))
                    item.setBackground(row_color)
                    item.setToolTip(f"Usage: {bin_data['USAGE_STATUS']}")
                    self.bin_table.setItem(row, col, item)

                total_capacity += bin_data["CAPACITY"]
                total_used += bin_data["USED"]

            self.bin_total_capacity_label.setText(f"Total Bin Capacity: {total_capacity}")
            self.bin_used_capacity_label.setText(f"Used: {total_used}")
            self.bin_available_capacity_label.setText(f"Available: {total_capacity - total_used}")

        self.bin_count_badge.setText(str(len(data) if data else 0))

    def load_products_for_warehouse(self, warehouse_id, bin_id=None):
        if bin_id:
            query = """
                SELECT P.PRODUCT_NAME, P.CATEGORY, P.UNIT,
                       PWS.STOCK_QTY, P.UNIT_PRICE,
                       CASE 
                           WHEN PWS.STOCK_QTY = 0 THEN 'Out of Stock'
                           WHEN PWS.STOCK_QTY <= P.MIN_STOCK THEN 'Low Stock'
                           ELSE 'In Stock'
                       END AS STOCK_STATUS
                FROM PRODUCT_WAREHOUSE_STOCK PWS
                JOIN PRODUCTS P ON P.PRODUCT_ID = PWS.PRODUCT_ID
                WHERE PWS.WAREHOUSE_ID = %s AND PWS.BIN_ID = %s
                ORDER BY P.PRODUCT_NAME
            """
            params = (warehouse_id, bin_id)
        else:
            query = """
                SELECT P.PRODUCT_NAME, P.CATEGORY, P.UNIT,
                       COALESCE(PWS.STOCK_QTY, 0) AS STOCK_QTY,
                       P.UNIT_PRICE,
                       CASE 
                           WHEN COALESCE(PWS.STOCK_QTY, 0) = 0 THEN 'Out of Stock'
                           WHEN COALESCE(PWS.STOCK_QTY, 0) <= P.MIN_STOCK THEN 'Low Stock'
                           ELSE 'In Stock'
                       END AS STOCK_STATUS
                FROM PRODUCTS P
                LEFT JOIN PRODUCT_WAREHOUSE_STOCK PWS 
                    ON PWS.PRODUCT_ID = P.PRODUCT_ID AND PWS.WAREHOUSE_ID = %s
                ORDER BY P.PRODUCT_NAME
            """
            params = (warehouse_id,)

        data = db.execute(query, params, fetch=True)

        if data:
            self.wh_products_table.setRowCount(len(data))
            for row, p in enumerate(data):
                if p["STOCK_STATUS"] == "Out of Stock":
                    row_color = QColor(255, 200, 200)
                    status_text = "🔴 Out of Stock"
                elif p["STOCK_STATUS"] == "Low Stock":
                    row_color = QColor(255, 230, 180)
                    status_text = "🟠 Low Stock"
                else:
                    row_color = QColor(200, 255, 200)
                    status_text = "🟢 In Stock"

                values = [
                    p["PRODUCT_NAME"],
                    p["CATEGORY"],
                    p["UNIT"],
                    p["STOCK_QTY"],
                    "₹{:,.2f}".format(p["UNIT_PRICE"]),
                    status_text
                ]
                for col, value in enumerate(values):
                    item = QTableWidgetItem(str(value))
                    item.setBackground(row_color)
                    item.setToolTip(f"Status: {p['STOCK_STATUS']}")
                    self.wh_products_table.setItem(row, col, item)
        else:
            self.wh_products_table.setRowCount(0)

    def update_capacity_utilization(self, warehouse_id, bin_id=None):
        wh_info = db.execute(
            "SELECT CAPACITY, WAREHOUSE_NAME, LOCATION FROM WAREHOUSE WHERE WAREHOUSE_ID=%s",
            (warehouse_id,),
            fetch=True
        )
        
        if not wh_info:
            return
        
        warehouse_capacity = wh_info[0]["CAPACITY"] or 0
        warehouse_name = wh_info[0]["WAREHOUSE_NAME"]
        location = wh_info[0]["LOCATION"] or ""
        
        self.wh_hero_name.setText(warehouse_name)
        if location:
            self.wh_hero_location.setText(f"📍 {location}")
        else:
            self.wh_hero_location.setText("")
        
        if bin_id:
            # Show stats for specific bin
            bin_info = db.execute(
                """
                SELECT B.CAPACITY, COALESCE(SUM(PWS.STOCK_QTY), 0) AS TOTAL_STOCK
                FROM BIN_LOCATION B
                LEFT JOIN PRODUCT_WAREHOUSE_STOCK PWS ON PWS.BIN_ID = B.BIN_ID
                WHERE B.BIN_ID = %s
                GROUP BY B.BIN_ID, B.CAPACITY
                """,
                (bin_id,),
                fetch=True
            )
            
            if bin_info:
                total_stock = bin_info[0]["TOTAL_STOCK"]
                capacity = bin_info[0]["CAPACITY"]
                
                self.wh_stock_value.setText(f"{total_stock:,}")
                self.wh_capacity_value.setText(f"/ {capacity:,}")
                
                if capacity > 0:
                    percent = round((total_stock / capacity) * 100)
                else:
                    percent = 0
                display_percent = min(percent, 100)
                self.wh_capacity_pct_label.setText(f"{percent}%")
                self.wh_capacity_bar.setValue(display_percent)
                
        else:
            # Show stats for entire warehouse
            total_stock = db.scalar(
                "SELECT COALESCE(SUM(STOCK_QTY), 0) FROM PRODUCT_WAREHOUSE_STOCK WHERE WAREHOUSE_ID=%s",
                (warehouse_id,)
            )
            
            self.wh_stock_value.setText(f"{total_stock:,}")
            self.wh_capacity_value.setText(f"/ {warehouse_capacity:,}")
            
            if warehouse_capacity > 0:
                percent = round((total_stock / warehouse_capacity) * 100)
            else:
                percent = 0
            display_percent = min(percent, 100)
            self.wh_capacity_pct_label.setText(f"{percent}%")
            self.wh_capacity_bar.setValue(display_percent)

    def clear_capacity_utilization(self):
        self.wh_stock_value.setText("0")
        self.wh_capacity_value.setText("/ 0")
        self.wh_capacity_pct_label.setText("0%")
        self.wh_capacity_bar.setValue(0)
        self.wh_hero_location.setText("")

    def load_warehouse_details(self, warehouse_id):
        wh_info = db.execute(
            """
            SELECT WAREHOUSE_NAME, LOCATION, CAPACITY
            FROM WAREHOUSE
            WHERE WAREHOUSE_ID=%s
            """,
            (warehouse_id,),
            fetch=True
        )

        if wh_info:
            wh = wh_info[0]
            self.wh_hero_name.setText(wh["WAREHOUSE_NAME"])
            if wh["LOCATION"]:
                self.wh_hero_location.setText(f"📍 {wh['LOCATION']}")
            else:
                self.wh_hero_location.setText("")

    def clear_warehouse_details(self):
        self.wh_hero_name.setText("Select a warehouse")
        self.wh_hero_location.setText("")
        self.clear_capacity_utilization()

    # ========================================================
    # BIN LOCATION DIALOG
    # ========================================================

    def bin_location_dialog(self, bin_data=None):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Bin Location" if bin_data else "Add Bin Location")
        dialog.setMinimumWidth(450)

        form = QFormLayout(dialog)
        form.setContentsMargins(30, 30, 30, 30)
        form.setSpacing(12)

        wh_id = self.warehouse_dropdown.currentData()
        if not wh_id:
            QMessageBox.warning(self, "Error", "Please select a warehouse first.")
            return None

        bin_name = QLineEdit()
        bin_name.setPlaceholderText("e.g., Aisle A - Shelf 1")

        capacity = QSpinBox()
        capacity.setMaximum(999999)
        capacity.setSuffix(" units")
        capacity.setMinimum(1)

        description = QTextEdit()
        description.setPlaceholderText("Optional description / category...")
        description.setMaximumHeight(80)

        if bin_data:
            bin_name.setText(bin_data["BIN_NAME"])
            capacity.setValue(bin_data["CAPACITY"])
            description.setPlainText(bin_data.get("DESCRIPTION") or "")

        form.addRow("Bin Name *", bin_name)
        form.addRow("Capacity *", capacity)
        form.addRow("Description / Category", description)

        buttons = QHBoxLayout()
        save = QPushButton("SAVE")
        save.setObjectName("primary")
        cancel = QPushButton("CANCEL")
        cancel.setObjectName("secondary")
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        form.addRow(buttons)

        cancel.clicked.connect(dialog.reject)

        def save_bin():
            name = bin_name.text().strip()
            cap = capacity.value()
            desc = description.toPlainText().strip()

            if not name:
                QMessageBox.warning(dialog, "Validation", "Bin name is required.")
                return
            if cap <= 0:
                QMessageBox.warning(dialog, "Validation", "Capacity must be greater than 0.")
                return

            check_query = """
                SELECT COUNT(*) FROM BIN_LOCATION 
                WHERE WAREHOUSE_ID = %s AND BIN_NAME = %s
            """
            params_check = (wh_id, name)
            if bin_data:
                check_query += " AND BIN_ID != %s"
                params_check = (wh_id, name, bin_data["BIN_ID"])

            exists = db.scalar(check_query, params_check)
            if exists > 0:
                QMessageBox.warning(dialog, "Validation", f"Bin name '{name}' already exists in this warehouse.")
                return

            can_add, msg = self.check_bin_capacity_within_warehouse(
                wh_id, cap, 
                bin_data["BIN_ID"] if bin_data else None
            )
            if not can_add:
                QMessageBox.warning(dialog, "Capacity Exceeded", msg)
                return

            if bin_data:
                query = """
                    UPDATE BIN_LOCATION
                    SET BIN_NAME=%s, CAPACITY=%s, DESCRIPTION=%s
                    WHERE BIN_ID=%s
                """
                params = (name, cap, desc, bin_data["BIN_ID"])
            else:
                query = """
                    INSERT INTO BIN_LOCATION (WAREHOUSE_ID, BIN_NAME, CAPACITY, DESCRIPTION)
                    VALUES (%s, %s, %s, %s)
                """
                params = (wh_id, name, cap, desc)

            result = db.execute(query, params)
            if result:
                dialog.accept()
            else:
                QMessageBox.critical(dialog, "Database Error", "Unable to save bin location.")

        save.clicked.connect(save_bin)
        return dialog

    def add_bin_location(self):
        dialog = self.bin_location_dialog()
        if dialog and dialog.exec_():
            wh_id = self.warehouse_dropdown.currentData()
            if wh_id:
                self.load_bin_locations(wh_id)
                self.load_warehouse_details(wh_id)
                self.load_all_bins_dropdown()
                QMessageBox.information(self, "Success", "Bin location added successfully.")

    def edit_bin_location(self, bin_id=None, _checked=None):
        if bin_id is None:
            rows = self.bin_table.selectionModel().selectedRows()
            if not rows:
                QMessageBox.warning(self, "Edit Bin", "Please select a bin location.")
                return
            row = rows[0].row()
            bin_id = int(self.bin_table.item(row, 0).text())

        result = db.execute(
            "SELECT * FROM BIN_LOCATION WHERE BIN_ID=%s",
            (bin_id,),
            fetch=True
        )
        if not result:
            QMessageBox.warning(self, "Edit Bin", "Bin location not found.")
            return

        dialog = self.bin_location_dialog(result[0])
        if dialog and dialog.exec_():
            wh_id = self.warehouse_dropdown.currentData()
            if wh_id:
                self.load_bin_locations(wh_id)
                self.load_warehouse_details(wh_id)
                self.load_all_bins_dropdown()
                QMessageBox.information(self, "Success", "Bin location updated successfully.")

    def delete_bin_location(self, bin_id=None, _checked=None):
        if bin_id is None:
            rows = self.bin_table.selectionModel().selectedRows()
            if not rows:
                QMessageBox.warning(self, "Delete Bin", "Please select a bin location.")
                return
            row = rows[0].row()
            bin_id = int(self.bin_table.item(row, 0).text())

        stock_count = db.scalar(
            "SELECT COUNT(*) FROM PRODUCT_WAREHOUSE_STOCK WHERE BIN_ID=%s AND STOCK_QTY>0",
            (bin_id,)
        )

        if stock_count > 0:
            QMessageBox.warning(self, "Cannot Delete", "This bin has products with stock. Please move them first.")
            return

        bin_name = self.bin_table.item(row, 1).text()

        answer = QMessageBox.question(
            self, 
            "Confirm Delete", 
            f"Delete bin '{bin_name}' permanently?",
            QMessageBox.Yes | QMessageBox.No
        )
        if answer != QMessageBox.Yes:
            return

        result = db.execute("DELETE FROM BIN_LOCATION WHERE BIN_ID=%s", (bin_id,))
        if result:
            wh_id = self.warehouse_dropdown.currentData()
            if wh_id:
                self.load_bin_locations(wh_id)
                self.load_warehouse_details(wh_id)
            self.load_all_bins_dropdown()
            QMessageBox.information(self, "Deleted", "Bin location deleted successfully.")
        else:
            QMessageBox.critical(self, "Error", "Unable to delete bin location.")

    # ========================================================
    # WAREHOUSE DIALOG
    # ========================================================

    def warehouse_dialog(self, warehouse=None):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Warehouse" if warehouse else "Add Warehouse")
        dialog.setMinimumWidth(450)

        form = QFormLayout(dialog)
        form.setContentsMargins(30, 30, 30, 30)
        form.setSpacing(12)

        name = QLineEdit()
        location = QLineEdit()
        capacity = QSpinBox()
        capacity.setMaximum(999999999)
        capacity.setSuffix(" units")

        if warehouse:
            name.setText(warehouse["WAREHOUSE_NAME"])
            location.setText(warehouse["LOCATION"])
            capacity.setValue(warehouse["CAPACITY"])

        form.addRow("Warehouse Name", name)
        form.addRow("Location", location)
        form.addRow("Capacity", capacity)

        buttons = QHBoxLayout()
        save = QPushButton("SAVE")
        save.setObjectName("primary")
        cancel = QPushButton("CANCEL")
        cancel.setObjectName("secondary")
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        form.addRow(buttons)

        cancel.clicked.connect(dialog.reject)

        def save_warehouse():
            if not name.text().strip():
                QMessageBox.warning(dialog, "Validation", "Warehouse name is required.")
                return
            if not location.text().strip():
                QMessageBox.warning(dialog, "Validation", "Location is required.")
                return

            new_capacity = capacity.value()
            
            if warehouse:
                current_bin_total = self.get_bin_total_capacity(warehouse["WAREHOUSE_ID"])
                if new_capacity < current_bin_total:
                    QMessageBox.warning(
                        dialog, 
                        "Capacity Error", 
                        f"Cannot reduce capacity below total bin capacity ({current_bin_total} units)."
                    )
                    return
                
                query = """
                    UPDATE WAREHOUSE
                    SET WAREHOUSE_NAME=%s, LOCATION=%s, CAPACITY=%s
                    WHERE WAREHOUSE_ID=%s
                """
                params = (name.text().strip(), location.text().strip(), new_capacity, warehouse["WAREHOUSE_ID"])
            else:
                query = """
                    INSERT INTO WAREHOUSE (WAREHOUSE_NAME, LOCATION, CAPACITY)
                    VALUES (%s,%s,%s)
                """
                params = (name.text().strip(), location.text().strip(), new_capacity)

            result = db.execute(query, params)
            if result:
                dialog.accept()
            else:
                QMessageBox.critical(dialog, "Database Error", "Unable to save warehouse.")

        save.clicked.connect(save_warehouse)
        return dialog

    def add_warehouse(self):
        dialog = self.warehouse_dialog()
        if dialog.exec_():
            self.load_warehouse_data()
            QMessageBox.information(self, "Success", "Warehouse added successfully.")

    def edit_warehouse(self):
        wh_id = self.warehouse_dropdown.currentData()
        if not wh_id:
            QMessageBox.warning(self, "Edit Warehouse", "Please select a warehouse.")
            return

        result = db.execute("SELECT * FROM WAREHOUSE WHERE WAREHOUSE_ID=%s", (wh_id,), fetch=True)
        if not result:
            return

        dialog = self.warehouse_dialog(result[0])
        if dialog.exec_():
            self.load_warehouse_data()
            QMessageBox.information(self, "Success", "Warehouse updated successfully.")

    def delete_warehouse(self):
        wh_id = self.warehouse_dropdown.currentData()
        if not wh_id:
            QMessageBox.warning(self, "Delete Warehouse", "Please select a warehouse.")
            return

        products_count = db.scalar(
            "SELECT COUNT(*) FROM PRODUCT_WAREHOUSE_STOCK WHERE WAREHOUSE_ID=%s AND STOCK_QTY>0",
            (wh_id,)
        )
        if products_count > 0:
            QMessageBox.warning(self, "Cannot Delete", "This warehouse has products with stock. Please move them first.")
            return

        bins_count = db.scalar(
            "SELECT COUNT(*) FROM BIN_LOCATION WHERE WAREHOUSE_ID=%s",
            (wh_id,)
        )
        if bins_count > 0:
            QMessageBox.warning(self, "Cannot Delete", "This warehouse has bin locations. Please delete them first.")
            return

        answer = QMessageBox.question(self, "Confirm Delete", "Delete this warehouse permanently?",
                                      QMessageBox.Yes | QMessageBox.No)
        if answer != QMessageBox.Yes:
            return

        result = db.execute("DELETE FROM WAREHOUSE WHERE WAREHOUSE_ID=%s", (wh_id,))
        if result:
            self.load_warehouse_data()
            QMessageBox.information(self, "Deleted", "Warehouse deleted successfully.")
        else:
            QMessageBox.critical(self, "Error", "Unable to delete warehouse.")

    # ========================================================
    # SUPPLIERS
    # ========================================================

    def show_suppliers(self):
        self.activate(self.supplier_btn)
        self.set_page_header("Supplier Management", "Manage suppliers and their products")

        if "suppliers" in self.pages:
            self.load_suppliers()
            self.stack.setCurrentWidget(self.pages["suppliers"])
            return

        page = QWidget()
        layout = QVBoxLayout(page)

        toolbar = QHBoxLayout()
        add_btn = QPushButton("+  ADD SUPPLIER")
        add_btn.setObjectName("primary")
        add_btn.clicked.connect(self.add_supplier)

        edit_btn = QPushButton("EDIT")
        edit_btn.setObjectName("secondary")
        edit_btn.clicked.connect(self.edit_supplier)

        delete_btn = QPushButton("DELETE")
        delete_btn.setObjectName("danger")
        delete_btn.clicked.connect(self.delete_supplier)

        export_btn = QPushButton("📥 EXPORT")
        export_btn.setObjectName("secondary")
        export_btn.clicked.connect(lambda: self.export_table_to_csv(self.supplier_table, "Suppliers"))

        toolbar.addStretch()
        toolbar.addWidget(add_btn)
        toolbar.addWidget(edit_btn)
        toolbar.addWidget(delete_btn)
        toolbar.addWidget(export_btn)

        layout.addLayout(toolbar)

        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter by Product:")
        self.supplier_product_filter = QComboBox()
        self.supplier_product_filter.addItem("All Products", None)
        products = db.execute("SELECT PRODUCT_ID, PRODUCT_NAME FROM PRODUCTS ORDER BY PRODUCT_NAME", fetch=True)
        if products:
            for p in products:
                self.supplier_product_filter.addItem(p["PRODUCT_NAME"], p["PRODUCT_ID"])

        self.supplier_product_filter.currentIndexChanged.connect(self.filter_suppliers)

        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.supplier_product_filter)
        filter_layout.addStretch()

        layout.addLayout(filter_layout)

        self.supplier_table = QTableWidget()
        self.supplier_table.setColumnCount(6)
        self.supplier_table.setHorizontalHeaderLabels([
            "ID", "Supplier Name", "Address", "Location", "Product", ""
        ])
        self.supplier_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.supplier_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.supplier_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.supplier_table)

        self.goto_page("suppliers", page)
        self.load_suppliers()

    def load_suppliers(self):
        data = db.execute(
            """
            SELECT S.SUPPLIER_ID, S.SUPPLIER_NAME, S.ADDRESS, S.LOCATION,
                   P.PRODUCT_NAME
            FROM SUPPLIER S
            LEFT JOIN PRODUCTS P ON S.PRODUCT_ID = P.PRODUCT_ID
            ORDER BY S.SUPPLIER_ID
            """,
            fetch=True
        )

        if data:
            self.supplier_table.setRowCount(len(data))
            for row, s in enumerate(data):
                values = [
                    s["SUPPLIER_ID"], s["SUPPLIER_NAME"], s["ADDRESS"] or "-",
                    s["LOCATION"], s["PRODUCT_NAME"] or "-", ""
                ]
                for col, value in enumerate(values):
                    self.supplier_table.setItem(row, col, QTableWidgetItem(str(value)))
        else:
            self.supplier_table.setRowCount(0)

    def filter_suppliers(self):
        product_id = self.supplier_product_filter.currentData()

        if product_id is None:
            query = """
                SELECT S.SUPPLIER_ID, S.SUPPLIER_NAME, S.ADDRESS, S.LOCATION,
                       P.PRODUCT_NAME
                FROM SUPPLIER S
                LEFT JOIN PRODUCTS P ON S.PRODUCT_ID = P.PRODUCT_ID
                ORDER BY S.SUPPLIER_ID
            """
            params = ()
        else:
            query = """
                SELECT S.SUPPLIER_ID, S.SUPPLIER_NAME, S.ADDRESS, S.LOCATION,
                       P.PRODUCT_NAME
                FROM SUPPLIER S
                LEFT JOIN PRODUCTS P ON S.PRODUCT_ID = P.PRODUCT_ID
                WHERE S.PRODUCT_ID = %s
                ORDER BY S.SUPPLIER_ID
            """
            params = (product_id,)

        data = db.execute(query, params, fetch=True)

        if data:
            self.supplier_table.setRowCount(len(data))
            for row, s in enumerate(data):
                values = [
                    s["SUPPLIER_ID"], s["SUPPLIER_NAME"], s["ADDRESS"] or "-",
                    s["LOCATION"], s["PRODUCT_NAME"] or "-", ""
                ]
                for col, value in enumerate(values):
                    self.supplier_table.setItem(row, col, QTableWidgetItem(str(value)))
        else:
            self.supplier_table.setRowCount(0)

    # ========================================================
    # SUPPLIER DIALOG
    # ========================================================

    def supplier_dialog(self, supplier=None):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Supplier" if supplier else "Add Supplier")
        dialog.setMinimumWidth(450)

        form = QFormLayout(dialog)
        form.setContentsMargins(30, 30, 30, 30)
        form.setSpacing(12)

        name = QLineEdit()
        address = QLineEdit()
        location = QLineEdit()

        product = QComboBox()
        product.addItem("None", None)
        products = db.execute("SELECT PRODUCT_ID, PRODUCT_NAME FROM PRODUCTS ORDER BY PRODUCT_NAME", fetch=True)
        if products:
            for p in products:
                product.addItem(p["PRODUCT_NAME"], p["PRODUCT_ID"])

        if supplier:
            name.setText(supplier["SUPPLIER_NAME"])
            address.setText(supplier["ADDRESS"] or "")
            location.setText(supplier["LOCATION"])
            if supplier.get("PRODUCT_ID"):
                idx = product.findData(supplier["PRODUCT_ID"])
                if idx >= 0:
                    product.setCurrentIndex(idx)

        form.addRow("Supplier Name", name)
        form.addRow("Address", address)
        form.addRow("Location", location)
        form.addRow("Product", product)

        buttons = QHBoxLayout()
        save = QPushButton("SAVE")
        save.setObjectName("primary")
        cancel = QPushButton("CANCEL")
        cancel.setObjectName("secondary")
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        form.addRow(buttons)

        cancel.clicked.connect(dialog.reject)

        def save_supplier():
            if not name.text().strip():
                QMessageBox.warning(dialog, "Validation", "Supplier name is required.")
                return
            if not location.text().strip():
                QMessageBox.warning(dialog, "Validation", "Location is required.")
                return

            product_id = product.currentData()

            if supplier:
                query = """
                    UPDATE SUPPLIER
                    SET SUPPLIER_NAME=%s, ADDRESS=%s, LOCATION=%s, PRODUCT_ID=%s
                    WHERE SUPPLIER_ID=%s
                """
                params = (
                    name.text().strip(), address.text().strip(), location.text().strip(),
                    product_id, supplier["SUPPLIER_ID"]
                )
            else:
                query = """
                    INSERT INTO SUPPLIER (SUPPLIER_NAME, ADDRESS, LOCATION, PRODUCT_ID)
                    VALUES (%s,%s,%s,%s)
                """
                params = (
                    name.text().strip(), address.text().strip(), location.text().strip(),
                    product_id
                )

            result = db.execute(query, params)
            if result:
                dialog.accept()
            else:
                QMessageBox.critical(dialog, "Database Error", "Unable to save supplier.")

        save.clicked.connect(save_supplier)
        return dialog

    def add_supplier(self):
        dialog = self.supplier_dialog()
        if dialog.exec_():
            self.load_suppliers()
            QMessageBox.information(self, "Success", "Supplier added successfully.")

    def edit_supplier(self):
        rows = self.supplier_table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.warning(self, "Edit Supplier", "Please select a supplier.")
            return

        s_id = int(self.supplier_table.item(rows[0].row(), 0).text())
        result = db.execute("SELECT * FROM SUPPLIER WHERE SUPPLIER_ID=%s", (s_id,), fetch=True)
        if not result:
            return

        dialog = self.supplier_dialog(result[0])
        if dialog.exec_():
            self.load_suppliers()
            QMessageBox.information(self, "Success", "Supplier updated successfully.")

    def delete_supplier(self):
        rows = self.supplier_table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.warning(self, "Delete Supplier", "Please select a supplier.")
            return

        s_id = int(self.supplier_table.item(rows[0].row(), 0).text())

        answer = QMessageBox.question(self, "Confirm Delete", "Delete this supplier permanently?",
                                      QMessageBox.Yes | QMessageBox.No)
        if answer != QMessageBox.Yes:
            return

        result = db.execute("DELETE FROM SUPPLIER WHERE SUPPLIER_ID=%s", (s_id,))
        if result:
            self.load_suppliers()
            QMessageBox.information(self, "Deleted", "Supplier deleted successfully.")
        else:
            QMessageBox.critical(self, "Error", "Unable to delete supplier.")

    # ========================================================
    # STOCK IN
    # ========================================================

    def show_stock_in(self):
        self.activate(self.stockin_btn)
        self.set_page_header("Stock In", "Receive products into the warehouse")

        if "stock_in" in self.pages:
            self.refresh_stockin_product_list(preserve_selection=True)
            self.refresh_stockin_table_and_chart()
            self.stack.setCurrentWidget(self.pages["stock_in"])
            return

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)

        tabs = QTabWidget()
        tabs.addTab(self.create_stockin_supplier_tab(), "Stock In from Supplier")
        tabs.addTab(self.create_stockin_transfer_tab(), "Transfer from Warehouse")

        layout.addWidget(tabs)

        history_frame = QFrame()
        history_frame.setObjectName("card")
        history_layout = QVBoxLayout(history_frame)

        history_title = QLabel("Stock In History")
        history_title.setStyleSheet("font-size:16px;font-weight:bold;")

        self.stockin_table = QTableWidget()
        self.stockin_table.setColumnCount(5)
        self.stockin_table.setHorizontalHeaderLabels([
            "Product", "Quantity", "Unit Price", "Source", ""
        ])
        self.stockin_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.stockin_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        stockin_export_btn = QPushButton("📥 Export")
        stockin_export_btn.setObjectName("secondary")
        stockin_export_btn.clicked.connect(lambda: self.export_table_to_csv(self.stockin_table, "Stock In History"))

        history_layout.addWidget(history_title)
        history_layout.addWidget(self.stockin_table)
        history_layout.addWidget(stockin_export_btn)

        layout.addWidget(history_frame)

        self.goto_page("stock_in", page)

        self.refresh_stockin_product_list(preserve_selection=False)
        self.refresh_stockin_table_and_chart()

    def populate_stockin_warehouses(self, category=None):
        self.stockin_warehouse.clear()
        self.stockin_warehouse.addItem("-- Select Warehouse --", None)

        if category:
            warehouses = self.get_warehouses_for_category(category)
        else:
            warehouses = db.execute("SELECT WAREHOUSE_ID, WAREHOUSE_NAME, LOCATION FROM WAREHOUSE ORDER BY WAREHOUSE_NAME", fetch=True)

        if warehouses:
            for w in warehouses:
                self.stockin_warehouse.addItem(f"{w['WAREHOUSE_NAME']} ({w['LOCATION']})", w["WAREHOUSE_ID"])

    def populate_stockin_bins(self, warehouse_id, category=None):
        self.stockin_bin.clear()
        self.stockin_bin.addItem("-- Select Bin --", None)
        if warehouse_id:
            if category:
                bins = self.get_bins_for_category(warehouse_id, category)
            else:
                bins = db.execute(
                    "SELECT BIN_ID, BIN_NAME, CAPACITY FROM BIN_LOCATION WHERE WAREHOUSE_ID=%s ORDER BY BIN_NAME",
                    (warehouse_id,),
                    fetch=True
                )
            if bins:
                for b in bins:
                    self.stockin_bin.addItem(
                        f"{b['BIN_NAME']} (Cap: {b['CAPACITY']})",
                        b["BIN_ID"]
                    )

    def refresh_all_stock_views(self):
        if "stock_out" in self.pages:
            self.refresh_stockout_product_list(preserve_selection=True)
            self.refresh_stockout_table_and_chart()
        if hasattr(self, "transfer_product"):
            self.populate_transfer_products()
        if hasattr(self, "transfer_chart_axis"):
            self.refresh_transfer_chart()
        if "warehouse" in self.pages:
            self.load_warehouse_data()
        if "products" in self.pages:
            self.load_products()
        if "dashboard" in self.pages:
            self.refresh_dashboard()
        if "transactions" in self.pages:
            self.load_transactions()

    def create_stockin_supplier_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        top_section = QHBoxLayout()
        top_section.setSpacing(15)

        form_frame = QFrame()
        form_frame.setObjectName("card")
        form = QFormLayout(form_frame)
        form.setContentsMargins(25, 25, 25, 25)
        form.setSpacing(12)

        self.stockin_product = QComboBox()
        self.stockin_product.currentIndexChanged.connect(self.on_stockin_product_change)

        self.stockin_supplier = QComboBox()
        self.stockin_supplier.addItem("Select supplier...", None)

        self.stockin_warehouse = QComboBox()
        self.populate_stockin_warehouses()
        self.stockin_warehouse.currentIndexChanged.connect(self.on_stockin_warehouse_change)

        self.stockin_bin = QComboBox()
        self.stockin_bin.addItem("-- Select Bin --", None)

        self.stockin_quantity = QSpinBox()
        self.stockin_quantity.setMinimum(1)
        self.stockin_quantity.setMaximum(999999)

        self.stockin_price = QDoubleSpinBox()
        self.stockin_price.setMaximum(99999999)
        self.stockin_price.setDecimals(2)
        self.stockin_price.setPrefix("₹ ")

        save = QPushButton("ADD STOCK")
        save.setObjectName("primary")

        form.addRow("Product", self.stockin_product)
        form.addRow("Supplier", self.stockin_supplier)
        form.addRow("Warehouse", self.stockin_warehouse)
        form.addRow("Bin Location", self.stockin_bin)
        form.addRow("Quantity", self.stockin_quantity)
        form.addRow("Unit Price", self.stockin_price)
        form.addRow("", save)

        top_section.addWidget(form_frame, 1)

        chart_frame = QFrame()
        chart_frame.setObjectName("card")
        chart_frame.setMinimumWidth(400)
        chart_frame.setMinimumHeight(320)
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(10, 10, 10, 10)

        self.stockin_canvas, self.stockin_figure, self.stockin_axis = self.make_chart_canvas(320, 6)
        chart_layout.addWidget(self.stockin_canvas)

        top_section.addWidget(chart_frame, 1)

        layout.addLayout(top_section)

        def add_supplier_stock():
            if self.stockin_product.count() == 0:
                QMessageBox.warning(self, "Stock In", "No products available.")
                return

            product_id = self.stockin_product.currentData()
            supplier_id = self.stockin_supplier.currentData()
            warehouse_id = self.stockin_warehouse.currentData()
            bin_id = self.stockin_bin.currentData()
            qty = self.stockin_quantity.value()
            unit_price = self.stockin_price.value()

            if not product_id:
                QMessageBox.warning(self, "Stock In", "Please select a product.")
                return

            if not supplier_id:
                QMessageBox.warning(self, "Stock In", "Please select a supplier.")
                return

            if not warehouse_id:
                QMessageBox.warning(self, "Stock In", "Please select a warehouse.")
                return

            if not bin_id:
                QMessageBox.warning(self, "Stock In", "Please select a bin location.")
                return

            can_add_wh, wh_capacity, wh_current, wh_msg = self.check_warehouse_capacity(warehouse_id, qty)
            if not can_add_wh:
                QMessageBox.warning(self, "Warehouse Capacity Exceeded", wh_msg)
                return

            can_add_bin, bin_capacity, bin_current, bin_msg = self.check_bin_capacity(bin_id, qty)
            if not can_add_bin:
                QMessageBox.warning(self, "Bin Capacity Exceeded", bin_msg)
                return

            update_result = db.execute(
                """
                INSERT INTO PRODUCT_WAREHOUSE_STOCK (PRODUCT_ID, WAREHOUSE_ID, BIN_ID, STOCK_QTY)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE STOCK_QTY = STOCK_QTY + VALUES(STOCK_QTY)
                """,
                (product_id, warehouse_id, bin_id, qty)
            )

            if not update_result:
                QMessageBox.critical(self, "Error", "Unable to update stock.")
                return

            db.execute(
                """
                INSERT INTO STOCK_TRANSACTIONS
                (PRODUCT_ID, USER_ID, TRANSACTION_TYPE, QUANTITY, UNIT_PRICE,
                 TOTAL_VALUE, SOURCE_TYPE, SOURCE_SUPPLIER_ID,
                 DESTINATION_TYPE, DESTINATION_WAREHOUSE_ID)
                VALUES (%s,%s,'STOCK IN',%s,%s,%s,'SUPPLIER',%s,'WAREHOUSE',%s)
                """,
                (
                    product_id, self.user["USER_ID"], qty, unit_price,
                    qty * unit_price, supplier_id, warehouse_id
                )
            )

            QMessageBox.information(self, "Success", 
                f"Stock added successfully.\n"
                f"Warehouse: {wh_current + qty} / {wh_capacity} units\n"
                f"Bin: {bin_current + qty} / {bin_capacity} units"
            )

            self.stockin_quantity.setValue(1)
            self.stockin_price.setValue(0)

            self.refresh_stockin_product_list(preserve_selection=False)
            self.refresh_stockin_table_and_chart()
            self.refresh_all_stock_views()

        save.clicked.connect(add_supplier_stock)
        return tab

    def on_stockin_warehouse_change(self):
        wh_id = self.stockin_warehouse.currentData()
        category = getattr(self, "stockin_selected_category", None)
        self.populate_stockin_bins(wh_id, category)

    def on_stockin_product_change(self):
        product_id = self.stockin_product.currentData()
        if not product_id:
            self.stockin_selected_category = None
            self.stockin_supplier.clear()
            self.stockin_supplier.addItem("Select supplier...", None)
            self.populate_stockin_warehouses()
            return

        suppliers = db.execute(
            """
            SELECT SUPPLIER_ID, SUPPLIER_NAME
            FROM SUPPLIER
            WHERE PRODUCT_ID=%s
            """,
            (product_id,),
            fetch=True
        )

        self.stockin_supplier.clear()
        self.stockin_supplier.addItem("Select supplier...", None)

        if suppliers:
            for s in suppliers:
                self.stockin_supplier.addItem(s["SUPPLIER_NAME"], s["SUPPLIER_ID"])

        category = db.scalar("SELECT CATEGORY FROM PRODUCTS WHERE PRODUCT_ID=%s", (product_id,))
        self.stockin_selected_category = category
        self.populate_stockin_warehouses(category)

    def refresh_stockin_product_list(self, preserve_selection=True):
        current_id = self.stockin_product.currentData() if preserve_selection else None

        self.stockin_product.blockSignals(True)
        self.stockin_product.clear()
        self.stockin_product.addItem("-- Select Product --", None)

        products = db.execute(
            """
            SELECT PRODUCT_ID, PRODUCT_NAME
            FROM PRODUCTS
            ORDER BY PRODUCT_NAME
            """,
            fetch=True
        )

        restore_index = -1
        if products:
            for p in products:
                self.stockin_product.addItem(p["PRODUCT_NAME"], p["PRODUCT_ID"])
                if current_id is not None and p["PRODUCT_ID"] == current_id:
                    restore_index = self.stockin_product.count() - 1

        if restore_index >= 0:
            self.stockin_product.setCurrentIndex(restore_index)

        self.stockin_product.blockSignals(False)

    def refresh_stockin_table_and_chart(self):
        if not hasattr(self, "stockin_table"):
            return
        data = db.execute(
            """
            SELECT P.PRODUCT_NAME, T.QUANTITY, T.UNIT_PRICE,
                   T.SOURCE_TYPE, T.DESTINATION_TYPE,
                   CASE
                       WHEN T.SOURCE_TYPE = 'SUPPLIER' THEN CONCAT('Supplier: ', S.SUPPLIER_NAME)
                       WHEN T.SOURCE_TYPE = 'WAREHOUSE' THEN CONCAT('Warehouse: ', W.WAREHOUSE_NAME)
                       ELSE 'N/A'
                   END AS SOURCE
            FROM STOCK_TRANSACTIONS T
            JOIN PRODUCTS P ON P.PRODUCT_ID = T.PRODUCT_ID
            LEFT JOIN SUPPLIER S ON S.SUPPLIER_ID = T.SOURCE_SUPPLIER_ID
            LEFT JOIN WAREHOUSE W ON W.WAREHOUSE_ID = T.SOURCE_WAREHOUSE_ID
            WHERE T.TRANSACTION_TYPE = 'STOCK IN'
            ORDER BY T.TRANSACTION_ID DESC
            LIMIT 50
            """,
            fetch=True
        )

        if data:
            self.stockin_table.setRowCount(len(data))
            for row, item in enumerate(data):
                color = QColor(255, 255, 255)
                if item["SOURCE_TYPE"] == 'SUPPLIER':
                    color = QColor(200, 255, 200)
                elif item["SOURCE_TYPE"] == 'WAREHOUSE':
                    color = QColor(200, 200, 255)
                
                values = [
                    item["PRODUCT_NAME"], item["QUANTITY"],
                    "₹{:,.2f}".format(item["UNIT_PRICE"]),
                    item["SOURCE"] or "-",
                    ""
                ]
                for col, value in enumerate(values):
                    cell = QTableWidgetItem(str(value))
                    cell.setBackground(color)
                    self.stockin_table.setItem(row, col, cell)
        else:
            self.stockin_table.setRowCount(0)

        top = db.execute(
            """
            SELECT P.PRODUCT_NAME AS NAME, SUM(T.QUANTITY) AS TOTAL_QTY
            FROM STOCK_TRANSACTIONS T
            JOIN PRODUCTS P ON P.PRODUCT_ID = T.PRODUCT_ID
            WHERE T.TRANSACTION_TYPE = 'STOCK IN' AND T.SOURCE_TYPE = 'SUPPLIER'
            GROUP BY P.PRODUCT_NAME
            ORDER BY TOTAL_QTY DESC
            LIMIT 6
            """,
            fetch=True
        )

        if top:
            categories = [row["NAME"] for row in top]
            values = [row["TOTAL_QTY"] for row in top]
            self.draw_donut_chart(
                self.stockin_axis, self.stockin_figure, self.stockin_canvas,
                values, categories, "Stock Received from Suppliers"
            )

    # ========================================================
    # STOCK OUT
    # ========================================================

    def show_stock_out(self):
        self.activate(self.stockout_btn)
        self.set_page_header("Stock Out", "Issue products from inventory")

        if "stock_out" in self.pages:
            self.refresh_stockout_product_list(preserve_selection=True)
            self.refresh_stockout_table_and_chart()
            self.stack.setCurrentWidget(self.pages["stock_out"])
            return

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)

        top_section = QHBoxLayout()
        top_section.setSpacing(15)

        form_frame = QFrame()
        form_frame.setObjectName("card")
        form = QFormLayout(form_frame)
        form.setContentsMargins(25, 25, 25, 25)
        form.setSpacing(12)

        self.stockout_product = QComboBox()
        self.stockout_product.currentIndexChanged.connect(self.on_stockout_product_change)

        self.stockout_warehouse = QComboBox()
        self.stockout_warehouse.addItem("-- Select Warehouse --", None)

        self.stockout_bin = QComboBox()
        self.stockout_bin.addItem("-- Select Bin --", None)
        self.stockout_warehouse.currentIndexChanged.connect(self.on_stockout_warehouse_change)

        self.stockout_quantity = QSpinBox()
        self.stockout_quantity.setMinimum(1)
        self.stockout_quantity.setMaximum(999999)

        save = QPushButton("REMOVE STOCK")
        save.setObjectName("danger")

        form.addRow("Product", self.stockout_product)
        form.addRow("Warehouse", self.stockout_warehouse)
        form.addRow("Bin Location", self.stockout_bin)
        form.addRow("Quantity", self.stockout_quantity)
        form.addRow("", save)

        top_section.addWidget(form_frame, 1)

        chart_frame = QFrame()
        chart_frame.setObjectName("card")
        chart_frame.setMinimumWidth(400)
        chart_frame.setMinimumHeight(320)
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(10, 10, 10, 10)

        self.stockout_canvas, self.stockout_figure, self.stockout_axis = self.make_chart_canvas(320, 6)
        chart_layout.addWidget(self.stockout_canvas)

        top_section.addWidget(chart_frame, 1)

        layout.addLayout(top_section)

        history_frame = QFrame()
        history_frame.setObjectName("card")
        history_layout = QVBoxLayout(history_frame)

        history_title = QLabel("Stock Out History")
        history_title.setStyleSheet("font-size:16px;font-weight:bold;")

        self.stockout_table = QTableWidget()
        self.stockout_table.setColumnCount(6)
        self.stockout_table.setHorizontalHeaderLabels([
            "Product", "Warehouse", "Quantity", "Unit Price", "Destination", ""
        ])
        self.stockout_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.stockout_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        stockout_export_btn = QPushButton("📥 Export")
        stockout_export_btn.setObjectName("secondary")
        stockout_export_btn.clicked.connect(lambda: self.export_table_to_csv(self.stockout_table, "Stock Out History"))

        history_layout.addWidget(history_title)
        history_layout.addWidget(self.stockout_table)
        history_layout.addWidget(stockout_export_btn)

        layout.addWidget(history_frame)

        def remove_stock():
            if self.stockout_product.count() == 0:
                QMessageBox.warning(self, "Stock Out", "No stock is currently available.")
                return

            product_data = self.stockout_product.currentData()
            if not product_data:
                QMessageBox.warning(self, "Stock Out", "Please select a product.")
                return

            warehouse_data = self.stockout_warehouse.currentData()
            if not warehouse_data:
                QMessageBox.warning(self, "Stock Out", "Please select a warehouse.")
                return

            bin_data = self.stockout_bin.currentData()
            if not bin_data:
                QMessageBox.warning(self, "Stock Out", "Please select a bin location.")
                return

            product_id = product_data["PRODUCT_ID"]
            warehouse_id = warehouse_data["WAREHOUSE_ID"]
            bin_id = bin_data["BIN_ID"]
            
            # Get available stock for this product in this bin
            stock_info = db.execute(
                """
                SELECT STOCK_QTY 
                FROM PRODUCT_WAREHOUSE_STOCK 
                WHERE PRODUCT_ID=%s AND WAREHOUSE_ID=%s AND BIN_ID=%s
                """,
                (product_id, warehouse_id, bin_id),
                fetch=True
            )
            
            if not stock_info:
                QMessageBox.warning(self, "Stock Out", "No stock found for this product in the selected bin.")
                return
                
            available = stock_info[0]["STOCK_QTY"]
            unit_price = float(product_data["UNIT_PRICE"])
            qty = self.stockout_quantity.value()

            if qty > available:
                QMessageBox.warning(self, "Insufficient Stock", f"Only {available} units are available in this bin.")
                return

            update_result = db.execute(
                """
                UPDATE PRODUCT_WAREHOUSE_STOCK
                SET STOCK_QTY = STOCK_QTY - %s
                WHERE PRODUCT_ID=%s AND WAREHOUSE_ID=%s AND BIN_ID=%s
                """,
                (qty, product_id, warehouse_id, bin_id)
            )

            if not update_result:
                QMessageBox.critical(self, "Error", "Unable to update stock.")
                return

            db.execute(
                """
                INSERT INTO STOCK_TRANSACTIONS
                (PRODUCT_ID, USER_ID, TRANSACTION_TYPE, QUANTITY, UNIT_PRICE,
                 TOTAL_VALUE, SOURCE_TYPE, SOURCE_WAREHOUSE_ID, DESTINATION_TYPE)
                VALUES (%s,%s,'STOCK OUT',%s,%s,%s,'WAREHOUSE',%s,'CUSTOMER')
                """,
                (
                    product_id, self.user["USER_ID"], qty, unit_price,
                    qty * unit_price, warehouse_id
                )
            )

            QMessageBox.information(self, "Success", "Stock removed successfully.")
            self.stockout_quantity.setValue(1)

            self.refresh_stockout_product_list(preserve_selection=False)
            self.refresh_stockout_table_and_chart()
            self.refresh_all_stock_views()

        save.clicked.connect(remove_stock)

        self.goto_page("stock_out", page)

        self.refresh_stockout_product_list(preserve_selection=False)
        self.refresh_stockout_table_and_chart()

    def on_stockout_warehouse_change(self):
        """Populate bins when warehouse changes in Stock Out"""
        warehouse_data = self.stockout_warehouse.currentData()
        if warehouse_data:
            wh_id = warehouse_data["WAREHOUSE_ID"]
            product_data = self.stockout_product.currentData()
            if product_data:
                self.populate_stockout_bins(wh_id, product_data["PRODUCT_ID"])
            else:
                self.populate_stockout_bins(wh_id, None)
        else:
            self.stockout_bin.clear()
            self.stockout_bin.addItem("-- Select Bin --", None)

    def populate_stockout_bins(self, warehouse_id, product_id=None):
        """Populate bins that have stock for a specific product"""
        self.stockout_bin.clear()
        self.stockout_bin.addItem("-- Select Bin --", None)
        
        if warehouse_id and product_id:
            bins = db.execute(
                """
                SELECT B.BIN_ID, B.BIN_NAME, PWS.STOCK_QTY
                FROM BIN_LOCATION B
                JOIN PRODUCT_WAREHOUSE_STOCK PWS ON PWS.BIN_ID = B.BIN_ID
                WHERE B.WAREHOUSE_ID = %s AND PWS.PRODUCT_ID = %s AND PWS.STOCK_QTY > 0
                ORDER BY B.BIN_NAME
                """,
                (warehouse_id, product_id),
                fetch=True
            )
            if bins:
                for b in bins:
                    self.stockout_bin.addItem(
                        f"{b['BIN_NAME']} (Stock: {b['STOCK_QTY']})",
                        {"BIN_ID": b["BIN_ID"], "BIN_NAME": b["BIN_NAME"]}
                    )

    def on_stockout_product_change(self):
        """Refresh warehouses and bins when product changes in Stock Out"""
        self.refresh_stockout_warehouses()

    def refresh_stockout_warehouses(self, preserve_selection=True):
        """Refresh warehouse dropdown with stock availability for selected product"""
        if not hasattr(self, "stockout_warehouse"):
            return

        current_wh_id = None
        current_data = self.stockout_warehouse.currentData()
        if preserve_selection and current_data:
            current_wh_id = current_data["WAREHOUSE_ID"]

        self.stockout_warehouse.blockSignals(True)
        self.stockout_warehouse.clear()
        self.stockout_warehouse.addItem("-- Select Warehouse --", None)

        product_data = self.stockout_product.currentData()
        if not product_data:
            self.stockout_warehouse.blockSignals(False)
            return

        rows = db.execute(
            """
            SELECT DISTINCT PWS.WAREHOUSE_ID, W.WAREHOUSE_NAME, W.LOCATION,
                   COALESCE(SUM(PWS.STOCK_QTY), 0) AS TOTAL_STOCK
            FROM PRODUCT_WAREHOUSE_STOCK PWS
            JOIN WAREHOUSE W ON W.WAREHOUSE_ID = PWS.WAREHOUSE_ID
            WHERE PWS.PRODUCT_ID = %s AND PWS.STOCK_QTY > 0
            GROUP BY PWS.WAREHOUSE_ID, W.WAREHOUSE_NAME, W.LOCATION
            ORDER BY W.WAREHOUSE_NAME
            """,
            (product_data["PRODUCT_ID"],),
            fetch=True
        )

        restore_index = -1
        if rows:
            for idx, r in enumerate(rows):
                self.stockout_warehouse.addItem(
                    f'{r["WAREHOUSE_NAME"]} ({r["LOCATION"]}) - Stock: {r["TOTAL_STOCK"]}',
                    {"WAREHOUSE_ID": r["WAREHOUSE_ID"], "STOCK_QTY": r["TOTAL_STOCK"]}
                )
                if current_wh_id is not None and r["WAREHOUSE_ID"] == current_wh_id:
                    restore_index = idx + 1

        if restore_index >= 0:
            self.stockout_warehouse.setCurrentIndex(restore_index)

        self.stockout_warehouse.blockSignals(False)

    def refresh_stockout_product_list(self, preserve_selection=True):
        """Refresh product list with stock availability"""
        current_id = None
        current_data = self.stockout_product.currentData()
        if preserve_selection and current_data:
            current_id = current_data["PRODUCT_ID"]

        self.stockout_product.blockSignals(True)
        self.stockout_product.clear()
        self.stockout_product.addItem("-- Select Product --", None)

        products = db.execute(
            """
            SELECT DISTINCT P.PRODUCT_ID, P.PRODUCT_NAME, P.UNIT_PRICE,
                   COALESCE(SUM(PWS.STOCK_QTY), 0) AS STOCK_QTY
            FROM PRODUCTS P
            JOIN PRODUCT_WAREHOUSE_STOCK PWS ON PWS.PRODUCT_ID = P.PRODUCT_ID
            GROUP BY P.PRODUCT_ID, P.PRODUCT_NAME, P.UNIT_PRICE
            HAVING STOCK_QTY > 0
            ORDER BY P.PRODUCT_NAME
            """,
            fetch=True
        )

        restore_index = -1
        if products:
            for p in products:
                self.stockout_product.addItem(
                    f'{p["PRODUCT_NAME"]} (Available: {p["STOCK_QTY"]})',
                    p
                )
                if current_id is not None and p["PRODUCT_ID"] == current_id:
                    restore_index = self.stockout_product.count() - 1

        if restore_index >= 0:
            self.stockout_product.setCurrentIndex(restore_index)

        self.stockout_product.blockSignals(False)
        self.refresh_stockout_warehouses(preserve_selection=preserve_selection)

    def refresh_stockout_table_and_chart(self):
        if not hasattr(self, "stockout_table"):
            return
        data = db.execute(
            """
            SELECT P.PRODUCT_NAME, T.QUANTITY, T.UNIT_PRICE,
                   T.DESTINATION_TYPE, COALESCE(W.WAREHOUSE_NAME, '-') AS WAREHOUSE_NAME,
                   CASE
                       WHEN T.DESTINATION_TYPE = 'CUSTOMER' THEN 'Customer'
                       WHEN T.DESTINATION_TYPE = 'WAREHOUSE' THEN 'Warehouse'
                       ELSE 'N/A'
                   END AS DESTINATION
            FROM STOCK_TRANSACTIONS T
            JOIN PRODUCTS P ON P.PRODUCT_ID = T.PRODUCT_ID
            LEFT JOIN WAREHOUSE W ON W.WAREHOUSE_ID = T.SOURCE_WAREHOUSE_ID
            WHERE T.TRANSACTION_TYPE = 'STOCK OUT'
            ORDER BY T.TRANSACTION_ID DESC
            LIMIT 50
            """,
            fetch=True
        )

        if data:
            self.stockout_table.setRowCount(len(data))
            for row, item in enumerate(data):
                color = QColor(255, 255, 255)
                if item["DESTINATION_TYPE"] == 'CUSTOMER':
                    color = QColor(255, 200, 200)
                elif item["DESTINATION_TYPE"] == 'WAREHOUSE':
                    color = QColor(255, 255, 200)
                
                values = [
                    item["PRODUCT_NAME"], item["WAREHOUSE_NAME"], item["QUANTITY"],
                    "₹{:,.2f}".format(item["UNIT_PRICE"]),
                    item["DESTINATION"],
                    ""
                ]
                for col, value in enumerate(values):
                    cell = QTableWidgetItem(str(value))
                    cell.setBackground(color)
                    self.stockout_table.setItem(row, col, cell)
        else:
            self.stockout_table.setRowCount(0)

        top = db.execute(
            """
            SELECT P.PRODUCT_NAME AS NAME, SUM(T.QUANTITY) AS TOTAL_QTY
            FROM STOCK_TRANSACTIONS T
            JOIN PRODUCTS P ON P.PRODUCT_ID = T.PRODUCT_ID
            WHERE T.TRANSACTION_TYPE = 'STOCK OUT' AND T.DESTINATION_TYPE = 'CUSTOMER'
            GROUP BY P.PRODUCT_NAME
            ORDER BY TOTAL_QTY DESC
            LIMIT 6
            """,
            fetch=True
        )

        if top:
            categories = [row["NAME"] for row in top]
            values = [row["TOTAL_QTY"] for row in top]
            self.draw_donut_chart(
                self.stockout_axis, self.stockout_figure, self.stockout_canvas,
                values, categories, "Top Products Issued"
            )

    # ========================================================
    # STOCK IN TRANSFER TAB
    # ========================================================

    def create_stockin_transfer_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        top_section = QHBoxLayout()
        top_section.setSpacing(15)

        form_frame = QFrame()
        form_frame.setObjectName("card")
        form = QFormLayout(form_frame)
        form.setContentsMargins(25, 25, 25, 25)
        form.setSpacing(12)

        self.transfer_product = QComboBox()
        self.transfer_product.currentIndexChanged.connect(self.on_transfer_product_change)

        self.transfer_from_warehouse = QComboBox()
        self.transfer_from_warehouse.addItem("-- Select Warehouse --", None)
        self.transfer_from_warehouse.currentIndexChanged.connect(self.populate_transfer_from_bins)

        self.transfer_from_bin = QComboBox()
        self.transfer_from_bin.addItem("-- Select Bin --", None)

        self.transfer_to_warehouse = QComboBox()
        self.transfer_to_warehouse.addItem("-- Select Warehouse --", None)
        self.transfer_to_warehouse.currentIndexChanged.connect(self.populate_transfer_to_bins)

        self.transfer_to_bin = QComboBox()
        self.transfer_to_bin.addItem("-- Select Bin --", None)

        self.transfer_quantity = QSpinBox()
        self.transfer_quantity.setMinimum(1)
        self.transfer_quantity.setMaximum(999999)

        save = QPushButton("TRANSFER STOCK")
        save.setObjectName("primary")

        form.addRow("Product", self.transfer_product)
        form.addRow("From Warehouse", self.transfer_from_warehouse)
        form.addRow("From Bin", self.transfer_from_bin)
        form.addRow("To Warehouse", self.transfer_to_warehouse)
        form.addRow("To Bin", self.transfer_to_bin)
        form.addRow("Quantity", self.transfer_quantity)
        form.addRow("", save)

        top_section.addWidget(form_frame, 1)

        chart_frame = QFrame()
        chart_frame.setObjectName("card")
        chart_frame.setMinimumWidth(400)
        chart_frame.setMinimumHeight(320)
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(10, 10, 10, 10)

        self.transfer_chart_canvas, self.transfer_chart_figure, self.transfer_chart_axis = self.make_chart_canvas(320, 6)
        chart_layout.addWidget(self.transfer_chart_canvas)

        self.refresh_transfer_chart()

        top_section.addWidget(chart_frame, 1)

        layout.addLayout(top_section)

        self.populate_transfer_products()

        def add_transfer_stock():
            if self.transfer_product.count() == 0:
                QMessageBox.warning(self, "Transfer", "No products available.")
                return

            product_data = self.transfer_product.currentData()
            if not product_data:
                QMessageBox.warning(self, "Transfer", "Please select a product.")
                return
                
            from_wh_id = self.transfer_from_warehouse.currentData()
            from_bin_id = self.transfer_from_bin.currentData()
            to_wh_id = self.transfer_to_warehouse.currentData()
            to_bin_id = self.transfer_to_bin.currentData()
            qty = self.transfer_quantity.value()

            if not from_wh_id or not to_wh_id:
                QMessageBox.warning(self, "Transfer", "Please select both source and destination warehouses.")
                return

            if from_wh_id == to_wh_id:
                QMessageBox.warning(self, "Transfer", "Source and destination warehouses must be different.")
                return

            if not from_bin_id or not to_bin_id:
                QMessageBox.warning(self, "Transfer", "Please select both source and destination bins.")
                return

            # Get available stock in source bin
            stock_info = db.execute(
                """
                SELECT STOCK_QTY 
                FROM PRODUCT_WAREHOUSE_STOCK 
                WHERE PRODUCT_ID=%s AND WAREHOUSE_ID=%s AND BIN_ID=%s
                """,
                (product_data["PRODUCT_ID"], from_wh_id, from_bin_id),
                fetch=True
            )
            
            if not stock_info or stock_info[0]["STOCK_QTY"] < qty:
                available = stock_info[0]["STOCK_QTY"] if stock_info else 0
                QMessageBox.warning(
                    self,
                    "Insufficient Stock",
                    f"Only {available} units available in the source bin."
                )
                return

            can_add_wh, wh_capacity, wh_current, wh_msg = self.check_warehouse_capacity(to_wh_id, qty)
            if not can_add_wh:
                QMessageBox.warning(self, "Warehouse Capacity Exceeded", wh_msg)
                return

            can_add_bin, bin_capacity, bin_current, bin_msg = self.check_bin_capacity(to_bin_id, qty)
            if not can_add_bin:
                QMessageBox.warning(self, "Bin Capacity Exceeded", bin_msg)
                return

            product_id = product_data["PRODUCT_ID"]

            update_result = db.execute(
                """
                UPDATE PRODUCT_WAREHOUSE_STOCK
                SET STOCK_QTY = STOCK_QTY - %s
                WHERE PRODUCT_ID=%s AND WAREHOUSE_ID=%s AND BIN_ID=%s
                """,
                (qty, product_id, from_wh_id, from_bin_id)
            )

            if not update_result:
                QMessageBox.critical(self, "Error", "Unable to remove stock from source.")
                return

            db.execute(
                """
                INSERT INTO PRODUCT_WAREHOUSE_STOCK (PRODUCT_ID, WAREHOUSE_ID, BIN_ID, STOCK_QTY)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE STOCK_QTY = STOCK_QTY + VALUES(STOCK_QTY)
                """,
                (product_id, to_wh_id, to_bin_id, qty)
            )

            db.execute(
                """
                INSERT INTO STOCK_TRANSACTIONS
                (PRODUCT_ID, USER_ID, TRANSACTION_TYPE, QUANTITY, UNIT_PRICE,
                 TOTAL_VALUE, SOURCE_TYPE, SOURCE_WAREHOUSE_ID,
                 DESTINATION_TYPE, DESTINATION_WAREHOUSE_ID)
                VALUES (%s,%s,'STOCK OUT',%s,%s,%s,'WAREHOUSE',%s,'WAREHOUSE',%s)
                """,
                (
                    product_id, self.user["USER_ID"], qty,
                    product_data["UNIT_PRICE"], qty * product_data["UNIT_PRICE"],
                    from_wh_id, to_wh_id
                )
            )

            db.execute(
                """
                INSERT INTO STOCK_TRANSACTIONS
                (PRODUCT_ID, USER_ID, TRANSACTION_TYPE, QUANTITY, UNIT_PRICE,
                 TOTAL_VALUE, SOURCE_TYPE, SOURCE_WAREHOUSE_ID,
                 DESTINATION_TYPE, DESTINATION_WAREHOUSE_ID)
                VALUES (%s,%s,'STOCK IN',%s,%s,%s,'WAREHOUSE',%s,'WAREHOUSE',%s)
                """,
                (
                    product_id, self.user["USER_ID"], qty,
                    product_data["UNIT_PRICE"], qty * product_data["UNIT_PRICE"],
                    from_wh_id, to_wh_id
                )
            )

            QMessageBox.information(self, "Success", 
                f"Stock transferred successfully.\n"
                f"Destination warehouse: {wh_current + qty} / {wh_capacity} units\n"
                f"Destination bin: {bin_current + qty} / {bin_capacity} units"
            )
            self.transfer_quantity.setValue(1)

            self.populate_transfer_products()
            self.refresh_stockin_table_and_chart()
            self.refresh_stockout_table_and_chart()
            self.refresh_transfer_chart()
            if "warehouse" in self.pages:
                self.load_warehouse_data()

        save.clicked.connect(add_transfer_stock)
        return tab

    def on_transfer_product_change(self):
        """Handle product change in transfer tab"""
        product_data = self.transfer_product.currentData()
        if product_data:
            self.populate_transfer_from_warehouses(product_data["PRODUCT_ID"])
            self.populate_transfer_to_warehouses(product_data.get("CATEGORY"))

    def populate_transfer_to_warehouses(self, category):
        """Populate destination warehouses for transfer"""
        self.transfer_to_warehouse.clear()
        self.transfer_to_warehouse.addItem("-- Select Warehouse --", None)

        warehouses = db.execute("SELECT WAREHOUSE_ID, WAREHOUSE_NAME, LOCATION FROM WAREHOUSE ORDER BY WAREHOUSE_NAME", fetch=True)
        if warehouses:
            for w in warehouses:
                self.transfer_to_warehouse.addItem(f"{w['WAREHOUSE_NAME']} ({w['LOCATION']})", w["WAREHOUSE_ID"])

    def populate_transfer_from_warehouses(self, product_id):
        """Populate source warehouses that have stock for transfer"""
        self.transfer_from_warehouse.clear()
        self.transfer_from_warehouse.addItem("-- Select Warehouse --", None)
        
        rows = db.execute(
            """
            SELECT DISTINCT PWS.WAREHOUSE_ID, W.WAREHOUSE_NAME, W.LOCATION,
                   COALESCE(SUM(PWS.STOCK_QTY), 0) AS TOTAL_STOCK
            FROM PRODUCT_WAREHOUSE_STOCK PWS
            JOIN WAREHOUSE W ON W.WAREHOUSE_ID = PWS.WAREHOUSE_ID
            WHERE PWS.PRODUCT_ID = %s AND PWS.STOCK_QTY > 0
            GROUP BY PWS.WAREHOUSE_ID, W.WAREHOUSE_NAME, W.LOCATION
            ORDER BY W.WAREHOUSE_NAME
            """,
            (product_id,),
            fetch=True
        )
        
        if rows:
            for r in rows:
                self.transfer_from_warehouse.addItem(
                    f"{r['WAREHOUSE_NAME']} ({r['LOCATION']}) - Stock: {r['TOTAL_STOCK']}", 
                    r["WAREHOUSE_ID"]
                )

    def populate_transfer_from_bins(self):
        """Populate source bins for transfer"""
        wh_id = self.transfer_from_warehouse.currentData()
        self.transfer_from_bin.clear()
        self.transfer_from_bin.addItem("-- Select Bin --", None)
        
        if wh_id:
            product_data = self.transfer_product.currentData()
            if product_data:
                bins = db.execute(
                    """
                    SELECT B.BIN_ID, B.BIN_NAME, PWS.STOCK_QTY
                    FROM BIN_LOCATION B
                    JOIN PRODUCT_WAREHOUSE_STOCK PWS ON PWS.BIN_ID = B.BIN_ID
                    WHERE B.WAREHOUSE_ID = %s AND PWS.PRODUCT_ID = %s AND PWS.STOCK_QTY > 0
                    ORDER BY B.BIN_NAME
                    """,
                    (wh_id, product_data["PRODUCT_ID"]),
                    fetch=True
                )
                if bins:
                    for b in bins:
                        self.transfer_from_bin.addItem(
                            f"{b['BIN_NAME']} (Stock: {b['STOCK_QTY']})",
                            b["BIN_ID"]
                        )

    def populate_transfer_to_bins(self):
        """Populate destination bins for transfer"""
        wh_id = self.transfer_to_warehouse.currentData()
        self.transfer_to_bin.clear()
        self.transfer_to_bin.addItem("-- Select Bin --", None)
        
        if wh_id:
            bins = db.execute(
                """
                SELECT BIN_ID, BIN_NAME, CAPACITY
                FROM BIN_LOCATION
                WHERE WAREHOUSE_ID = %s
                ORDER BY BIN_NAME
                """,
                (wh_id,),
                fetch=True
            )
            if bins:
                for b in bins:
                    self.transfer_to_bin.addItem(
                        f"{b['BIN_NAME']} (Cap: {b['CAPACITY']})",
                        b["BIN_ID"]
                    )

    def populate_transfer_products(self):
        """Populate products with stock for transfer"""
        self.transfer_product.clear()
        self.transfer_product.addItem("-- Select Product --", None)
        products = db.execute(
            """
            SELECT DISTINCT P.PRODUCT_ID, P.PRODUCT_NAME, P.UNIT_PRICE, P.CATEGORY,
                   COALESCE(SUM(PWS.STOCK_QTY), 0) AS STOCK_QTY
            FROM PRODUCT_WAREHOUSE_STOCK PWS
            JOIN PRODUCTS P ON P.PRODUCT_ID = PWS.PRODUCT_ID
            WHERE PWS.STOCK_QTY > 0
            GROUP BY P.PRODUCT_ID, P.PRODUCT_NAME, P.UNIT_PRICE, P.CATEGORY
            ORDER BY P.PRODUCT_NAME
            """,
            fetch=True
        )

        if products:
            for p in products:
                self.transfer_product.addItem(
                    f"{p['PRODUCT_NAME']} (Available: {p['STOCK_QTY']})",
                    p
                )

    def refresh_transfer_chart(self):
        if not hasattr(self, "transfer_chart_axis"):
            return

        top = db.execute(
            """
            SELECT P.PRODUCT_NAME AS NAME, SUM(T.QUANTITY) AS TOTAL_QTY
            FROM STOCK_TRANSACTIONS T
            JOIN PRODUCTS P ON P.PRODUCT_ID = T.PRODUCT_ID
            WHERE T.TRANSACTION_TYPE = 'STOCK OUT'
              AND T.SOURCE_TYPE = 'WAREHOUSE'
              AND T.DESTINATION_TYPE = 'WAREHOUSE'
            GROUP BY P.PRODUCT_NAME
            ORDER BY TOTAL_QTY DESC
            LIMIT 6
            """,
            fetch=True
        )

        if top:
            categories = [row["NAME"] for row in top]
            values = [row["TOTAL_QTY"] for row in top]
            self.draw_donut_chart(
                self.transfer_chart_axis, self.transfer_chart_figure, self.transfer_chart_canvas,
                values, categories, "Most Transferred Products"
            )

    # ========================================================
    # TRANSACTIONS
    # ========================================================

    def show_transactions(self):
        self.activate(self.transactions_btn)
        self.set_page_header("Transactions", "Complete inventory movement history")

        if "transactions" in self.pages:
            self.load_transactions()
            self.stack.setCurrentWidget(self.pages["transactions"])
            return

        page = QWidget()
        layout = QVBoxLayout(page)

        chart_frame = QFrame()
        chart_frame.setObjectName("card")
        chart_layout = QHBoxLayout(chart_frame)
        chart_layout.setContentsMargins(10, 10, 10, 10)

        self.trans_canvas1, self.trans_figure1, self.trans_axis1 = self.make_chart_canvas(220, 5)
        chart_layout.addWidget(self.trans_canvas1)

        self.trans_canvas2, self.trans_figure2, self.trans_axis2 = self.make_chart_canvas(220, 5)
        chart_layout.addWidget(self.trans_canvas2)

        layout.addWidget(chart_frame)

        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(7)
        self.transactions_table.setHorizontalHeaderLabels([
            "ID", "Product", "User", "Type", "Quantity", "Value", ""
        ])
        self.transactions_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.transactions_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        trans_export_layout = QHBoxLayout()
        trans_export_btn = QPushButton("📥 Export Transactions")
        trans_export_btn.setObjectName("secondary")
        trans_export_btn.clicked.connect(lambda: self.export_table_to_csv(self.transactions_table, "Transactions"))
        trans_export_layout.addStretch()
        trans_export_layout.addWidget(trans_export_btn)

        layout.addWidget(self.transactions_table)
        layout.addLayout(trans_export_layout)

        self.goto_page("transactions", page)
        self.load_transactions()

    def load_transactions(self):
        data = db.execute(
            """
            SELECT
                T.TRANSACTION_ID, P.PRODUCT_NAME, U.FULL_NAME,
                T.TRANSACTION_TYPE, T.SOURCE_TYPE, T.DESTINATION_TYPE,
                T.QUANTITY, T.TOTAL_VALUE
            FROM STOCK_TRANSACTIONS T
            JOIN PRODUCTS P ON P.PRODUCT_ID=T.PRODUCT_ID
            JOIN USERS U ON U.USER_ID=T.USER_ID
            ORDER BY T.TRANSACTION_ID DESC
            """,
            fetch=True
        )

        if data:
            self.transactions_table.setRowCount(len(data))
            for row, item in enumerate(data):
                tx_type = item["TRANSACTION_TYPE"]
                source = item["SOURCE_TYPE"]
                dest = item["DESTINATION_TYPE"]
                
                color = QColor(255, 255, 255)
                if tx_type == 'STOCK IN' and source == 'SUPPLIER':
                    color = QColor(200, 255, 200)
                elif tx_type == 'STOCK OUT' and dest == 'CUSTOMER':
                    color = QColor(255, 200, 200)
                elif tx_type == 'STOCK IN' and source == 'WAREHOUSE':
                    color = QColor(200, 200, 255)
                elif tx_type == 'STOCK OUT' and dest == 'WAREHOUSE':
                    color = QColor(255, 255, 200)
                
                values = [
                    item["TRANSACTION_ID"], item["PRODUCT_NAME"], item["FULL_NAME"],
                    item["TRANSACTION_TYPE"], item["QUANTITY"],
                    "₹{:,.2f}".format(item["TOTAL_VALUE"]),
                    ""
                ]
                for col, value in enumerate(values):
                    cell = QTableWidgetItem(str(value))
                    cell.setBackground(color)
                    self.transactions_table.setItem(row, col, cell)
        else:
            self.transactions_table.setRowCount(0)

        stock_in = db.scalar("SELECT COALESCE(SUM(QUANTITY),0) FROM STOCK_TRANSACTIONS WHERE TRANSACTION_TYPE='STOCK IN'")
        stock_out = db.scalar("SELECT COALESCE(SUM(QUANTITY),0) FROM STOCK_TRANSACTIONS WHERE TRANSACTION_TYPE='STOCK OUT'")

        self.draw_bar_chart(
            self.trans_axis1, self.trans_figure1, self.trans_canvas1,
            ['Stock In', 'Stock Out'],
            [stock_in, stock_out],
            'Stock Movement Summary',
            ['#22c55e', '#ef4444']
        )

        top_products = db.execute(
            """
            SELECT P.PRODUCT_NAME AS NAME, COUNT(*) AS TRANS_COUNT
            FROM STOCK_TRANSACTIONS T
            JOIN PRODUCTS P ON P.PRODUCT_ID = T.PRODUCT_ID
            GROUP BY P.PRODUCT_NAME
            ORDER BY TRANS_COUNT DESC
            LIMIT 6
            """,
            fetch=True
        )

        if top_products:
            categories = [row["NAME"] for row in top_products]
            values = [row["TRANS_COUNT"] for row in top_products]
            self.draw_donut_chart(
                self.trans_axis2, self.trans_figure2, self.trans_canvas2,
                values, categories, "Most Active Products"
            )

    # ========================================================
    # USERS - ADMIN ONLY
    # ========================================================

    def show_users(self):
        if self.user["ROLE"] != "ADMIN":
            return

        self.activate(self.users_btn)
        self.set_page_header("User Management", "Create and manage system users and access levels")

        if "users" in self.pages:
            self.load_users()
            self.stack.setCurrentWidget(self.pages["users"])
            return

        page = QWidget()
        layout = QVBoxLayout(page)

        toolbar = QHBoxLayout()

        add_btn = QPushButton("+  ADD USER")
        add_btn.setObjectName("primary")
        add_btn.clicked.connect(self.add_user)

        edit_btn = QPushButton("EDIT USER")
        edit_btn.setObjectName("secondary")
        edit_btn.clicked.connect(self.edit_user)

        delete_btn = QPushButton("DELETE USER")
        delete_btn.setObjectName("danger")
        delete_btn.clicked.connect(self.delete_user)

        export_btn = QPushButton("📥 EXPORT")
        export_btn.setObjectName("secondary")
        export_btn.clicked.connect(lambda: self.export_table_to_csv(self.users_table, "Users"))

        toolbar.addStretch()
        toolbar.addWidget(add_btn)
        toolbar.addWidget(edit_btn)
        toolbar.addWidget(delete_btn)
        toolbar.addWidget(export_btn)

        layout.addLayout(toolbar)

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels(["ID", "Username", "Full Name", "Role", "Status", ""])
        self.users_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.users_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.users_table)

        self.goto_page("users", page)
        self.load_users()

    def load_users(self):
        data = db.execute(
            """
            SELECT USER_ID, USERNAME, FULL_NAME, ROLE, STATUS
            FROM USERS
            ORDER BY USER_ID
            """,
            fetch=True
        )

        if data:
            self.users_table.setRowCount(len(data))
            for row, user in enumerate(data):
                values = [user["USER_ID"], user["USERNAME"], user["FULL_NAME"],
                          user["ROLE"], user["STATUS"], ""]
                for col, value in enumerate(values):
                    self.users_table.setItem(row, col, QTableWidgetItem(str(value)))
        else:
            self.users_table.setRowCount(0)

    def selected_user_id(self):
        rows = self.users_table.selectionModel().selectedRows()
        if not rows:
            return None
        row = rows[0].row()
        return int(self.users_table.item(row, 0).text())

    def user_dialog(self, user=None):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit User" if user else "Add User")
        dialog.setMinimumWidth(450)

        form = QFormLayout(dialog)
        form.setContentsMargins(30, 30, 30, 30)
        form.setSpacing(13)

        username = QLineEdit()
        password = QLineEdit()
        password.setEchoMode(QLineEdit.Password)

        fullname = QLineEdit()

        role = QComboBox()
        role.addItem("-- Select Role --", None)
        role.addItems(["ADMIN", "MANAGER", "STAFF"])

        status = QComboBox()
        status.addItem("-- Select Status --", None)
        status.addItems(["ACTIVE", "INACTIVE"])

        if user:
            username.setText(user["USERNAME"])
            fullname.setText(user["FULL_NAME"])
            role.setCurrentText(user["ROLE"])
            status.setCurrentText(user["STATUS"])
            password.setPlaceholderText("Leave empty to keep current password")

        form.addRow("Username", username)
        form.addRow("Password", password)
        form.addRow("Full Name", fullname)
        form.addRow("Role", role)
        form.addRow("Status", status)

        buttons = QHBoxLayout()
        cancel = QPushButton("CANCEL")
        cancel.setObjectName("secondary")
        save = QPushButton("SAVE")
        save.setObjectName("primary")
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        form.addRow(buttons)

        cancel.clicked.connect(dialog.reject)

        def save_user():
            if not username.text().strip():
                QMessageBox.warning(dialog, "Validation", "Username is required.")
                return
            if not fullname.text().strip():
                QMessageBox.warning(dialog, "Validation", "Full name is required.")
                return
            if role.currentIndex() == 0:
                QMessageBox.warning(dialog, "Validation", "Please select a role.")
                return
            if status.currentIndex() == 0:
                QMessageBox.warning(dialog, "Validation", "Please select a status.")
                return
            if not user and not password.text():
                QMessageBox.warning(dialog, "Validation", "Password is required.")
                return

            try:
                if user:
                    if password.text():
                        query = """
                            UPDATE USERS
                            SET USERNAME=%s, PASSWORD=%s, FULL_NAME=%s, ROLE=%s, STATUS=%s
                            WHERE USER_ID=%s
                        """
                        params = (
                            username.text().strip(), password.text(), fullname.text().strip(),
                            role.currentText(), status.currentText(), user["USER_ID"]
                        )
                    else:
                        query = """
                            UPDATE USERS
                            SET USERNAME=%s, FULL_NAME=%s, ROLE=%s, STATUS=%s
                            WHERE USER_ID=%s
                        """
                        params = (
                            username.text().strip(), fullname.text().strip(),
                            role.currentText(), status.currentText(), user["USER_ID"]
                        )
                else:
                    query = """
                        INSERT INTO USERS (USERNAME, PASSWORD, FULL_NAME, ROLE, STATUS)
                        VALUES (%s,%s,%s,%s,%s)
                    """
                    params = (
                        username.text().strip(), password.text(), fullname.text().strip(),
                        role.currentText(), status.currentText()
                    )

                result = db.execute(query, params)
                if result:
                    dialog.accept()
                else:
                    QMessageBox.critical(dialog, "Error", "Unable to save user.")
            except Exception as e:
                QMessageBox.critical(dialog, "Error", str(e))

        save.clicked.connect(save_user)
        return dialog

    def add_user(self):
        dialog = self.user_dialog()
        if dialog.exec_():
            self.load_users()
            QMessageBox.information(self, "Success", "User created successfully.")

    def edit_user(self):
        user_id = self.selected_user_id()
        if not user_id:
            QMessageBox.warning(self, "Edit User", "Please select a user.")
            return

        result = db.execute("SELECT * FROM USERS WHERE USER_ID=%s", (user_id,), fetch=True)
        if not result:
            return

        dialog = self.user_dialog(result[0])
        if dialog.exec_():
            self.load_users()
            QMessageBox.information(self, "Success", "User updated successfully.")

    def delete_user(self):
        user_id = self.selected_user_id()
        if not user_id:
            QMessageBox.warning(self, "Delete User", "Please select a user.")
            return

        if user_id == self.user["USER_ID"]:
            QMessageBox.warning(self, "Action Not Allowed", "You cannot delete your own account.")
            return

        answer = QMessageBox.question(self, "Confirm Delete", "Delete this user permanently?",
                                      QMessageBox.Yes | QMessageBox.No)
        if answer != QMessageBox.Yes:
            return

        result = db.execute("DELETE FROM USERS WHERE USER_ID=%s", (user_id,))
        if result:
            self.load_users()
            QMessageBox.information(self, "Deleted", "User deleted successfully.")
        else:
            QMessageBox.critical(self, "Error", "Unable to delete user.")

    # ========================================================
    # LOGOUT
    # ========================================================

    def logout(self):
        answer = QMessageBox.question(self, "Logout", "Are you sure you want to logout?",
                                      QMessageBox.Yes | QMessageBox.No)
        if answer == QMessageBox.Yes:
            self.login_window = LoginWindow()
            self.login_window.show()
            self.close()


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