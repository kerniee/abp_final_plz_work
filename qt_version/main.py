# 9roH}$gr - пароль от архива

import os
import sys

import xlrd

if hasattr(sys, 'frosen'):
    os.environ['PATH'] = sys._MEIPASS + ';' + os.environ['PATH']
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from data import db_session
from data.Parts import Parts
from data.Types import Types
from data.drons import Drons
from data.tech_maps import TechMaps


class LoadToDataBaseWindow(QMainWindow):
    def __init__(self):
        db_session.global_init("db/Ttracking_drones.sqlite")
        super().__init__()
        uic.loadUi('ui/load_form.ui', self)
        self.pushButton.clicked.connect(self.viewFile)
        self.pushButton1.clicked.connect(self.viewFile)
        self.pushButton2.clicked.connect(self.viewFile)
        self.b_load.clicked.connect(self.loadFile)
        self.b_close.clicked.connect(self.close)

    def viewFile(self):
        fname = QFileDialog.getOpenFileName(self, 'Выбирете файл', '')[0]
        if self.sender() == self.pushButton:
            self.e_drons.setText(fname)
        elif self.sender() == self.pushButton1:
            self.e_complact.setText(fname)
        elif self.sender() == self.pushButton2:
            self.e_cards.setText(fname)

    def loadFile(self):
        dron_file = self.e_drons.text().strip()
        complact_file = self.e_complact.text().strip()
        cards_file = self.e_cards.text().strip()
        print(os.path.exists(dron_file), os.path.exists(complact_file), os.path.exists(cards_file))
        if os.path.exists(dron_file) and os.path.exists(complact_file) and os.path.exists(cards_file):
            self.load(dron_file, complact_file, cards_file)

    def load(self, drons, complact, cards_file):
        wb = xlrd.open_workbook(drons)
        sh = wb.sheet_by_index(0)
        for row_number in range(1, sh.nrows):
            temp = sh.row_values(row_number)
            self.addDron(temp[1], temp[2])

        wb1 = xlrd.open_workbook(complact)
        sh1 = wb1.sheet_by_index(0)
        for row_number in range(1, sh1.nrows):
            temp = sh1.row_values(row_number)
            self.addParts(temp[1], temp[2])

        wb2 = xlrd.open_workbook(cards_file)
        sh2 = wb2.sheet_by_index(0)
        for row_number in range(1, sh2.nrows):
            temp = sh2.row_values(row_number)
            self.addTechMap(temp[1], temp[2], temp[3])

    def addDron(self, name, cost):
        dron = Drons()
        dron.name = name
        dron.cost = cost

        session = db_session.create_session()
        session.add(dron)
        session.commit()

    def addParts(self, name, type_):
        # создание элемента нужного класса
        part = Parts()
        # установка параметров элемента
        part.name = name

        # создание сессии к базе данных
        session = db_session.create_session()
        part.type = session.query(Types).filter(Types.name.like("%" + type_ + "%")).first().id

        # запись элемента в базу
        session.add(part)
        session.commit()

    def addTechMap(self, dron_name, part_name, qual):
        map_ = TechMaps()

        session = db_session.create_session()
        map_.id_drons = session.query(Drons).filter(Drons.name.like("%" + dron_name + "%")).first().id
        map_.id_parts = session.query(Parts).filter(Parts.name.like("%" + part_name + "%")).first().id
        map_.quantity = qual

        session.add(map_)
        session.commit()


class AddPartWindow(QMainWindow):
    def __init__(self):
        db_session.global_init("db/Ttracking_drones.sqlite")
        super().__init__()
        uic.loadUi('ui/add_parts_form.ui', self)
        self.ok.clicked.connect(self.loadToDB)
        self.b_load.clicked.connect(self.loadToDB)
        self.b_close.clicked.connect(self.close)

    def loadToDB(self):
        # TODO: запись в реальную базу данных
        #получение данных из таблицы
        parts_lst = self.getData()

        #запись в базу данных
        #for i in parts_lst:
            #self.addParts(i[0], i[1], i[2])

        with open('log.txt', 'a+') as log:
            n = self.spinBox.value()
            date = self.dateEdit.date().toString()
            name = self.lineEdit.text()
            log.write('-----------\n')
            log.write(f'Номер: {n}     Дата: {date}\n')
            log.write(f'Ответственный: {name}\n')
            lines = []
            for line in lines:
                log.write(line + '\n')
        if self.sender() == self.ok:
            self.close()
         
    def getData(self):
        rows = self.tableWidget.rowCount()
        cols = self.tableWidget.columnCount()
        data = []
        for row in range(rows):
            tmp = []
            for col in range(cols):
                tmp.append(self.tableWidget.item(row, col).text())
            data.append(tmp)
        return data

    def addRow(self):
        rows = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(rows + 1)

    def addParts(self, name, type_):
        # создание элемента нужного класса
        part = Parts()
        # установка параметров элемента
        part.name = name

        # создание сессии к базе данных
        session = db_session.create_session()
        part.type = session.query(Types).filter(Types.name.like("%" + '' + "%")).first().id

        # запись элемента в базу
        session.add(part)
        session.commit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AddPartWindow()
    ex.show()
    sys.exit(app.exec_())
