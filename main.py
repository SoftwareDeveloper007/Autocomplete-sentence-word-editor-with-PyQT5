import sys
import time
from PyQt5.QtWidgets import QTextEdit, QCompleter, QMainWindow, QApplication, QLabel
from PyQt5.QtGui import QCursor, QKeySequence, QTextCursor, QFont, QSyntaxHighlighter, QTextCharFormat
from PyQt5.QtCore import Qt, QFile, QStringListModel, QRegExp

import customcompleter_rc


class mainGUI(QMainWindow):
    def __init__(self, parent=None):
        # super().__init__()
        # QMainWindow.__init__(self, None)
        super(mainGUI, self).__init__(parent)
        self.initUI()

    def initUI(self):

        # -------- Window Settings -------------------------------------------
        # self.setGeometry(100,100,700,700)
        self.setFixedSize(700, 700)
        self.setWindowTitle("AutoComplete Sentence Tool")
        # self.show()

        # -------- Status Bar -------------------------------------------
        self.status = self.statusBar()

        # -------- Sentence List -------------------------------------------
        self.sentencelabel = QLabel(self)
        self.sentencelabel.setText('Sentence List')
        self.sentencelabel.setStyleSheet("color: blue;"
                                         "font: bold 18pt 'Times New Roman';")
        self.sentencelabel.setAlignment(Qt.AlignCenter)
        self.sentencelabel.setGeometry(50, 70, 400, 30)

        # self.sentencelist = QTextEdit(self)
        font = QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)

        self.sentencelist = TextEdit(self)
        # self.sentencelist.setFont(font)
        self.sentencelist.setStyleSheet("color: rgb(255, 0, 0);")
        self.completer = QCompleter(self)
        self.completer.setModel(self.modelFromFile(':/resources/wordlist.txt'))
        self.completer.setModelSorting(QCompleter.CaseInsensitivelySortedModel)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setWrapAround(False)
        self.sentencelist.setCompleter(self.completer)
        self.sentencelist.setGeometry(50, 100, 400, 550)
        # self.sentencelist.textChanged.connect(self.updateSentenceList)

        # -------- Word List -------------------------------------------
        self.wordlabel = QLabel(self)
        self.wordlabel.setText('Word List')
        self.wordlabel.setStyleSheet("color: blue;"
                                     "font: bold 18pt 'Times New Roman';")
        self.wordlabel.setAlignment(Qt.AlignCenter)
        self.wordlabel.setGeometry(500, 70, 150, 30)

        self.wordlist = QTextEdit(self)
        self.wordlist.setGeometry(500, 100, 150, 550)
        infile = open('resources/wordlist.txt', 'r')
        self.wordlist.setPlainText(infile.read())
        infile.close()
        self.wordlist.textChanged.connect(self.updateWordsList)
        self.words = self.wordlist.document().toPlainText()
        keywordPatterns = self.words.split('\n')

        while '' in keywordPatterns:
            keywordPatterns.remove('')

        for i, wd in enumerate(keywordPatterns):
            keywordPatterns[i] = "\\b" + keywordPatterns[i] + "\\b"

        self.highlighter = Highlighter(keywordPatterns, self.sentencelist.document())

        # -------- Statusbar -------------------------------------------
        self.status = self.statusBar()
        self.sentencelist.cursorPositionChanged.connect(self.CursorPosition)

    def updateWordsList(self):
        self.words = self.wordlist.document().toPlainText()
        outfile = open('resources/wordlist.txt', 'w')
        outfile.write(self.words)
        outfile.close()
        # print(self.words.split('\n'))
        self.completer.setModel(self.modelFromFile(':/resources/wordlist.txt'))

        keywordPatterns = self.words.split('\n')
        while '' in keywordPatterns:
            keywordPatterns.remove('')

        for i, wd in enumerate(keywordPatterns):
            keywordPatterns[i] = "\\b" + keywordPatterns[i] + "\\b"

        self.highlighter.updateKeywordPatterns(keywordPatterns)

    def updateSentenceList(self):
        self.sentences = self.sentencelist.document().toPlainText()

        if len(self.sentences.split('\n')):
            for sentence in self.sentences.split('\n'):
                pass

    def modelFromFile(self, fileName):
        f = QFile(fileName)
        if not f.open(QFile.ReadOnly):
            return QStringListModel(self.completer)

        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

        words = []
        while not f.atEnd():
            line = f.readLine().trimmed()
            if line.length() != 0:
                try:
                    line = str(line, encoding='ascii')
                except TypeError:
                    line = str(line)

                words.append(line)

        QApplication.restoreOverrideCursor()

        return QStringListModel(words, self.completer)

    def CursorPosition(self):
        line = self.sentencelist.textCursor().blockNumber()
        col = self.sentencelist.textCursor().columnNumber()
        linecol = ("Line: " + str(line) + " | " + "Column: " + str(col))
        self.status.showMessage(linecol)


