# -*- coding: utf-8 -*-

"""
List Widget
Create a scrollable list with selectable rows. Data must be a List of Lists
@version: 17.03.17
@author: Edgardo Javier Stacul
@email: staculjavier@gmail.com
"""
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.recycleview import RecycleView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.config import ConfigParser
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.metrics import dp
from datetime import datetime
import os
import ast
import time
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, ListProperty
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton

from data.Parts import Parts
from data import db_session
from data.storage import Storage

Builder.load_string("""
<List>:
    ScrollView:
        id: sv
        GridLayout:
            id:         gl
            cols:       root.cols
            size_hint:  (0.5,1)
            height:     self.minimum_height
            width:      self.minimum_width
            spacing:    '2dp'

<ListCell>:
    font_size:'12dp'
    padding: ('10dp', '10dp')
    size_hint: (0.5,.5)
    size: self.texture_size
    color: 0,0,0,1
    bcolor: 1,1,1,1
    canvas.before:
        Color:
            rgba: self.bcolor
        Rectangle:
            pos: self.pos
            size: self.size
<ListHeader>:
    font_size: '16dp'
    padding: ('5dp','5dp')
    size_hint: (None,None)
    size: self.texture_size
    color: 1,1,1,1
    bcolor: 0.5, 0.5, 0.5, 1
    canvas.before:
        Color:
            rgba: self.bcolor
        Rectangle:
            pos: self.pos
            size: self.size
""")


class List(RelativeLayout):
    data = ListProperty([])
    cols = NumericProperty()
    rowSelected = NumericProperty()

    def __init__(self, *args, **kwargs):
        super(List, self).__init__(**kwargs)

    def on_data(self, *arg):
        self.list_scrollable()
        self.add_buttons()

    def close(self, *args):
        exit(0)

    def load_to_db(self, *args):
        # TODO сделать загрузку в базу данных
        # получение текста из текстовых полей
        quans = []
        for i in self.Rows:
            quans.append(i[-1].text)
        db_woker.loadDataToDB(quans)

    def add_buttons(self):

        b1 = Button(text='Записать', size_hint=(0.3, 0.1),
                    width='20dp', pos_hint={'center_x': .838, 'center_y': .6},
                    on_press=self.load_to_db)
        b2 = Button(text='Закрыть', size_hint=(0.3, 0.1),
                    width='20dp', pos_hint={'center_x': .838, 'center_y': .45},
                    on_press=self.close)

        self.add_widget(b1)
        self.add_widget(b2)

    def list_scrollable(self):
        self.t = self.ids['gl']  # get table widget from kv
        # Reset widget
        self.t.clear_widgets()
        # Build header and table content
        if isinstance(self.data, list):
            try:
                self.Rows = []
                print(1)
                self.t.cols = len(self.data[0]) + 1
                self.t.add_widget(ListHeader(text="<>"))

                for item in self.data[0]:
                    self.t.add_widget(ListHeader(text=item))

                for i in range(len(self.data) - 1):
                    row = []
                    row.append(ToggleButton(id=str(i + 1), on_press=self.select_row, group='table', size_hint=(None, 1),
                                            width='20dp'))
                    print(4)
                    # cb.bind(active=self.selrow)
                    for j in range(len(self.data[i])):
                        if j == 2:
                            tr = TextInput(size_hint=(1, 0.1))
                            tr.insert_text(substring=str(self.data[i + 1][j]).encode("utf-8").decode("utf-8"))
                            row.append(tr)
                        else:
                            row.append(ListCell(text=str(self.data[i + 1][j]).encode("utf-8").decode("utf-8")))
                    for cell in row:
                        self.t.add_widget(cell)
                    self.Rows.append(row)
            except:
                self.t.cols = 1
                self.t.add_widget(ListHeader(text='Error al construir tabla'))

        else:
            self.t.cols = 1
            self.t.add_widget(ListHeader(text='Error: datos incorrectos'))

    def refresh(self):
        self.list_scrollable()

    def select_row(self, button):
        for cell in self.Rows[self.rowSelected - 1]:
            cell.color = [0, 0, 0, 1]
            cell.bcolor = [1, 1, 1, 1]
        self.rowSelected = int(button.id)
        for cell in self.Rows[self.rowSelected - 1]:
            cell.color = [1, 1, 1, 1]
            cell.bcolor = [0, 0, 0.8, 1]

class ListHeader(Button):
    bcolor = ListProperty([1, 1, 1, 1])

class ListCell(Label):
    bcolor = ListProperty([1, 1, 1, 1])

class DBWoker():
    def __init__(self):
        db_session.global_init("db/Tracking_drones.sqlite")
        self.inf = []

    def laodDataFromDB(self):
        session = db_session.create_session()
        session.inf = []
        for i in session.query(Storage).all():
            temp = [str(i.part.name), str(i.quantity), '0']
            self.inf.append(temp)

    def loadDataToDB(self, quan):
        session = db_session.create_session()
        temp = session.query(Storage).all()
        for i in range(len(temp)):
            temp[i].quantity = quan[i]
        session.commit()
        self.laodDataFromDB()
        c.data = [['Номенклатура', 'Остаток по данным ДБ', 'Фактическое количество']] + self.inf


# ----------------TEST------------------
if __name__ == "__main__":
    db_woker = DBWoker()
    db_woker.laodDataFromDB()
    from kivy.base import runTouchApp

    help(TextInput)
    c = List()
    print(db_woker.inf)
    c.data = [['Номенклатура', 'Остаток по данным ДБ', 'Фактическое количество']] + db_woker.inf
    runTouchApp(c)
