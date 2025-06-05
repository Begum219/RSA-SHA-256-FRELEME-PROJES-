# rsa_gui.py
import sys, base64, hashlib
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit,
    QLabel, QMainWindow, QStackedWidget, QFileDialog
)
from PyQt5.QtGui import QFont, QPalette, QBrush, QPixmap
from PyQt5.QtCore import Qt
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

# LED Efektli Buton
class StylishButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setFont(QFont("Segoe UI", 11))
        self.setStyleSheet("""
            QPushButton {
                background-color: #1e1e1e;
                color: #ffff33;
                padding: 12px 20px;
                border: 2px solid #ffff33;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #333;
                border: 2px solid #ffaa00;
            }
            QPushButton:pressed {
                background-color: #444;
                border: 2px solid #ffcc00;
            }
        """)

# LED Efektli Başlık
def create_led_label(text, size=20):
    label = QLabel(text)
    label.setStyleSheet(f"""
        color: #ffff33;
        font-size: {size}px;
        font-weight: bold;
        text-shadow: 0 0 5px #ffff33, 0 0 10px #ffaa00;
    """)
    label.setAlignment(Qt.AlignCenter)
    return label

# Taban Sayfa
class BasePage(QWidget):
    def __init__(self, switch_page_callback):
        super().__init__()
        self.setStyleSheet("background-color: transparent; color: white;")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

        self.back_button = StylishButton("↩ Ana Menü")
        self.back_button.clicked.connect(lambda: switch_page_callback("menu"))
        layout.addWidget(self.back_button)

        self.layout = layout

# Ana Menü
class MainMenu(QWidget):
    def __init__(self, switch_page_callback):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

        title = create_led_label("🔐 Şifreleme Sistemleri", 24)
        title.setStyleSheet("""
            color: #ffff33;
            font-size: 24px;
            font-weight: bold;
            background-color: rgba(0, 0, 0, 0.6);
            padding: 8px;
            border-radius: 8px;
        """)
        layout.addWidget(title)

        buttons = [
            ("RSA Anahtar Üret", "keygen"),
            ("RSA Şifrele", "encrypt"),
            ("RSA Deşifrele", "decrypt"),
            ("SHA-256 Özeti", "hash")
        ]
        for text, page in buttons:
            btn = StylishButton(text)
            btn.clicked.connect(lambda _, p=page: switch_page_callback(p))
            layout.addWidget(btn)

        label = QLabel("GELİŞTİREN: BEGÜM ÇETİNKAYA")
        label.setStyleSheet("""
            color: #ffff33;
            margin-top: 20px;
            font-size: 15px;
            background-color: rgba(0, 0, 0, 0.5);
            padding: 4px;
            border-radius: 6px;
        """)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

# RSA Anahtar Üretim Sayfası
class KeyGenPage(BasePage):
    def __init__(self, switch_page_callback):
        super().__init__(switch_page_callback)
        self.layout.addWidget(create_led_label("🔑 RSA Anahtar Üret"))

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.layout.addWidget(self.output)

        btn = StylishButton("Anahtar Üret")
        btn.clicked.connect(self.generate_keys)
        self.layout.addWidget(btn)

    def generate_keys(self):
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()

        private_pem = private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption()
        )

        public_pem = public_key.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo
        )

        self.output.setText(f"🔒 Private Key:\n{private_pem.decode()}\n\n🔓 Public Key:\n{public_pem.decode()}")

