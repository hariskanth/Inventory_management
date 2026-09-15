"""
ui.py
------------------------------------------------------------
All UI-related things: global stylesheet, and the mixin
classes that build widgets, layouts, pages and dialogs for
LoginWindow and MainWindow.

These mixins contain no business logic / database calls of
their own (aside from what a few dialog "save" callbacks do
inline, since those are inseparable from the dialog widgets
they belong to) - the actual event handling and data loading
lives in app.py. main.py combines a *UI mixin with an
*App mixin (from app.py) to build the final, runnable
LoginWindow and MainWindow classes.
"""

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

from database import db


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
# LOGIN WINDOW - UI MIXIN
# ============================================================

class LoginUI:
    """UI-building methods for LoginWindow."""

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



# ============================================================
# MAIN WINDOW - UI MIXIN
# ============================================================

class MainWindowUI:
    """UI-building methods for MainWindow: sidebar/navigation,
    page layouts, dialogs and chart-drawing helpers."""

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


