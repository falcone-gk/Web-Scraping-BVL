"""
Creación de la interfaz gráfica para el uso de usuario que desea exportar los
datos de la Bolsa de Valores de Lima.
"""

import selenium
import wx
import wx.dataview as dv
import wx.adv as adv
import pandas as pd
from web_bvl import WebBVL

FIRMS = pd.read_excel("codes_bvl/codes.xlsx", index_col=0)

class GUIBvl(wx.Frame):
    """
    Interfaz para la creación del software.
    """

    def __init__(self):

        wx.Frame.__init__(self, None, title="Extracción de datos BVL",
                          style=wx.DEFAULT_FRAME_STYLE)

        self.main_box = wx.BoxSizer(wx.HORIZONTAL)
        self.list_panel = ListPanel(self)
        self.calendar = CalendarPanel(self)
        self.main_box.Add(self.list_panel, 0, wx.EXPAND|wx.ALL, 5)
        self.main_box.Add(self.calendar, 0, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(self.main_box)
        self.main_box.Fit(self)

class ListPanel(wx.Panel):
    """
    Panel en el que se mostrarán una lista con los nombres de las empresas.
    """

    def __init__(self, parent):

        wx.Panel.__init__(self, parent, size=(300, 500))

        self.parent = parent
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        title_txt = wx.StaticText(self, label="Empresas Disponibles")
        self.lbox = dv.DataViewListCtrl(self)
        self.lbox.AppendTextColumn(label="Nombre", width=200)
        self.lbox.AppendTextColumn(label="Código")

        data = list(FIRMS.values)

        for row in data:
            self.lbox.AppendItem(row)

        self.btn_data = wx.Button(self, label="Obtener datos")
        self.Bind(wx.EVT_BUTTON, self.get_data_total, self.btn_data)

        self.vbox.Add(title_txt, 0, wx.BOTTOM, 5)
        self.vbox.Add(self.lbox, 1, wx.EXPAND)
        self.vbox.Add(self.btn_data, 0, wx.TOP, 5)

        self.SetSizer(self.vbox)

    def get_data_total(self, event):
        """
        Obtiene la data de la BVL.
        """

        row = self.lbox.GetSelectedRow()
        item = self.lbox.GetValue(row, 1)
        calendar_panel = self.parent.calendar
        init_date = calendar_panel.get_init_date()
        end_date = calendar_panel.get_end_date()

        web_bvl = WebBVL("/usr/bin/chromedriver")

        try:
            data = web_bvl.get_data_firm(item, init_date, end_date)
            data.to_excel(item + ".xlsx")
        except selenium.common.exceptions.NoSuchElementException:
            msg = "Error en la señal. Revisar su conexión a internet e " \
                  "intentar de nuevo"

            cap = "Error de conexión"
            msg_error = wx.MessageDialog(self, msg, cap,
                                         style=wx.ICON_ERROR)

            msg_error.ShowModal()
            web_bvl.exit_web()

        event.Skip()

class CalendarPanel(wx.Panel):
    """
    Panel en el que irá tanto un calendario para indicar la fecha de inicio así
    como la fecha final de las que se desea obtener la información de la empresa
    indicada.
    """

    def __init__(self, parent):

        wx.Panel.__init__(self, parent, size=(300, -1))

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        init_txt = wx.StaticText(self, label="Fecha Inicial")
        self.init_calendar = adv.CalendarCtrl(self)

        end_txt = wx.StaticText(self, label="Fecha Final")
        self.end_calendar = adv.CalendarCtrl(self)

        self.vbox.Add(init_txt, 0, wx.BOTTOM, 5)
        self.vbox.Add(self.init_calendar, 1, wx.EXPAND|wx.BOTTOM, 10)
        self.vbox.Add(end_txt, 0, wx.BOTTOM, 5)
        self.vbox.Add(self.end_calendar, 1, wx.EXPAND)

        self.SetSizer(self.vbox)

    def get_init_date(self):
        """
        Retorna la fecha inicial del calendario especificado para esa función.
        """

        date = self.init_calendar.GetDate().Format("%d/%m/%Y")
        return date

    def get_end_date(self):
        """
        Retorna la fecha inicial del calendario especificado para esa función.
        """

        date = self.end_calendar.GetDate().Format("%d/%m/%Y")
        return date

def main():
    "Crea la interfaz gráfica"

    app = wx.App()
    frame = GUIBvl()
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
