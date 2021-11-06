import requests

from bs4 import BeautifulSoup
from requests_html import HTMLSession, HTML

import urllib.request
import re
from selenium import webdriver
import time
import numpy as np
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

def main():
    print("Dentro main")
    # input_web_site = "https://ec.europa.eu/eurostat/databrowser/view/NRG_PC_204__custom_1504783/default/table"
    # input_web_site = "http://appsso.eurostat.ec.europa.eu/nui/submitViewTableAction.do"
    input_web_site = "http://appsso.eurostat.ec.europa.eu/nui/show.do?dataset=nrg_pc_204"
    # input_web_site = "https://ec.europa.eu/eurostat/databrowser/view/NRG_PC_204__custom_1504783/default/table?lang=en"

    #Set the header values of HTTP Request
    header = {}
    header['Origin'] = "http://appsso.eurostat.ec.europa.eu"
    header['Referer'] = "http://appsso.eurostat.ec.europa.eu/nui/show.do?dataset=nrg_pc_204"
    header['Content-Type'] = "application/x-www-form-urlencoded"
    # header['X-Requested-With'] = 'XMLHttpRequest'
    # header['x-elastica_gw'] = '2.43.0'

    print(f"URL: {input_web_site}")

    r = re.compile('\d{4}S\d')

    # run firefox webdriver from executable path of your choice
    driver = webdriver.Firefox()
    # driver.set_window_position(0, 0)
    # driver.set_window_size(2000, 2000)
    driver.maximize_window()

    # driver = webdriver.Firefox(executable_path='/Users/damaro/Desktop/lib/geckodriver')

    driver.get(input_web_site)
    # driver.execute_script("document.body.style.MozTransform='scale(0.5)'")
    # driver.execute_script("document.body.style.MozTransformOrigin='0 0'")

    # tmp = driver.find_element(by=By.ID, value="scrollyTable")
    tmp = driver.find_element(by=By.ID, value="TIME")
    print(f"Last value {tmp}")
    time_button = tmp.find_element(By.TAG_NAME, value='button')


    main_window_handler = driver.current_window_handle
    secondary_window_handler = None
    secondary_window_handler = None
    tertiary_window_handler = None

    action = ActionChains(driver)
    action.move_to_element(tmp).perform()

    # new web - time
    time_button.click()
    time.sleep(5)

    # Get the secondary window
    while not secondary_window_handler:
        for handle in driver.window_handles:
            if handle != main_window_handler:
                secondary_window_handler = handle
                break

    driver.switch_to.window(secondary_window_handler)
    driver.find_element(by=By.ID, value="checkUncheckAllCheckboxTable").click()
    time.sleep(3)
    driver.find_element(by=By.ID, value="updateExtractionButton").click()
    time.sleep(3)
    driver.switch_to.window(main_window_handler)
    time.sleep(3)

    # check button
    # checkUncheckAllTableHeader
    # update button
    # updateExtractionButton

    tmp = driver.find_element(by=By.ID, value="nav")
    print(f"Last value {tmp}")
    preview_button = tmp.find_element(By.CLASS_NAME, value="preview")
    preview_button.click()
    time.sleep(5)

    # Get the third window
    while not tertiary_window_handler:
        for handle in driver.window_handles:
            if handle != main_window_handler and handle != secondary_window_handler:
                tertiary_window_handler = handle
                break

    driver.switch_to.window(tertiary_window_handler)

    # Codigo bueno
    # tmp = driver.find_element(by=By.ID, value="scrollyTable")
    # for _ in range(10):
    #     tmp.click()
    #     # tmp.send_keys(Keys.SPACE)
    #     tmp.send_keys(Keys.ARROW_DOWN)
    #     time.sleep(0.1)
    #
    # tmp = driver.find_element(by=By.ID, value="scrollxTable")
    # for _ in range(10):
    #     tmp.click()
    #     tmp.send_keys(Keys.ARROW_RIGHT)


    results = driver.find_elements(by=By.TAG_NAME, value="table")

    print('Number of results', len(results))
    # data = []
    columns = []
    final_df = pd.DataFrame()

    # loop over results
    for result in results:
        data = []
        product_name = result.text
        # Remove the "TIME" and "GEO" header and split the table values
        table_values = product_name.split("\n", 1)[1].split("\n")
        # pd.DataFrame(data=table_values, columns=table_values[0:4], index=table_values[5::6])

        # Counting the number of year columns and adding an extra one for the countries
        num_cols = len(list(filter(r.match, table_values))) + 1
        columns.append(table_values[0:num_cols])

        set_columns = table_values[0:num_cols]

        for i in range(num_cols, len(table_values), num_cols):
            tmp_value = []
            for j in range(0, num_cols):
                tmp_value.append(table_values[i + j])

            data.append(tmp_value)

        temporal_df = pd.DataFrame(data=data, columns=set_columns)

        if final_df.empty:
            final_df = temporal_df
        else:
            final_df = pd.merge(final_df, temporal_df, how="left", on=["GEO"])

        # link = result.find_element_by_tag_name('a')
        # product_link = link.get_attribute("href")
        # append dict to array
        # data.append({"product": product_name, "link": product_link})


    time.sleep(5)
    driver.quit()

    # Clean the output dataframe
    year_cols = [x for x in final_df.columns if "GEO" not in x]
    final_df[year_cols] = final_df[year_cols].astype(str).applymap(lambda x: re.sub(r'[^0-9^\-\.]+', '', x)).replace('', np.nan).astype('float64')
    # final_df[year_cols].astype(str).applymap(lambda x: re.sub(r'[^0-9^\-\.]+', '', x)).replace('', np.float64(0)).astype('float64')
    # save the final dataframe
    final_df.to_csv("../csv/electricity_prices_for_household_consumers.csv")

    # try
    #
    #
    # except Exception as e:
    #     print(f"Error ----- {e}")

