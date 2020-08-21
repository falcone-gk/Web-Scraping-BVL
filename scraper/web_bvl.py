"""
Se realizará todas las opciones posibles para extraer toda la información
posible de la página web de la Bolsa de Valores de Lima.
"""

from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

URL = "https://www.bvl.com.pe/neg_rv_alfa.html"

def get_table_info(rows_data):
    """
    Función que se encargará de obtener la información de las tablas que se
    desea según el nombre de la tabla.
    """

    data_matrix = []

    for row in rows_data:
        cells = row.find_all("td")
        line = []

        for cell in cells:
            value = cell.text

            if value == u'\xa0':
                line.append(np.nan)
            elif value == "":
                pass
            else:
                line.append(value)

        data_matrix.append(line)

    return data_matrix

class WebBVL:
    """
    Clase en la que se abrirá la página web de la Bolsa de Valores de Lima y en
    la que, a partir de ella, se extraerá la información dentro de la página.
    """

    def __init__(self, wait_secs=5):

        self.driver = webdriver.Chrome()
        self.wait_time = wait_secs
        self.driver.get(URL)

    def get_lastday_info(self):
        """
        Método para obtener toda la información hasta el momento del día.
        """

        table = self.driver.find_element_by_class_name("Tablas")
        row_headers = table.find_elements_by_tag_name("tr")[1]
        headers = row_headers.find_elements_by_tag_name("th")
        headers_list = list(map(lambda head: head.text, headers))
        headers_list.insert(4, "Moneda")

        table_bs = BeautifulSoup(table.get_attribute("outerHTML"),
                                 "html.parser")

        table_data = table_bs.find_all("tr")[2:]
        list_data = get_table_info(table_data)

        data_last_day = pd.DataFrame(list_data, columns=headers_list)

        self.driver.quit()

        return data_last_day

    def get_current_data_table(self):
        """
        Obtiene los datos de la tabla presente en la ubicación de la página
        actual.
        """

        table = self.driver.find_element_by_class_name("Tablas")
        table_bs = BeautifulSoup(table.get_attribute("outerHTML"),
                                 "html.parser")

        table_data = table_bs.find_all("tr")[2:]
        list_data = get_table_info(table_data)

        return list_data

    @staticmethod
    def _change_date_format(date):
        """
        Cambiar el formato de la columna de las fechas.
        """

        format_date = "%d/%m/%Y"
        try:
            date_formated = datetime.strptime(date, format_date).date()
            return date_formated

        except TypeError:
            return np.nan

    def get_data_firm(self, nem, init_date, end_date):
        """
        Método que obtendrá la información de solo una de las empresas sengún el
        rango de fechas que se desee.
        """

        init_date = datetime.strptime(init_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        # Escribir en el buscador el código de la empresa.
        search = self.driver.find_element_by_name("textNemonico")
        search.send_keys(nem)

        # Click en la lupa para filtrar la tabla de datos y obtener solamente el
        # link de la empresa de la cual se quiere la información.
        division = self.driver.find_element_by_id('divBloqueGris')
        image = division.find_element_by_tag_name("img")
        image.click()
        self.driver.implicitly_wait(self.wait_time)

        # Código para llegar a la página donde está la información de los precios
        # de cierre de la empresa.
        table = self.driver.find_element_by_class_name("Tablas")
        rows = table.find_elements_by_tag_name("tr")
        row = rows[2].find_elements_by_tag_name("td")
        text_link = row[1].text
        link = self.driver.find_element_by_link_text(text_link)
        link.click()
        self.driver.implicitly_wait(self.wait_time)

        # Navegando hacia la página donde están los resultados en una tabla.
        link = self.driver.find_element_by_link_text("Histórico de cotizaciones")
        link.click()
        self.driver.implicitly_wait(self.wait_time)

        # Obteniendo los datos del último mes.
        data = self.get_current_data_table()

        # Seleccionando la fecha inicial
        sel_init_month = self.driver.find_element_by_id("mesIni")
        path = "//option[@value = {}]".format(init_date.month)
        sel_init_month.find_element_by_xpath(path).click()

        sel_init_year = self.driver.find_element_by_id("anoIni")
        path = "//option[@value = {}]".format(init_date.year)
        sel_init_year.find_element_by_xpath(path).click()

        # Click en el botón buscar para según las fechas indicadas
        self.driver.find_element_by_name("button").click()
        self.driver.implicitly_wait(self.wait_time)

        # Obteniendo la data de la tabla después de hacer los cambios.
        data_total_range = self.get_current_data_table()

        header = ["Fecha", "Apertura", "Cierre", "Máxima", "Mínima",
                  "Promedio", "Cantidad Negociada", "Monto Negociado (S/.)",
                  "Fecha Anterior", "Cierre Anterior"]

        data.extend(data_total_range)
        data = pd.DataFrame(data, columns=header)
        data["Fecha"] = data["Fecha"].apply(self._change_date_format)
        data["Fecha Anterior"] = data["Fecha Anterior"].apply(self._change_date_format)
        data = data[(data["Fecha"] <= end_date) & (data["Fecha"] >= init_date)]
        data = data.set_index("Fecha")

        self.driver.quit()

        return data

    def exit_web(self):
        """
        Método para forzar cierre de la página web debido a problemas de
        conexión.
        """

        self.driver.quit()

def main():
    """
    Función para testear los avances del script.
    """

    web = WebBVL()
    web.get_data_firm("ALICORC1", "20/09/2018", "20/11/2019")

if __name__ == "__main__":
    main()
