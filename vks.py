import sys, datetime, sqlite3
from PyQt5 import QtWidgets as QW
from PyQt5 import QtGui as QG
from  PyQt5 import QtCore as QC
from vksui import Ui_vks

class my_app(QW.QMainWindow):
    def __init__(self):   #, parent=None):
        super().__init__()

        self.colorRed = QG.QColor(255, 0, 0)
        self.colorGray = QG.QColor(128, 128, 128)
        self.colorBlack = QG.QColor(0, 0, 0)
        self.ui = Ui_vks()
        self.ui.setupUi(self)

        self.date = datetime.date.today()
        self.ui.vksdate.setDate(self.date)

        self.ui.vkstable.setRowHeight(0, 50)

        self.readBase()

        self.ui.btnLoad.clicked.connect(self.loadBase)
        self.ui.btnSave.clicked.connect(self.saveBase)
        self.ui.btnDel.clicked.connect(self.delBase)
        self.ui.btnAdd.clicked.connect(self.addBase)
        self.ui.btnColRed.clicked.connect(lambda: self.colorChange(self.colorRed, 'R'))
        self.ui.btnColGray.clicked.connect(lambda: self.colorChange(self.colorGray, 'G'))
        self.ui.btnColBlack.clicked.connect(lambda: self.colorChange(self.colorBlack, 'B'))
        self.ui.btnHTML.clicked.connect(self.saveHTML)

    def loadBase(self):
        self.date = self.ui.vksdate.date().toPyDate()
        self.readBase()

    def readBase(self):
        sql = """SELECT name, tstart, oper, uchast, prim, zal, cvet FROM vks
            WHERE date = '{0}' ORDER BY tstart ASC;""".format(datetime.date.isoformat(self.date))
        self.base = sqlite3.connect('vksdb.db')
        self.baseCursor = self.base.cursor()
        data = self.baseCursor.execute(sql).fetchall()
        self.base.close()

        self.ui.vkstable.setRowCount(len(data))
        for i, row in enumerate(data):
            len0 = len(data[i][0])
            if len0 > 110:
                self.ui.vkstable.setRowHeight(i, 25 * (len0 // 55 + 1))

            color = self.colorBlack
            if data[i][6] == 'R':
                color = self.colorRed
            if data[i][6] == 'G':
                color = self.colorGray

            for j in range(7):
                self.ui.vkstable.setItem(i, j, QW.QTableWidgetItem(data[i][j]))
                self.ui.vkstable.item(i, j).setForeground(color)

    def keyPressEvent(self, event):
        key = event.key()
        if (key == QC.Qt.Key_V) and (event.modifiers() & QC.Qt.ControlModifier):
            clip = QW.QApplication.clipboard().text().rstrip()
            clip = clip.split(sep='\t')
            row = self.ui.vkstable.currentRow()
            lenclip = len(clip)
            if lenclip > 6:
                lenclip = 6
            for i in range(lenclip):
                self.ui.vkstable.setItem(row, i, QW.QTableWidgetItem(clip[i]))
        super().keyPressEvent(event)

    def addBase(self):
        self.ui.vkstable.setRowCount(self.ui.vkstable.rowCount() + 1)
        for j in range(6):
            self.ui.vkstable.setItem(self.ui.vkstable.rowCount() - 1, j, QW.QTableWidgetItem(' '))
        self.ui.vkstable.setItem(self.ui.vkstable.rowCount() - 1, 6, QW.QTableWidgetItem('B'))


    def delBase(self):
        self.ui.vkstable.removeRow(self.ui.vkstable.currentRow())

    def colorChange(self, color, nameColor):
        row = self.ui.vkstable.currentRow()
        self.ui.vkstable.setItem(row, 6, QW.QTableWidgetItem(nameColor))
        for i in range(7):
            self.ui.vkstable.item(row,i).setForeground(color)

    def saveBase(self):
        data = []
        rcount = self.ui.vkstable.rowCount()
        for i in range(rcount):
            ccount = self.ui.vkstable.columnCount()
            rowdata = []
            for j in range(ccount):
                rowdata.append(self.ui.vkstable.item(i, j).text())
            data.append(rowdata)
        sql = """DELETE FROM vks WHERE date = '{0}';""".format(datetime.date.isoformat(self.date))

        self.base = sqlite3.connect('vksdb.db')
        self.baseCursor = self.base.cursor()
        self.baseCursor.execute(sql)
        self.base.commit()

        sql = """INSERT INTO vks (date, name, tstart, oper, uchast, prim, zal, cvet)
                VALUES ('{0}', ?, ?, ?, ?, ?, ?, ?);""".format(datetime.date.isoformat(self.date))
        self.baseCursor.executemany(sql, data)
        self.base.commit()
        self.base.close()

        self.readBase()

    def saveHTML(self):
        html0 = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Type" content="text/html;" />
    <link rel="stylesheet" href="vks.css">
    <title>График совещаний видео-конференц связи Балаковской АЭС</title>
</head>
<body>
    <table>
        <caption><h2>График совещаний видео-конференц связи Балаковской АЭС на {0}.{1}.{2}</h2></caption>
        <thead>
            <tr>
                <th width="34%">Мероприятие</th>
                <th width="4%">Время</th>
                <th width="5%">Оператор</th>
                <th width="32%">Участники</th>
                <th width="15%">Примечания</th>
                <th width="10%">Помещение</th>
            </tr>
        </thead>""".format(self.date.day, self.date.month, self.date.year)
        rcount = self.ui.vkstable.rowCount()
        for i in range(rcount):
            color = 'style="color: black">'
            if self.ui.vkstable.item(i, 6).text() == 'R':
                color = 'style="color: red">'
            if self.ui.vkstable.item(i, 6).text() == 'G':
                color = 'style="color: grey">'

            html0 = html0 + '<tr>\r\n'
            html0 = html0 + '<td align="left" ' + color + self.ui.vkstable.item(i, 0).text()+'</td>\r\n'
            html0 = html0 + '<td align="center"' + color + self.ui.vkstable.item(i, 1).text() + '</td>\r\n'
            html0 = html0 + '<td align="center"' + color + self.ui.vkstable.item(i, 2).text() + '</td>\r\n'
            html0 = html0 + '<td align="left"' + color + self.ui.vkstable.item(i, 3).text() + '</td>\r\n'
            html0 = html0 + '<td align="center"' + color + self.ui.vkstable.item(i, 4).text() + '</td>\r\n'
            html0 = html0 + '<td align="center"' + color + self.ui.vkstable.item(i, 5).text() + '</td>\r\n'
            html0 = html0 + '</tr>'

        html0 = html0 + """</table></body></html> """
        with open('vks.htm', 'w') as f:
            f.write(html0)

app = QW.QApplication(sys.argv)
window = my_app()
window.show()
app.exec_()