class TextEdit(QTextEdit):
    def __init__(self, parent=None):
        super(TextEdit, self).__init__(parent)
        self._completer = None
        self.setPlainText('')

    def setCompleter(self, c):
        if self._completer is not None:
            self._completer.activated.disconnect()

        self._completer = c

        c.setWidget(self)
        c.setCompletionMode(QCompleter.PopupCompletion)
        c.setCaseSensitivity(Qt.CaseInsensitive)
        c.activated.connect(self.insertCompletion)

    def completer(self):
        return self._completer

    def insertCompletion(self, completion):
        if self._completer.widget() is not self:
            return

        tc = self.textCursor()
        extra = len(completion) - len(self._completer.completionPrefix())
        tc.movePosition(QTextCursor.Left)
        tc.movePosition(QTextCursor.EndOfWord)
        if extra is not 0:
            tc.insertText(completion[-extra:])
            self.setTextCursor(tc)

        tc1 = self.textCursor()
        tc1.movePosition(QTextCursor.StartOfWord)
        tc1.movePosition(QTextCursor.EndOfWord)
        tc1.selectedText().setFontWeight(QFont.Bold)

    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)

        return tc.selectedText()

    def focusInEvent(self, e):
        if self._completer is not None:
            self._completer.setWidget(self)

        super(TextEdit, self).focusInEvent(e)

    def keyPressEvent(self, e):
        if self._completer is not None and self._completer.popup().isVisible():
            # The following keys are forwarded by the completer to the widget.
            if e.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, Qt.Key_Tab, Qt.Key_Backtab):
                e.ignore()
                # Let the completer do default behavior.
                return

        isShortcut = ((e.modifiers() & Qt.ControlModifier) != 0 and e.key() == Qt.Key_0)
        if self._completer is None or not isShortcut:
            # Do not process the shortcut when we have a completer.
            super(TextEdit, self).keyPressEvent(e)

        ctrlOrShift = e.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier)
        if self._completer is None or (ctrlOrShift and len(e.text()) == 0):
            return

        eow = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-="
        hasModifier = (e.modifiers() != Qt.NoModifier) and not ctrlOrShift
        completionPrefix = self.textUnderCursor()

        if not isShortcut and (hasModifier or len(e.text()) == 0 or len(completionPrefix) < 2 or e.text()[-1] in eow):
            self._completer.popup().hide()
            return

        if completionPrefix != self._completer.completionPrefix():
            self._completer.setCompletionPrefix(completionPrefix)
            self._completer.popup().setCurrentIndex(
                self._completer.completionModel().index(0, 0))

        cr = self.cursorRect()
        cr.setWidth(self._completer.popup().sizeHintForColumn(
            0) + self._completer.popup().verticalScrollBar().sizeHint().width())
        self._completer.complete(cr)


class Highlighter(QSyntaxHighlighter):
    def __init__(self, keywordPatterns, parent=None):
        super(Highlighter, self).__init__(parent)

        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(Qt.darkBlue)
        keywordFormat.setFontWeight(QFont.Bold)

        self.keywordPatterns = keywordPatterns

        self.highlightingRules = [(QRegExp(pattern), keywordFormat)
                                  for pattern in self.keywordPatterns]

    def updateKeywordPatterns(self, keywordPatterns):
        self.keywordPatterns = keywordPatterns
        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(Qt.darkBlue)
        keywordFormat.setFontWeight(QFont.Bold)
        self.highlightingRules = [(QRegExp(pattern), keywordFormat)
                                  for pattern in self.keywordPatterns]

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet("QMainWindow{background-color: rgb(200,200,100);border: 2px solid rgb(20,20,20)}")
    GUI = mainGUI()
    GUI.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
