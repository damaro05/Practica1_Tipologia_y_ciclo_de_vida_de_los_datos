import re
import time
import logging
import numpy as np
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from web_scraper.version import __appName__
from selenium.webdriver.common.action_chains import ActionChains


class WebCollector():
    def __init__(self, web_endpoint: str = '', output_csv_file: str = '', show_graphs: bool = False, driver_path: str = None):
        self.logger = self.setup_logggin()
        self.web_endpoint = web_endpoint
        self.show_graphs = show_graphs
        self.driver_path = driver_path
        self.output_csv_file = output_csv_file
        self.output_fig_path = "../doc/"

        self._main_window_handler = None
        self._secondary_window_handler = None
        self._tertiary_window_handler = None
        self.regex = re.compile('\d{4}S\d')

    # Logger initializier
    def setup_logggin(self) -> logging.Logger:
        log_format = "%(levelname)s %(asctime)s - %(message)s"
        logging.basicConfig(format=log_format, level=logging.INFO)
        logger = logging.getLogger(__appName__)
        return logger

    def load_all_available_dates(self, driver):
        # Find the time button
        time_elem = driver.find_element(by=By.ID, value="TIME")
        time_button = time_elem.find_element(By.TAG_NAME, value='button')

        # We save the main browser window
        self._main_window_handler = driver.current_window_handle
        # Focus on the elements we want to interact
        action = ActionChains(driver)
        action.move_to_element(time_button).perform()
        time_button.click()
        time.sleep(5)

        # Get the secondary window (pop up window)
        while not self._secondary_window_handler:
            for handle in driver.window_handles:
                if handle != self._main_window_handler:
                    self._secondary_window_handler = handle
                    break

        # We change the main window for the pop-up one
        driver.switch_to.window(self._secondary_window_handler)
        # We look for the button to enable all dates
        driver.find_element(by=By.ID, value="checkUncheckAllCheckboxTable").click()
        time.sleep(3)
        # And update the main table which is in the main window
        driver.find_element(by=By.ID, value="updateExtractionButton").click()
        time.sleep(3)
        # Change again to the main window
        driver.switch_to.window(self._main_window_handler)
        time.sleep(3)

    def create_data_table_as_dataframe(self, driver):
        # First we select the preview option so we can iterate over the whole dataset and not only the visible one
        nav_elem = driver.find_element(by=By.ID, value="nav")
        preview_button = nav_elem.find_element(By.CLASS_NAME, value="preview")
        preview_button.click()
        time.sleep(5)

        # Get the third window (pop-up)
        while not self._tertiary_window_handler:
            for handle in driver.window_handles:
                if handle != self._main_window_handler and handle != self._secondary_window_handler:
                    self._tertiary_window_handler = handle
                    break

        driver.switch_to.window(self._tertiary_window_handler)


        table_elem = driver.find_elements(by=By.TAG_NAME, value="table")
        self.logger.info(f"Number of sub-tables {len(table_elem)}")
        self.logger.info("Collecting values from the web site")
        set_columns = []
        table_df = pd.DataFrame()
        # loop over results
        for sub_table in table_elem:
            data = []
            # Remove the "TIME" and "GEO" header and split the table values
            table_values = sub_table.text.split("\n", 1)[1].split("\n")

            # Counting the number of year columns and adding an extra one for the countries
            num_year_cols = len(list(filter(self.regex.match, table_values))) + 1
            # Get the column names
            set_columns = table_values[0:num_year_cols]

            # Iterate over the cost values and jump every num_year_cols columns
            for i in range(num_year_cols, len(table_values), num_year_cols):
                tmp_value = []
                for j in range(0, num_year_cols):
                    tmp_value.append(table_values[i + j])
                data.append(tmp_value)
            # Create a temporal dataframe which is the sub table data
            temporal_df = pd.DataFrame(data=data, columns=set_columns)
            # Merge with the final dataframe
            if table_df.empty:
                table_df = temporal_df
            else:
                table_df = pd.merge(table_df, temporal_df, how="left", on=["GEO"])

        return table_df

    def generate_graph_spain(self, input_csv):
        input_df = pd.read_csv(input_csv, index_col=0)
        year_cols = [x for x in input_df.columns if "GEO" not in x]
        input_df[year_cols] = input_df[year_cols].replace(np.nan, np.float64(0))

        spain_values = input_df.loc[input_df["GEO"] == "Spain"]
        input_df.loc[input_df.index.max() + 1] = input_df[year_cols].mean().replace(np.nan, "European-Mean")
        input_df.iloc[input_df.index.max(), input_df.columns.get_loc('GEO')] = "European-Mean"

        mean_values = input_df.loc[input_df["GEO"] == "European-Mean"]

        spain_values = spain_values.append(mean_values)
        plot_values = spain_values[year_cols].T
        plot_values.columns = ["Spain", "European-Mean"]

        # mean_line = plot_values["European-Mean"].plot(linestyle='-', marker='o')
        plot = plot_values.plot(kind="bar", title="Comparativa de la evolución de precios de la energia Europa vs. España")
        plot.set_xlabel("Año")
        plot.set_ylabel("Precio kWh")
        fig = plot.get_figure()
        fig.savefig(self.output_fig_path + "figure_spain.png")

    def generate_graph_top_expensive(self, input_csv):
        input_df = pd.read_csv(input_csv, index_col=0)
        year_cols = [x for x in input_df.columns if "GEO" not in x]
        input_df[year_cols] = input_df[year_cols].replace(np.nan, np.float64(0))

        countries_to_filter = ["Ireland", "Liechtenstein", "Belgium",
                               "Germany (until 1990 former territory of the FRG)", "Luxembourg", "Italy"]
        input_df = input_df[input_df["GEO"].isin(countries_to_filter)]

        new_col_names = input_df["GEO"]

        plot_values = input_df[year_cols].T
        plot_values.columns = new_col_names

        plot = plot_values.plot(kind="bar", title="Comparativa de la evolución de precios de la energia en Europa para los paises más caros")
        plot.set_xlabel("Año")
        plot.set_ylabel("Precio kWh")
        fig = plot.get_figure()
        fig.savefig(self.output_fig_path + "figure_top_expensives.png")


    def start(self):
        self.logger.info("Starting the web data collector!")
        self.logger.info(f"The website used to do the scraping is: {self.web_endpoint}")

        try:
            self.logger.info("We create the firefox web driver from the path of the executable that we want (if needed)")
            driver = webdriver.Firefox(executable_path=self.driver_path) if self.driver_path else webdriver.Firefox()
            # Maximize the size of the browser to load more JS data
            driver.maximize_window()
            # Selenium don't contain API for request headers
            self.logger.info("Querying the website")
            driver.get(self.web_endpoint)

            self.logger.info("We load all possible years for the data")
            self.load_all_available_dates(driver)

            self.logger.info("We select the preview option to iterate over the table data")
            final_df = self.create_data_table_as_dataframe(driver)

            time.sleep(5)
            self.logger.info("Closing the browser")
            driver.quit()

            self.logger.info("Clean the output dataframe")
            year_cols = [x for x in final_df.columns if "GEO" not in x]
            # Removing strings in price columns and assigning NA for nonexistent ones
            final_df[year_cols] = final_df[year_cols].astype(str).applymap(
                lambda x: re.sub(r'[^0-9^\-\.]+', '', x)).replace('', np.nan).astype('float64')

            self.logger.info(f"Saving the final dataframe in {self.output_csv_file}")
            final_df.to_csv(self.output_csv_file)

            if self.show_graphs:
                self.logger.info("Generating graphs!")
                self.generate_graph_spain(self.output_csv_file)
                self.generate_graph_top_expensive(self.output_csv_file)

        except Exception as e:
            self.logger.warning(f"Exception during the data collection - [{e.args[0]}].")