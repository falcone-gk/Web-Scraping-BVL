"""
Código para obtener los códigos de las empresas que se registran en la bolsa de
valores de lima.
"""

import time
from selenium.webdriver import Chrome
from bs4 import BeautifulSoup
import pandas as pd


def get_codes():
    """
    Función que obtendrá todos los códigos con links disponibles.
    """

    url = "https://www.bvl.com.pe/neg_rv_alfa.html"
    driver = Chrome("/usr/bin/chromedriver")
    driver.get(url)

    driver.find_element_by_class_name("todas").click()
    driver.implicitly_wait(20)

    data_codes = {"name": [], "nem": []}
    cols = list(data_codes.keys())
    table = driver.find_element_by_class_name("Tablas")
    bs_table = BeautifulSoup(table.get_attribute("outerHTML"), "html.parser")
    rows = bs_table.find_all("tr")[2:]

    links = list(map(lambda link: link.text, bs_table.find_all("a")))

    for row in rows:
        cells = row.find_all("td")
        for i, cell in enumerate(cells):
            try:
                if i == 0:
                    pass
                else:
                    value = cell.text
                    data_codes[cols[i-1]].append(value)

            except IndexError:
                break

    data_fr = pd.DataFrame(data_codes)
    data = data_fr[data_fr["name"].isin(links)]

    data.to_excel("codes.xlsx")
    print("Data exportada correctamente!")

    time.sleep(10)

    driver.quit()

def main():
    "Correr la función"

    get_codes()

if __name__ == "__main__":
    main()
