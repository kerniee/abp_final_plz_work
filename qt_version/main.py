# 9roH}$gr - пароль от архива

import os
import sys
import time
import datetime

import xlrd
import xlwt

import pyqtgraph as pg

if hasattr(sys, 'frosen'):
    os.environ['PATH'] = sys._MEIPASS + ';' + os.environ['PATH']
from PyQt5 import uic, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem
from PyQt5 import QtWidgets
from data import db_session
from data.Parts import Parts
from data.Types import Types
from data.drons import Drons
from data.tech_maps import TechMaps
from data.storage import Storage


class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/menu.ui', self)
        self.b_loadData.clicked.connect(self.createWindow('LoadToDataBaseWindow'))
        self.b_addPart.clicked.connect(self.createWindow('AddPartWindow'))
        self.b_viewAll.clicked.connect(self.createWindow('ViewAllWindow'))
        # self.b_createRequest.clicked.connect(self.createWindow('...'))
        # self.b_viewRequests.clicked.connect(self.createWindow('...'))
        self.b_viewAKB.clicked.connect(self.createWindow('ViewAKBWindow'))

    def createWindow(self, name):
        def _createWindow():
            window = globals()[name]()
            setattr(self, name, window)
            getattr(self, name, window).show()

        return _createWindow


class LoadToDataBaseWindow(QMainWindow):
    def __init__(self):
        db_session.global_init("db/Tracking_drones.sqlite")
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
        db_session.global_init("db/Tracking_drones.sqlite")
        super().__init__()
        uic.loadUi('ui/add_parts_form.ui', self)
        self.ok.clicked.connect(self.loadToDB)
        self.b_load.clicked.connect(self.loadToDB)
        self.b_close.clicked.connect(self.cclose)
        self.b_addRow.clicked.connect(self.addRow)

    def cclose(self):
        parts_lst = self.getData()
        flag = False
        for line in parts_lst:
            if any([l == '' for l in line]):
                flag = True
                self.error_window = Error()
                self.error_window.show()
        if not flag:
            self.close()

    def loadToDB(self):
        # получение данных из таблицы
        parts_lst = self.getData()

        # запись в базу данных
        for i in parts_lst:
            print(i)
            self.addPost(i[0], i[1], i[2])

        with open('log.txt', 'a+') as log:
            n = self.spinBox.value()
            date = self.dateEdit.date().toString()
            name = self.lineEdit.text()
            log.write('-----------\n')
            log.write(f'Номер: {n}     Дата: {date}\n')
            log.write(f'Ответственный: {name}\n')
            for line in parts_lst:
                s = f'Комплектующие: {line[0]} Серийный номер: {line[1]} Количество: {line[2]}'
                log.write(s + '\n')
        if self.sender() == self.ok:
            self.close()

    def getData(self):
        rows = self.tableWidget.rowCount()
        cols = self.tableWidget.columnCount()
        data = []
        for row in range(rows):
            tmp = []
            for col in range(cols):
                try:
                    tmp.append(self.tableWidget.item(row, col).text())
                except AttributeError:
                    tmp.append('')
            data.append(tmp)
        return data

    def addRow(self):
        rows = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(rows + 1)

    def addPost(self, name, ser_num, qual):
        post = Storage()
        session = db_session.create_session()
        post.id_parts = session.query(Parts).filter(Parts.name.like("%" + name + "%")).first().id
        try:
            post.serial_number = int(ser_num)
        except TypeError:
            print('некоторые параметры не записаны')
        try:
            post.quantity = int(qual)
        except TypeError:
            print('некоторые параметры не записаны')
        session.add(post)
        session.commit()


