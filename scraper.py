from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.expected_conditions import visibility_of_element_located as visibilidad
from selenium.webdriver.support.expected_conditions import element_to_be_clickable
from selenium.webdriver.common.by import By
from selenium import webdriver
from playsound import playsound
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
            time.sleep(3)
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
            respuestas = contenedor_chat.find_elements(By.TAG_NAME, 'li')
            if len(respuestas) > 2:
                break
            time.sleep(0.1)
        self.bot.append(respuestas[-1].text.strip().replace('\n', ' '))
        print('Dentro del chatbot')
        print(f'Bot: {self.bot[-1]}')
        return True

    def cheq_opciones(self):
        time.sleep(2)
        chat = self.find_element(By.XPATH, '//*[@id="bm-entries-ul"]')
        WebDriverWait(self, 30).until(
            lambda x: chat.find_elements(By.TAG_NAME, 'li')[-1].get_attribute('class') == 'bm-webchat-pills-li')

    def ingresar_datos_pers(self):
        """Ingresar datos personales al principio de la conversacion"""
        self.responder(os.getenv('DNI'))
        chat = self.find_element(By.XPATH, '//*[@id="bm-entries-ul"]')
        WebDriverWait(self, 15).until(
            lambda x: '(DDMMAAAA)' in chat.find_elements(By.TAG_NAME, 'li')[-1].text)
        self.actualizar_conversacion()
        self.responder(os.getenv('NACIMIENTO'))

    def actualizar_conversacion(self):
        """Anadir respuestas a la conversacion. Minimo una respuesta nueva"""
        chat = self.find_element(By.XPATH, '//*[@id="bm-entries-ul"]')
        filas_chat = chat.find_elements(By.TAG_NAME, 'li')
        texto = filas_chat[-2].text.strip().replace('\n', ' ')
        if texto == self.bot[-1]:
            time.sleep(0.5)
            return True
        self.bot.append(texto)
        print(f'Bot: {texto}')
        return True

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
        print(f'\tYo: {respuesta}')

        if respuesta == os.getenv('DNI'):
            return True

        self.cheq_opciones()
        self.actualizar_conversacion()
        return True

    def get_fechas(self):
        """Obtener fechas dentro de botones en la ultima fila de conversacion"""
        chat = self.find_element(By.XPATH, '//*[@id="bm-entries-ul"]')
        ult_fila = chat.find_elements(By.TAG_NAME, 'li')[-1]
        opciones = ult_fila.find_elements(By.TAG_NAME, 'button')
        fechas = set()
        for boton in opciones:
            if 'menu' in boton.text:
                continue
            fechas.add(boton.text)
        print(fechas)
        return fechas

    def buscar_turnos(self, fechas_pref: set[str]):
        """
        Loop para buscar turnos deseados
        :param fechas_pref: set con fechas a buscar, ej.: {'20/09/2030', '21/09/2030', ...}
        """
        while True:
            self.actualizar_conversacion()
            if 'empezamos?' in self.bot[-1] and self.yo[-1] != 'Turnos':
                self.responder('Turnos')
            elif 'deseada' in self.bot[-1] and self.yo[-1] != 'Nuevos turnos':
                self.responder('Nuevos turnos')
            elif 'sacar un turno' in self.bot[-1] and self.yo[-1] != 'Lic. de conducir':
                self.responder('Lic. de conducir')
            elif 'DNI:' in self.bot[-1] and self.yo[-1] != 'Si':
                self.responder('Si')
            elif 'licencia de conducir' in self.bot[-1] and self.yo[-1] != 'Original':
                self.responder('Original')
            elif 'dirección de mail' in self.bot[-1] and self.yo[-1] != os.getenv('CORREO'):
                self.responder(os.getenv('CORREO'))
            elif 'Qué día te conviene más' in self.bot[-1]:
                if self.get_fechas().isdisjoint(fechas_pref):
                    self.responder('Volver al menu')
                    print('Esperando 10 minutos para volver a intentar')
                    time.sleep(600)
                else:
                    print('Fecha encontrada!  Ctrl+C para terminar')
                    try:
                        playsound('ringtone.mp3')
                    except KeyboardInterrupt:
                        exit(0)
