import sys
import traceback

from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox

from view.widgets import MainWindow


def main():
    try:
        app = QApplication(sys.argv)
        path = QFileDialog.getOpenFileName(None, 'Выбрать файл', '')[0]
        if path != '':
            window = MainWindow(path)
            window.show()
            sys.exit(app.exec_())
    except Exception as e:
        QMessageBox.critical(None, e.__class__.__name__, traceback.format_exc())


def except_hook(cls, exception, traceback_):
    sys.__excepthook__(cls, exception, traceback_)


if __name__ == '__main__':
    sys.excepthook = except_hook
    main()
