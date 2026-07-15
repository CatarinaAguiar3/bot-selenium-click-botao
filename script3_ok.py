import os
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from detector_elementos import DetectorElementos

# CONFIGURAÇÕES INICIAIS ---------------
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


# -----------------------------------------
# ENCONTRAR E CLICAR BOTÃO ASSUMIR
# -----------------------------------------
def encontrar_assumir(navegador):
    """
    Procura o botão Assumir.
    Retorna o elemento se encontrar.
    Retorna None se não encontrar.
    """

    seletores_assumir = [
        "//button[contains(.,'Assumir')]",
        "//button[label[contains(.,'Assumir')]]",
        "//label[contains(.,'Assumir')]",
        "//*[contains(text(),'Assumir')]"
    ]

    for seletor in seletores_assumir:

        try:
            botao = WebDriverWait(navegador, 2).until(
                EC.element_to_be_clickable(
                    (By.XPATH, seletor)
                )
            )

            detector._salvar_logs(
                f"Botão Assumir encontrado usando: {seletor}"
            )

            return botao

        except Exception:
            continue


    detector._salvar_logs(
        "Botão Assumir não disponível."
    )

    return None

# -----------------------------------------
# EXECUÇÃO
# -----------------------------------------
try:
    # LOGIN
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

    # LOOP PRINCIPAL
    while True:

            # Atualizar página
            botao_atualizar = espera30.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@title='Atualizar']"))
            )
            botao_atualizar.click()

            detector._salvar_logs("Botão 'Atualizar' clicado.")
            # Proteção para não clicar mais de uma vez em menos de 1 minuto
            time.sleep(60)
            

            while True:

                try:

                    botao_assumir = encontrar_assumir(navegador)

                    if not botao_assumir:
                        detector._salvar_logs(
                            "Nenhum botão Assumir disponível."
                        )
                        break

                    detector._salvar_logs(
                        "Botão Assumir encontrado."
                    )

                    navegador.execute_script(
                        "arguments[0].click();",
                        botao_assumir
                    )

                    detector._salvar_logs(
                        "Botão Assumir clicado."
                    )

                    time.sleep(3)

                except Exception as e:

                    detector._salvar_logs(
                        f"Erro dentro do loop de Assumir: {e}"
                    )

                    break    


                # Espera o modal e fecha
                try:
                    # log: Aguardando modal...
                    detector._salvar_logs(
                        "Aguardando modal..."
                    )


                    # botão de fechar do modal
                    botao_fechar = navegador.find_elements(
                        By.CSS_SELECTOR,
                        ".slds-icon-utility-close"
                    )

                    if botao_fechar:
                        fechar_modal = WebDriverWait(navegador, 10).until(
                            EC.element_to_be_clickable(
                                (By.CSS_SELECTOR, ".slds-icon-utility-close")
                            )
                        )

                        navegador.execute_script(
                            "arguments[0].click();",
                            fechar_modal
                        )

                        #time.sleep(2)

                        detector._salvar_logs(
                            "Modal fechado."
                        )
                        time.sleep(5)
                    else:
                        detector._salvar_logs(
                            "Nenhum modal encontrado."
                        )    

                except Exception as e:
                    detector._salvar_logs(
                        f"Não foi possível fechar o modal: {e}"
                    )

                # Dá tempo para a lista atualizar
                time.sleep(2)

except Exception as e:
    detector._salvar_logs(f"Erro Geral: {e}")
        