def main2():
    input_web_site = "https://www.eia.gov/totalenergy/data/annual/showtext.php?t=ptb0810"
    response = requests.get(input_web_site)
    # response = requests.post(input_web_site, data=paramsValues, headers=headersValues)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find('table')

    priceList = []
    currentIndex = 0
    table_tr = table.findAll("tr")
    for row in table_tr[3:len(table_tr)-6]:
        cells = row.findAll('td')
        # if (currentIndex > 0):
            # This is because exists rowspan, if not use the previous category
        year = cells[0].find(text=True)
        nominal = cells[1].find(text=True)
        real = cells[2].find(text=True)


        element = [year, nominal, real]
        priceList.append(element)
        # currentIndex = currentIndex + 1


    print(table.text)

def generate_graph(input_csv):
    input_df = pd.read_csv(input_csv, index_col=0)
    year_cols = [x for x in input_df.columns if "GEO" not in x]
    input_df[year_cols] = input_df[year_cols].replace(np.nan, np.float64(0))

    spain_values = input_df.loc[input_df["GEO"] == "Spain"]
    input_df.loc[input_df.index.max()+1] = input_df[year_cols].mean().replace(np.nan, "European-Mean")
    input_df.iloc[input_df.index.max(), input_df.columns.get_loc('GEO')] = "European-Mean"

    mean_values = input_df.loc[input_df["GEO"] == "European-Mean"]

    spain_values = spain_values.append(mean_values)
    plot_values = spain_values[year_cols].T
    plot_values.columns = ["Spain", "European-Mean"]

    plot_values.plot(kind="bar")
    plot_values["European-Mean"].plot(kind="line")

    # Media de precio por año en toda euro representa la tendencia global europa
    # un par diferenciados por paises
    print("Chao")


if __name__ == "__main__":
    print('Ejecutando como programa principal')
    # main()
    # main2()
    generate_graph("../csv/electricity_prices_for_household_consumers.csv")