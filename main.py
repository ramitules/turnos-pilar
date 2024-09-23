from scraper import WebScraper
from bienvenida import bienvenida, fechas_deseadas
import os
import dotenv


if __name__ == '__main__':
    if 'config.env' not in os.listdir():
        if not bienvenida():
            exit(1)
    dotenv.load_dotenv('config.env')
    fechas_preferencia = set(fechas_deseadas().split(' - '))
    scraper = WebScraper(headless=True)
    scraper.pagina_municipio()
    scraper.autogestion_turnos()
    scraper.ingresar_datos_pers()
    scraper.buscar_turnos(fechas_preferencia)