# RSA Şifreleme Sayfası
class EncryptPage(BasePage):
    def __init__(self, switch_page_callback):
        super().__init__(switch_page_callback)
        self.layout.addWidget(create_led_label("🛡 RSA Şifreleme"))

        self.public_input = QTextEdit()
        self.public_input.setPlaceholderText("Public Key girin...")
        self.layout.addWidget(self.public_input)

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Şifrelenecek metni girin...")
        self.layout.addWidget(self.message_input)

        btn = StylishButton("Şifrele")
        btn.clicked.connect(self.encrypt)
        self.layout.addWidget(btn)

        self.result = QTextEdit()
        self.result.setReadOnly(True)
        self.layout.addWidget(self.result)

    def encrypt(self):
        try:
            pubkey = serialization.load_pem_public_key(self.public_input.toPlainText().encode())
            message = self.message_input.toPlainText().encode()
            encrypted = pubkey.encrypt(
                message,
                padding.OAEP(
                    mgf=padding.MGF1(hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            self.result.setText(base64.b64encode(encrypted).decode())
        except Exception as e:
            self.result.setText(f"Hata: {str(e)}")

# RSA Deşifreleme Sayfası
class DecryptPage(BasePage):
    def __init__(self, switch_page_callback):
        super().__init__(switch_page_callback)
        self.layout.addWidget(create_led_label("🔓 RSA Deşifreleme"))

        self.private_input = QTextEdit()
        self.private_input.setPlaceholderText("Private Key girin...")
        self.layout.addWidget(self.private_input)

        self.encrypted_input = QTextEdit()
        self.encrypted_input.setPlaceholderText("Şifreli metni girin...")
        self.layout.addWidget(self.encrypted_input)

        btn = StylishButton("Deşifrele")
        btn.clicked.connect(self.decrypt)
        self.layout.addWidget(btn)

        self.result = QTextEdit()
        self.result.setReadOnly(True)
        self.layout.addWidget(self.result)

    def decrypt(self):
        try:
            privkey = serialization.load_pem_private_key(self.private_input.toPlainText().encode(), password=None)
            encrypted_data = base64.b64decode(self.encrypted_input.toPlainText().encode())
            decrypted = privkey.decrypt(
                encrypted_data,
                padding.OAEP(
                    mgf=padding.MGF1(hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            self.result.setText(decrypted.decode())
        except Exception as e:
            self.result.setText(f"Hata: {str(e)}")

# SHA-256 Özeti Sayfası
class SHA256Page(BasePage):
    def __init__(self, switch_page_callback):
        super().__init__(switch_page_callback)
        self.layout.addWidget(create_led_label("🔎 SHA-256 Özeti"))

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Özetlenecek metni yazın veya dosya yükleyin...")
        self.layout.addWidget(self.text_input)

        file_btn = StylishButton("Dosya Yükle")
        file_btn.clicked.connect(self.load_file)
        self.layout.addWidget(file_btn)

        hash_btn = StylishButton("SHA-256 Hesapla")
        hash_btn.clicked.connect(self.calculate_hash)
        self.layout.addWidget(hash_btn)

        self.result = QTextEdit()
        self.result.setReadOnly(True)
        self.layout.addWidget(self.result)

    def load_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Dosya Seç")
        if path:
            try:
                with open(path, "rb") as f:
                    content = f.read()
                    self.text_input.setText(base64.b64encode(content).decode())
            except Exception as e:
                self.text_input.setText(f"Dosya okunamadı: {str(e)}")

    def calculate_hash(self):
        try:
            data = base64.b64decode(self.text_input.toPlainText())
            digest = hashlib.sha256(data).hexdigest()
            self.result.setText(digest)
        except Exception as e:
            self.result.setText(f"Hata: {str(e)}")

# Ana Pencere
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔐 Güvenli Şifreleme Sistemleri")
        self.setGeometry(250, 100, 800, 700)

        self.background = QPixmap("plan.png")
        self.update_background()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.pages = {
            "menu": MainMenu(self.switch_page),
            "keygen": KeyGenPage(self.switch_page),
            "encrypt": EncryptPage(self.switch_page),
            "decrypt": DecryptPage(self.switch_page),
            "hash": SHA256Page(self.switch_page)
        }

        for page in self.pages.values():
            self.stack.addWidget(page)

        self.switch_page("menu")

    def switch_page(self, name):
        if name in self.pages:
            self.stack.setCurrentWidget(self.pages[name])

    def resizeEvent(self, event):
        self.update_background()
        super().resizeEvent(event)

    def update_background(self):
        if not self.background.isNull():
            scaled = self.background.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            palette = QPalette()
            palette.setBrush(QPalette.Window, QBrush(scaled))
            self.setPalette(palette)

# Uygulamayı Başlat
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
