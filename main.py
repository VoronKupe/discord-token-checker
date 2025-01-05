import json
import requests
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QWidget, QFileDialog, QHeaderView
)
from PySide6.QtCore import Qt, QPropertyAnimation, QRect
from PySide6.QtGui import QFont, QColor, QPalette
import sys
import threading


class DiscordTokenChecker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Discord Token Checker - Par Voronkupe")
        self.setGeometry(100, 100, 1000, 700)

        self.tokens = []
        self.results = []

        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E2E;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #2E2E3E;
                border: 1px solid #3E3E5E;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #444466;
            }
            QPushButton:pressed {
                background-color: #555577;
            }
            QTableWidget {
                background-color: #2E2E3E;
                color: #FFFFFF;
                gridline-color: #444466;
                selection-background-color: #444466;
            }
            QHeaderView::section {
                background-color: #3E3E4E;
                color: #FFFFFF;
                padding: 5px;
                border: none;
            }
        """)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.title_label = QLabel("Discord Token Checker")
        self.title_label.setFont(QFont("Arial", 28, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        self.import_button = self.create_button("Importer Tokens")
        self.import_button.clicked.connect(self.import_tokens)
        self.layout.addWidget(self.import_button)

        self.start_button = self.create_button("Start")
        self.start_button.clicked.connect(self.start_checking)
        self.layout.addWidget(self.start_button)

        self.export_button = self.create_button("Exporter les Valides")
        self.export_button.clicked.connect(self.export_valid_tokens)
        self.layout.addWidget(self.export_button)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Token", "Validité", "Nitro", "Hypesquad", "Moyen de Paiement"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setFont(QFont("Arial", 12))
        self.layout.addWidget(self.table)

        self.footer_label = QLabel("Par Voronkupe - 2025")
        self.footer_label.setFont(QFont("Arial", 10))
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.footer_label.setStyleSheet("color: #888888; margin-top: 20px;")
        self.layout.addWidget(self.footer_label)

    def create_button(self, text):
        """Créer un bouton avec animation"""
        button = QPushButton(text)
        button.setFont(QFont("Arial", 14))
        return button

    def import_tokens(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Importer Tokens", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, "r") as file:
                self.tokens = [line.strip() for line in file.readlines() if line.strip()]
            self.update_status(f"{len(self.tokens)} tokens importés.")

    def update_status(self, message):
        self.title_label.setText(message)

    def start_checking(self):
        if not self.tokens:
            self.update_status("Veuillez importer des tokens d'abord.")
            return

        self.results = []
        self.table.setRowCount(0)
        threading.Thread(target=self.check_tokens).start()

    def check_tokens(self):
        for token in self.tokens:
            result = self.check_token(token)
            self.results.append(result)
            self.update_table(result)

    def check_token(self, token):
        headers = {"Authorization": token}
        response = requests.get("https://discord.com/api/v9/users/@me", headers=headers)

        if response.status_code == 200:
            nitro = self.check_nitro(token)
            hypesquad = self.check_hypesquad(token)
            payment_methods = self.check_payment_methods(token)

            return {
                "token": token,
                "valid": "Oui",
                "nitro": nitro,
                "hypesquad": hypesquad,
                "payment_methods": payment_methods,
            }
        else:
            return {
                "token": token,
                "valid": "Non",
                "nitro": "N/A",
                "hypesquad": "N/A",
                "payment_methods": "N/A",
            }

    def check_nitro(self, token):
        headers = {"Authorization": token}
        response = requests.get("https://discord.com/api/v9/users/@me/billing/subscriptions", headers=headers)

        if response.status_code == 200 and len(response.json()) > 0:
            return "Oui"
        return "Non"

    def check_hypesquad(self, token):
        headers = {"Authorization": token}
        response = requests.get("https://discord.com/api/v9/hypesquad/online", headers=headers)

        if response.status_code == 204:
            return "Oui"
        return "Non"

    def check_payment_methods(self, token):
        headers = {"Authorization": token}
        response = requests.get("https://discord.com/api/v9/users/@me/billing/payment-sources", headers=headers)

        if response.status_code == 200 and len(response.json()) > 0:
            return "Oui"
        return "Non"

    def update_table(self, result):
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(result["token"]))
        self.table.setItem(row, 1, QTableWidgetItem(result["valid"]))
        self.table.setItem(row, 2, QTableWidgetItem(result["nitro"]))
        self.table.setItem(row, 3, QTableWidgetItem(result["hypesquad"]))
        self.table.setItem(row, 4, QTableWidgetItem(result["payment_methods"]))

    def export_valid_tokens(self):
        valid_tokens = [result["token"] for result in self.results if result["valid"] == "Oui"]
        if not valid_tokens:
            self.update_status("Aucun token valide à exporter.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Exporter les Tokens Valides", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, "w") as file:
                file.write("\n".join(valid_tokens))
            self.update_status(f"{len(valid_tokens)} tokens valides exportés vers {file_path}.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DiscordTokenChecker()
    window.show()
    sys.exit(app.exec())
