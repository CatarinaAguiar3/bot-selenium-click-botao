"""
Módulo para detecção de novos elementos HTML na página
"""
from selenium.webdriver.common.by import By
import os
import time
class DetectorElementos:
    def __init__(self, arquivo_historico='elementos_historico.txt', arquivo_logs='logs.txt'):
        self.arquivo_historico = arquivo_historico
        self.arquivo_logs = arquivo_logs
        self.elementos_conhecidos = self._carregar_historico()

    def _carregar_historico(self):
        """Carrega o histórico de elementos do arquivo"""
        if not os.path.exists(self.arquivo_historico):
            self._salvar_logs(
                f"Arquivo de histórico não encontrado. Será criado na primeira execução.")
            return set()

        with open(self.arquivo_historico, 'r', encoding='utf-8') as f:
            linhas = f.read().strip().split('\n')
            elementos = set(linha for linha in linhas if linha)

        self._salvar_logs(f"Histórico carregado: {len(elementos)} elementos conhecidos")
        return elementos

    def _salvar_historico(self, elementos):
        """Salva o histórico de elementos no arquivo"""
        with open(self.arquivo_historico, 'w', encoding='utf-8') as f:
            for elemento in sorted(elementos):
                f.write(elemento + '\n')
        self._salvar_logs(f"Histórico salvo: {len(elementos)} elementos")

    def _salvar_logs(self, mensagem):
        """Salva mensagens de log no arquivo"""
        agora = time.strftime("%Y-%m-%d %H:%M:%S")
        linha = f"[{agora}] {mensagem}"
        print(linha)

        with open(self.arquivo_logs, 'a', encoding='utf-8') as f:
            f.write(linha + '\n')

    def _extrair_atributos(self, elemento):
        """Extrai todos os atributos relevantes de um elemento"""
        try:
            atributos = {
                'tag': elemento.tag_name,
                'id': elemento.get_attribute('id') or '',
                'class': elemento.get_attribute('class') or '',
                'name': elemento.get_attribute('name') or '',
                'value': elemento.get_attribute('value') or '',
                'title': elemento.get_attribute('title') or '',
                'text': elemento.text.strip() or '',
                'href': elemento.get_attribute('href') or '',
                'type': elemento.get_attribute('type') or '',
                'role': elemento.get_attribute('role') or '',
                'aria-label': elemento.get_attribute('aria-label') or '',
            }
            return atributos
        except Exception as e:
            return None

    def _gerar_assinatura(self, atributos):
        """Gera uma assinatura única para o elemento"""
        # Cria uma string com os atributos mais relevantes
        partes = []
        for chave in ['tag', 'id', 'class', 'name', 'title', 'text', 'type']:
            valor = atributos.get(chave, '')
            if valor:  # Só adiciona se tiver valor
                partes.append(f"{chave}:{valor}")

        assinatura = '|'.join(partes)
        return assinatura if assinatura else None

    def coletar_elementos(self, navegador):
        """Coleta todos os elementos da página"""
        self._salvar_logs("\nColetando elementos da página...")

        # Busca todos os elementos interativos e importantes
        seletores = [
            "button",
            "a",
            "input",
            "select",
            "textarea",
            "[role='button']",
            "[onclick]",
            ".slds-button",  # Classe comum em Salesforce
            "[title]",  # Elementos com title
        ]

        elementos_encontrados = []
        assinaturas_atuais = set()

        for seletor in seletores:
            try:
                elementos = navegador.find_elements(By.CSS_SELECTOR, seletor)
                for elemento in elementos:
                    atributos = self._extrair_atributos(elemento)
                    if atributos:
                        assinatura = self._gerar_assinatura(atributos)
                        if assinatura and assinatura not in assinaturas_atuais:
                            assinaturas_atuais.add(assinatura)
                            elementos_encontrados.append(
                                (assinatura, atributos, elemento))
            except Exception as e:
                self._salvar_logs(f"Erro ao buscar {seletor}: {e}")
                continue

        self._salvar_logs(
            f"Total de elementos únicos encontrados: {len(elementos_encontrados)}")
        return elementos_encontrados, assinaturas_atuais

    def detectar_novos_elementos(self, navegador):
        """
        Detecta elementos novos na página comparando com o histórico
        Retorna lista de elementos novos com seus atributos
        """
        elementos_encontrados, assinaturas_atuais = self.coletar_elementos(
            navegador)

        # Primeira execução: não há histórico
        if not self.elementos_conhecidos:
            self._salvar_logs("\nPRIMEIRA EXECUÇÃO - Criando baseline do histórico")
            self._salvar_historico(assinaturas_atuais)
            self.elementos_conhecidos = assinaturas_atuais
            self._salvar_logs("Baseline criado. Próximas execuções irão detectar novos elementos.")
            return []

        # Detecta elementos novos
        assinaturas_novas = assinaturas_atuais - self.elementos_conhecidos

        if not assinaturas_novas:
            self._salvar_logs("\nNenhum elemento novo detectado.")
            return []

        # Filtra os elementos novos
        elementos_novos = [
            (assinatura, atributos, elemento)
            for assinatura, atributos, elemento in elementos_encontrados
            if assinatura in assinaturas_novas
        ]

        self._salvar_logs(f"\nALERTA: {len(elementos_novos)} ELEMENTO(S) NOVO(S) DETECTADO(S)!")
        self._salvar_logs("=" * 80)

        for i, (assinatura, atributos, elemento) in enumerate(elementos_novos, 1):    
            self._salvar_logs(f"\nElemento Novo #{i}:")
            self._salvar_logs(f"   Tag: {atributos['tag']}")
            if atributos['id']:                
                self._salvar_logs(f"   ID: {atributos['id']}")
            if atributos['class']:                
                self._salvar_logs(f"   Classes: {atributos['class']}")
            if atributos['name']:                
                self._salvar_logs(f"   Name: {atributos['name']}")
            if atributos['title']:                
                self._salvar_logs(f"   Title: {atributos['title']}")
            if atributos['text']:                
                self._salvar_logs(f"   Texto: {atributos['text']}")
            if atributos['type']:                
                self._salvar_logs(f"   Type: {atributos['type']}")
            if atributos['href']:                
                self._salvar_logs(f"   Href: {atributos['href']}")
            if atributos['role']:               
                self._salvar_logs(f"   Role: {atributos['role']}")
            if atributos['aria-label']:              
                self._salvar_logs(f"   Aria-label: {atributos['aria-label']}")           
            self._salvar_logs(f"   Assinatura: {assinatura}")
            self._salvar_logs("-" * 80)

        # Atualiza o histórico com os novos elementos
        self.elementos_conhecidos.update(assinaturas_novas)
        self._salvar_historico(self.elementos_conhecidos)

        return elementos_novos

    def buscar_elemento_assumir(self, elementos_novos):
        """
        Busca nos elementos novos aquele que pode ser o botão 'Assumir'
        """
        for assinatura, atributos, elemento in elementos_novos:
            texto_lower = atributos['text'].lower()
            title_lower = atributos['title'].lower()

            if 'assumir' in texto_lower or 'assumir' in title_lower:
                self._salvar_logs(f"\nENCONTRADO! Elemento com 'Assumir' detectado:")
                self._salvar_logs(f"   Tag: {atributos['tag']}")
                self._salvar_logs(f"   Texto: {atributos['text']}")
                self._salvar_logs(f"   Title: {atributos['title']}")
                self._salvar_logs(f"   Classes: {atributos['class']}")
                return elemento

        return None