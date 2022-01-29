from PyQt5.QtGui import QPalette, QColor


class DarkPalette(QPalette):
    def __init__(self):
        super().__init__()

        black = QColor('#313335')
        gray = QColor('#3C3F41')
        primary = QColor('#4B6EAF')
        white = QColor('#FFFFFF')

        self.setColor(QPalette.Window, gray)
        self.setColor(QPalette.WindowText, white)
        self.setColor(QPalette.Base, black)
        self.setColor(QPalette.AlternateBase, gray)
        self.setColor(QPalette.ToolTipBase, primary)
        self.setColor(QPalette.ToolTipText, white)
        self.setColor(QPalette.Text, white)
        self.setColor(QPalette.Button, gray)
        self.setColor(QPalette.ButtonText, white)
        self.setColor(QPalette.Link, primary)
        self.setColor(QPalette.Highlight, primary)
        self.setColor(QPalette.HighlightedText, white)

        self.setColor(QPalette.Active, QPalette.Button, black)
        self.setColor(QPalette.Disabled, QPalette.Base, gray)
        self.setColor(QPalette.Disabled, QPalette.ButtonText, white.darker())
        self.setColor(QPalette.Disabled, QPalette.WindowText, gray)
        self.setColor(QPalette.Disabled, QPalette.Text, white.darker())
        self.setColor(QPalette.Disabled, QPalette.Light, black)
