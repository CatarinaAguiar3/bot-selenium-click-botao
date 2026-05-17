from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from dotenv import load_dotenv

def log(msg):
    agora = time.strftime("%Y-%m-%d %H:%M:%S")
    linha = f"[{agora}] {msg}"

    print(linha)



load_dotenv()

log("Iniciando script")
# Configurar o driver do Selenium (Chrome)
options = webdriver.ChromeOptions()
# Descomente a linha abaixo para modo headless (sem abrir a janela do navegador)
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
# Oculta mensagens de erro do console (como o DEPRECATED_ENDPOINT)
options.add_experimental_option("excludeSwitches", ["enable-logging"])
# Define o nível de log para mostrar apenas erros fatais
options.add_argument("--log-level=3")

navegador = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)
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
    log("Login realizado com sucesso.")

    botao_atualizar = espera30.until(
        EC.element_to_be_clickable((By.XPATH, "//button[@title='Atualizar']"))
    )
    botao_atualizar.click()
    log("Botão 'Atualizar' clicado.")
    time.sleep(60) # Proteção para não clicar mais de uma vez em menos de 1 minuto

    try:
        # botao_assumir = espera_maxima.until(
        #     EC.element_to_be_clickable(
        #         (
        #             By.XPATH,
        #             "//button[@title='Assumir'] | //a[contains(text(), 'Assumir') and @href]",
        #         )
        #     )
        # )

        botao_assumir = espera10.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.slds-button.slds-button_success.slds-button_stretch")
            )
        )

        # Procura qualquer elemento (*) que tenha "Assumir" no título ou texto
        # botao_assumir = espera_maxima.until(
        #     EC.element_to_be_clickable((By.XPATH,
        #         "//*[@title='Assumir' or contains(text(), 'Assumir')]"
        #     ))
        # )

        if botao_assumir.is_displayed():
            botao_assumir.click()
            log("Botão 'Assumir' encontrado e clicado.")
            time.sleep(5)
        else:
            log("Botão 'Assumir' não encontrado ou não clicável.")
    except:
        log("Tempo esgotado. Erro ao tentar encontrar o botão 'Assumir'.")

finally:
    navegador.quit()