from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.expected_conditions import visibility_of_element_located as visibilidad
from selenium.webdriver.support.expected_conditions import element_to_be_clickable
from selenium.webdriver.common.by import By
from selenium import webdriver
import os
import time


class WebScraper(webdriver.Chrome):
    def __init__(self, headless: bool = True):
        self.__headless = headless
        self.opciones = self.__config_opc()
        super().__init__(self.opciones, Service())
        self.set_window_size(1900, 1050)
        self.bot = list()
        self.yo = list()

    def __config_opc(self):
        """Default options for Chrome"""
        download_dir = os.getcwd()  # Current directory is where files will be downloaded

        o = webdriver.ChromeOptions()

        if self.__headless:
            o.add_argument('--headless=new')
        o.add_argument('--disable-web-security')
        o.add_argument('--disable-notifications')
        o.add_argument(f'--remote-debugging-port=1111')
        o.add_argument('--ignore-certificate-errors')
        o.add_argument('--no-sandbox')
        o.add_argument('--no-default-browser-check')
        o.add_argument('--no-first-run')
        o.add_argument('--no-proxy-server')
        o.add_argument('--disable-blink-features=AutomationControlled')

        exp_options = ['enable-automation', 'ignore-certificate-errors']

        prefs = {
            'profile.default_content_setting_values.notifications': 2,
            'credentials_enable_service': False,
            'download.default_directory': download_dir
        }

        o.add_experimental_option('excludeSwitches', exp_options)
        o.add_experimental_option('prefs', prefs)

        print('Para debuggear, ingrese desde Chrome a "chrome://inspect" y configure "localhost:1111')
        return o

    def pagina_municipio(self):
        """Funcion para acceder a la pagina del municipio"""
        pagina = 'https://pilar.gov.ar'
        self.get(pagina)
        print('Dentro de la pagina')
        return True

    def autogestion_turnos(self):
        """Acceder a la autogestion de turnos"""
        # En el caso de Pilar, se realiza a traves de un chatbot
        # Acceder al chatbot dentro de un iframe
        self.switch_to.frame(self.find_element(By.TAG_NAME, "iframe"))
        ubi = '//*[@id="wc-button"]'
        try:
            WebDriverWait(self, 10).until(element_to_be_clickable((By.XPATH, ubi)))
            self.find_element(By.XPATH, ubi).click()
        except TimeoutException:
            print('No se ha podido encontrar el boton de chatbot')
            return False
        # Buscar contenedor de conversacion (DIV)
        ubi = '//*[@id="bm-entries-ul"]'
        try:
            WebDriverWait(self, 5).until(visibilidad((By.XPATH, ubi)))
            contenedor_chat = self.find_element(By.XPATH, ubi)
        except TimeoutException:
            print('No se ha podido encontrar la conversacion')
            return False
        # Asegurar que el bot esta activo
        while True:
            if len(contenedor_chat.find_elements(By.TAG_NAME, 'li')) > 2:
                break
            time.sleep(0.1)
        print('Dentro del chatbot')
        return True

    def actualizar_conversacion(self):
        """Anadir respuestas a la conversacion"""
        respuestas = len(self.bot)
        secs = int(time.time())
        # Capturar los mensajes
        chat = self.find_element(By.XPATH, '//*[@id="bm-entries-ul"]')
        while True:
            filas_chat = chat.find_elements(By.TAG_NAME, 'li')
            for fila in filas_chat:
                # Si existe una respuesta y se ha esperado otra respuesta durante mas de tres segundos, volver
                if len(self.bot) == respuestas:
                    # Si no hay respuesta, reiniciar segundero
                    secs = time.time()
                elif int(secs - time.time()) > 3:
                    # Si existe una o mas respuestas y se ha esperado otra durante mas de tres segundos, volver
                    return True
                ubicacion = fila.get_attribute('style')
                if not ubicacion:
                    # Una fila donde solo se muestra fecha y hora u opciones
                    continue
                ubicacion = ubicacion.split('-')[-1].replace(';', '').strip()
                texto = fila.text.strip()
                # Guardar chat en listas
                if ubicacion == 'start':
                    if texto in self.bot:
                        continue
                    self.bot.append(texto)
                elif ubicacion == 'end':
                    if texto in self.yo:
                        continue
                    self.yo.append(texto)
                else:
                    continue

    def responder(self, respuesta: str):
        """Responderle al chatbot"""
        # Ingresar texto
        self.find_element(By.XPATH, '//*[@id="wc-textarea"]').send_keys(respuesta)
        boton = '/html/body/div/div/div/div[4]/div[2]/div/button'
        try:
            WebDriverWait(self, 3).until(element_to_be_clickable((By.XPATH, boton)))
        except TimeoutException:
            print('No se ha encontrado el boton para enviar mensaje')
            return False
        self.find_element(By.XPATH, boton).click()
        self.yo.append(respuesta)
        return True


if __name__ == '__main__':
    ws = WebScraper()
    ws.pagina_municipio()
    ws.autogestion_turnos()
    input('ENTER cuando termine el testeo')
    ws.quit()
