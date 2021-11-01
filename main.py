import sys
from PyQt5.QtWidgets import QApplication, QFileDialog

from widgets import MainWindow


def main():
    app = QApplication(sys.argv)
    path = QFileDialog.getOpenFileName(None, 'Выбрать файл', '')[0]
    if path != '':
        window = MainWindow(path)
        window.show()
        sys.exit(app.exec_())


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hook
    main()
