# Practica 1 - Web Scraping

## Descripción
Este repositorio contiene la práctica 1 de la asignatura Tipología y ciclo de vida de los datos del Máster en Ciencia de Datos de la UOC. Se han aplicado tecnicas de web scraping en Python para generar un dataset con los precios de la electricidad en Europa.
El repositorio está compuesto por:
* **src:** Carpeta con el código fuente.
* **doc:** Contiene el documento con las respuestas de la actividad y los graficos generados.
* **csv:** Contiene el archivo final del dataset.
* **requerimientos.txt:** Archivo con las dependencias del proyecto.

## Miembros del equipo
La práctica ha sido realizada de manera individual por Sebastian Maya Hernández.

## Ficheros del código fuente
* **src/dataset_generator.py:** Es la entrada del programa, parsea los parametros de entrada y crea un objeto de la clase WebCollector. Los parametros de entrada son:
    * *web_endpoint:* Url de la página web.
    * *output_csv_file:* Path + nombre del archivo de salida o dataset.
    * *show_graphs:* Es un flag para activar la generación de gráficos.
    * *driver_path:* Es el custom path donde tenemos instalados los drivers de Selenium, por defecto no hace falta indicarlos.
* **src/web_scraper/collector.py:** Es la clase principal encargada de hacer el web scraping, limpieza de los datos y posterior guardado. También tiene una opción para generar gráficos de los datos.
* **src/web_scraper/version.py:** Es un archivo de configuración que contiene el nombre y la versión de la aplicación.
* **src/web_scraper/__init__.py:** Archivo que es parte obligatoria de un paquete de python.

## Como ejecutar el código
Primero, ejecute los siguientes comandos para instalar las dependencias y crear un entorno virtual.

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

También necesitamos instalar los drivers que utiliza Selenium en Python

    brew install geckodriver

Para generar el dataset ejecute:

    python3 src/dataset_generator.py --web_endpoint "xxx" --output_csv_file "xxx"

Asegúrese de cambiar los valores en *"xxx"* antes de ejecutarlo. A continuación tiene un ejemplo de ejecución:

    python3 src/dataset_generator.py --web_endpoint "http://appsso.eurostat.ec.europa.eu/nui/show.do?dataset=nrg_pc_204" --output_csv_file "../csv/output_dataset.csv"

Si desea generar gráficos añada la opción **--show_graphs**

    python3 src/dataset_generator.py --web_endpoint "http://appsso.eurostat.ec.europa.eu/nui/show.do?dataset=nrg_pc_204" --output_csv_file "../csv/output_dataset.csv" --show_graphs

## DOI de Zenodo

## Notas
Fíjese que en la ejecución pasamos los parametros junto a la url de la web, en este caso el dataset nrg_pc_204 que corresponde a los precios de la electricidad para los consumidores domésticos pero podríamos cambiar el valor de este parámetro y generar un dataset para otro tipo concreto de datos por ejemplo, el precio de la electricidad para los consumidores no domésticos o industriales.

## Recursos
1. Subirats, L., Calvo, M. (2019). Web Scraping. Editorial UOC.
2. Masip, D. (2010). El lenguaje Python. Editorial UOC.
3. Lawson, R. (2015). _Web Scraping with Python_. Packt Publishing Ltd. Chapter 2. Scraping the Data.