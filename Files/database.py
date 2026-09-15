"""
database.py
------------------------------------------------------------
All database-related things: connection configuration, the
Database wrapper class, and the shared `db` instance used
throughout the application.
"""

import mysql.connector
from PyQt5.QtWidgets import QMessageBox


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


# Shared database instance used across the whole application
db = Database()
