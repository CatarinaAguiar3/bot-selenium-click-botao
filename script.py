import os
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from detector_elementos import DetectorElementos

detector = DetectorElementos() 

load_dotenv()

detector._salvar_logs("Iniciando script")
# Configurar o driver do Selenium (Chrome)
options = webdriver.ChromeOptions()
# Descomente a linha abaixo para modo headless (sem abrir a janela do navegador)
#options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument("--start-maximized")
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
# Oculta mensagens de erro do console (como o DEPRECATED_ENDPOINT)
options.add_experimental_option("excludeSwitches", ["enable-logging"])
# Define o nível de log para mostrar apenas erros fatais
options.add_argument("--log-level=3")

navegador = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)
# navegador.maximize_window()
# navegador.set_window_size(1280, 700)
navegador.get(os.getenv("SITE"))
espera10 = WebDriverWait(navegador, 10)
espera30 = WebDriverWait(navegador, 30)

try:
    input_username = espera10.until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    input_username.send_keys(os.getenv("USER"))

    input_password = espera10.until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    input_password.send_keys(os.getenv("PASSWORD"))

    botao_login = espera10.until(EC.element_to_be_clickable((By.ID, "Login")))
    botao_login.click()

    time.sleep(2)
    if navegador.title != os.getenv("TITLE_PAGE"):
        detector._salvar_logs("Login realizado com sucesso.")
    else:
        error_login = WebDriverWait(navegador, 0).until(
            EC.presence_of_element_located((By.ID, "error"))
        )
        raise Exception(error_login.text)

    while True:
        botao_atualizar = espera30.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@title='Atualizar']"))
        )
        botao_atualizar.click()
        detector._salvar_logs("Botão 'Atualizar' clicado.")
        # Proteção para não clicar mais de uma vez em menos de 1 minuto
        
        elementos_novos = detector.detectar_novos_elementos(navegador)
        
        time.sleep(60)

        # Se encontrou elementos novos, tenta localizar o botão "Assumir"
        if elementos_novos:
            botao_assumir = detector.buscar_elemento_assumir(elementos_novos)

            if botao_assumir:
                try:
                    if botao_assumir.is_displayed() and botao_assumir.is_enabled():
                        botao_assumir.click()
                        detector._salvar_logs("Botão 'Assumir' clicado com sucesso!")
                        time.sleep(5)
                    else:
                        detector._salvar_logs("Botão 'Assumir' encontrado mas não está clicável.")
                except Exception as e:
                    detector._salvar_logs(f"Erro ao clicar no botão 'Assumir': {e}")
            else:
                detector._salvar_logs("Elementos novos detectados, mas nenhum é o botão 'Assumir'.")
        else:
            detector._salvar_logs("Nenhum elemento novo na página.")
except Exception as e:
    detector._salvar_logs(f"Erro: {e}")
