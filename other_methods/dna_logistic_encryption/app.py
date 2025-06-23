import sys
from PyQt5 import QtWidgets
from encrypt import encrypt_image
from decrypt import decrypt_image

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DNA + Logistic Encryptor")
        self.resize(600, 400)
        self.init_ui()

    def init_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        v = QtWidgets.QVBoxLayout(central)

        # Girdi/Çıktı seçimi
        self.inp = QtWidgets.QLineEdit(); b1 = QtWidgets.QPushButton("Girdi Seç"); b1.clicked.connect(self.select_input)
        self.out = QtWidgets.QLineEdit(); b2 = QtWidgets.QPushButton("Çıktı Seç"); b2.clicked.connect(self.select_output)
        h1 = QtWidgets.QHBoxLayout(); h1.addWidget(self.inp); h1.addWidget(b1)
        h2 = QtWidgets.QHBoxLayout(); h2.addWidget(self.out); h2.addWidget(b2)
        v.addLayout(h1); v.addLayout(h2)

        # Parola
        self.pwd = QtWidgets.QLineEdit(); self.pwd.setEchoMode(self.pwd.Password)
        v.addWidget(QtWidgets.QLabel("Parola:")); v.addWidget(self.pwd)

        # DNA kuralı ve kaotik parametreler
        self.dna = QtWidgets.QComboBox(); self.dna.addItems([str(i) for i in range(1,9)])
        v.addWidget(QtWidgets.QLabel("DNA Kuralı")); v.addWidget(self.dna)

        grid = QtWidgets.QGridLayout()
        self.x0 = [QtWidgets.QDoubleSpinBox() for _ in range(3)]
        self.r = [QtWidgets.QDoubleSpinBox() for _ in range(3)]
        for i in range(3):
            self.x0[i].setRange(0.0, 1.0); self.x0[i].setSingleStep(0.01); self.x0[i].setValue(0.41 + 0.1*i)
            self.r[i].setRange(3.0, 4.0); self.r[i].setSingleStep(0.01); self.r[i].setValue(3.99)
            grid.addWidget(QtWidgets.QLabel(f"x0[{i+1}]"), 0, 2*i)
            grid.addWidget(self.x0[i], 0, 2*i+1)
            grid.addWidget(QtWidgets.QLabel(f"r[{i+1}]"), 1, 2*i)
            grid.addWidget(self.r[i], 1, 2*i+1)
        v.addLayout(grid)

        # Butonlar ve geri bildirim
        btn_h = QtWidgets.QHBoxLayout()
        encrypt_btn = QtWidgets.QPushButton("Şifrele"); encrypt_btn.clicked.connect(self.on_encrypt)
        decrypt_btn = QtWidgets.QPushButton("Çöz"); decrypt_btn.clicked.connect(self.on_decrypt)
        btn_h.addWidget(encrypt_btn); btn_h.addWidget(decrypt_btn)
        v.addLayout(btn_h)
        self.status = QtWidgets.QLabel("Hazır")
        self.progress = QtWidgets.QProgressBar(); self.progress.setRange(0, 100)
        v.addWidget(self.progress); v.addWidget(self.status)

    def select_input(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Girdi Resim", "", "Image Files (*.png *.jpg *.jpeg)")
        if path: self.inp.setText(path)

    def select_output(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Çıktı Resim", "", "PNG (*.png)")
        if path: self.out.setText(path)

    def on_encrypt(self):
        inp, outp, pwd = self.inp.text(), self.out.text(), self.pwd.text()
        if not inp or not outp or not pwd:
            QtWidgets.QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun")
            return
        dna_rule = int(self.dna.currentText())
        x0_list = [w.value() for w in self.x0]
        r_list = [w.value() for w in self.r]
        try:
            self.progress.setValue(10)
            encrypt_image(inp, outp, pwd, dna_rule, x0_list, r_list)
            self.progress.setValue(100)
            self.status.setText("Şifreleme tamamlandı")
            QtWidgets.QMessageBox.information(self, "Başarılı", "Şifrelendi!")
        except Exception as e:
            self.status.setText("Hata")
            QtWidgets.QMessageBox.critical(self, "Hata", str(e))

    def on_decrypt(self):
        inp, outp, pwd = self.inp.text(), self.out.text(), self.pwd.text()
        if not inp or not outp or not pwd:
            QtWidgets.QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun")
            return
        try:
            self.progress.setValue(10)
            decrypt_image(inp, outp, pwd)
            self.progress.setValue(100)
            self.status.setText("Çözüm tamamlandı")
            QtWidgets.QMessageBox.information(self, "Başarılı", "Çözüldü!")
        except Exception as e:
            self.status.setText("Hata")
            QtWidgets.QMessageBox.critical(self, "Hata", str(e))

def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
