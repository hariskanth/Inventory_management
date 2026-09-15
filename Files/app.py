"""
app.py
------------------------------------------------------------
All event-handler / business-logic things: form validation,
loading data from the database into tables, responding to
button clicks and dropdown changes, and other actions that
happen once the UI (built by ui.py) is already on screen.

These mixins call into database.py (the shared `db` instance)
to read/write data and update the widgets that ui.py created
on `self`. main.py combines an *App mixin with a *UI mixin
(from ui.py) to build the final, runnable LoginWindow and
MainWindow classes.
"""

import csv
from datetime import datetime, timedelta
from functools import partial

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

from database import db


# ============================================================
# LOGIN WINDOW - EVENT HANDLERS
# ============================================================

class LoginApp:
    """Event-handling / business-logic methods for LoginWindow."""

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

        from main import MainWindow  # local import avoids a circular import with main.py
        self.main_window = MainWindow(user)
        self.main_window.show()
        self.close()


# ============================================================
# MAIN WINDOW
# ============================================================


# ============================================================
# MAIN WINDOW - EVENT HANDLERS
# ============================================================

class MainWindowApp:
    """Event-handling / business-logic methods for MainWindow:
    capacity checks, data loading, filtering, CRUD actions and
    other responses to user interaction."""

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
            from main import LoginWindow  # local import avoids a circular import with main.py
            self.login_window = LoginWindow()
            self.login_window.show()
            self.close()


# ============================================================
# APPLICATION START
# ============================================================


