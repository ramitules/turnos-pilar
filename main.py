from scraper import WebScraper
import time


if __name__ == '__main__':
    scraper = WebScraper()
    scraper.pagina_municipio()
    scraper.autogestion_turnos()
    scraper.actualizar_conversacion()
    if 'Ingresa tu DNI' in scraper.bot[-1]:
        scraper.responder('dni')
    if '(DDMMAAAA)' in scraper.bot[-1]:
        scraper.responder('fecha de nacimiento')