class ViewAllWindow(QMainWindow):
    def __init__(self):
        db_session.global_init("db/Tracking_drones.sqlite")
        super().__init__()
        uic.loadUi('ui/remainings.ui', self)
        self.b_load.clicked.connect(self.takeNote)
        self.b_print.clicked.connect(self.createXLSX)
        self.b_close.clicked.connect(self.close)
        self.editDateTime()

    def editDateTime(self):
        today = datetime.datetime.now().date()
        self.dateEdit.setMaximumDate(today)

    def loadDataToTable(self, data):
        self.tableWidget.setRowCount(len(data))
        for i, elem in enumerate(data):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.tableWidget.resizeColumnsToContents()

    def takeNote(self):
        day = self.dateEdit.date().toPyDate()
        now_day = datetime.datetime.now().date()
        #Если дата в будущем вызываем ошибку
        if day > now_day:
            warn = Error(self, 'На указаную дату не может быть отчёта')
            warn.show()
        #если дата назначено сегодня - вызываем информацию напрямую из базы
        elif day == now_day:
            self.takeDataFromBase()
        else:
            # проверка есть ли отчёт на это число
            dates_where_we_have_otchet = open('отчёты/otchet_lod.txt', 'r')
            temp = dates_where_we_have_otchet.read().split('\n')

            #если есть берём этот отч1т и выводим в таблицу
            if str(day) in temp:
                filename = 'отчёты/Остаток_на_' + str(day) + '.xls'
                self.takeDataFromFile(filename)
            else:
                temp.append(str(day))
                dates = []
                for i in temp:
                    dates.append(datetime.date(int(i.split('-')[0]), int(i.split('-')[1]), int(i.split('-')[2])))
                dates = sorted(dates)
                #иначе берёмсамое близкое число, предшествующее данному и показываем отчёт за него
                indx = dates.index(day) - 1
                filename = 'отчёты/Остаток_на_' + str(dates[indx])  + '.xls'
                #Если этот индекс валидный - значит есть отчёт, который предшествует данно дате - выводим его
                if 0 <= indx:
                    self.takeDataFromFile(filename)
                else:
                    # Иначе предупреждаем об ошибке
                    warn = Error(self, 'На указаную дату нет отчёта. На предшествующие даты также нет отчётов.')
                    warn.show()

    def takeDataFromFile(self, filename):
        wb2 = xlrd.open_workbook(filename)
        sh2 = wb2.sheet_by_index(0)
        data = []
        for row_number in range(1, sh2.nrows):
            temp = sh2.row_values(row_number)
            data.append(temp)
        self.loadDataToTable(data)

    def takeDataFromBase(self):
        session = db_session.create_session()
        data = [[i.id, i.part.name, i.quantity] for i in session.query(Storage).all()]
        self.loadDataToTable(data)

    def getDataFromTable(self):
        rows = self.tableWidget.rowCount()
        cols = self.tableWidget.columnCount()
        data = []
        for row in range(rows):
            tmp = []
            for col in range(cols):
                try:
                    tmp.append(self.tableWidget.item(row, col).text())
                except AttributeError:
                    tmp.append('')
            data.append(tmp)
        return data

    def createXLSX(self):
        files = os.listdir('отчёты')
        filename = 'Остаток_на_' + str(self.dateEdit.date().toPyDate()) + '.xls'
        if filename not in files:
            file = open('отчёты/' + filename, 'w')
            file.close()

            file = open('отчёты/otchet_lod.txt', 'r')
            dates = []
            for i in (file.read() + '\n' + str(self.dateEdit.date().toPyDate())).split('\n'):
                dates.append(datetime.date(int(i.split('-')[0]), int(i.split('-')[1]), int(i.split('-')[2])))
            dates = '\n'.join(list(map(str, sorted(dates))))
            file.close()

            file = open('отчёты/otchet_lod.txt', 'w')
            file.write(dates)
            file.close()

        book = xlwt.Workbook(encoding="utf-8")
        sheet1 = book.add_sheet("Python Sheet 1")
        sheet1.write(0, 0, '№')
        sheet1.write(0, 1, 'Комплектующее')
        sheet1.write(0, 2, 'Остаток')

        datas = self.getDataFromTable()

        for row, data in enumerate(datas, start=1):
            for col, field in enumerate(data):
                sheet1.write(row, col, field)

        book.save('отчёты/' + filename)
        win = Error(self, 'Отчёт от остатке успешно подготовлен. Вы можете найти его по пути:\n' + os.path.abspath('отчёты/' + filename))
        win.setWindowTitle('Успешно подготовлен xls')
        win.show()


class ViewAKBWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/spare_parts_remaining_form.ui', self)

        self.dateEdit.dateChanged.connect(self.generate_plot)
        self.dateEdit_2.dateChanged.connect(self.generate_plot)

        self.view = view = pg.PlotWidget()
        self.curve = view.plot(name="Line")
        self.generate_plot()

    def generate_dates(self):
        start_date = self.dateEdit.date().toPyDate()
        l = []
        for i in range(self.NUM_OF_DATES):
            l.append(str(start_date + datetime.timedelta(days=i))[5:])
        return l

    def generate_plot(self):
        # random_array = np.random.random_sample(20)
        self.gridLayout.removeWidget(self.view)
        self.NUM_OF_DATES = (self.dateEdit_2.date().toPyDate() -
                             self.dateEdit.date().toPyDate()).days

        self.view = view = pg.PlotWidget()
        self.curve = view.plot(name="Line")

        # TODO: load info from db
        import random
        array = [random.randint(1, 100) for x in range(self.NUM_OF_DATES)]

        dates = [list(zip(range(self.NUM_OF_DATES), self.generate_dates()))]
        xax = self.view.getAxis('bottom')
        xax.setTicks(dates)
        self.curve.setData(array)
        self.gridLayout.addWidget(self.view)


class Error(QtWidgets.QDialog):
    def __init__(self, main=None, text='Не все поля заполнены'):
        super().__init__(main)
        uic.loadUi('ui/error.ui', self)
        self.label.setText(text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainMenu()
    ex.show()
    sys.exit(app.exec_())
