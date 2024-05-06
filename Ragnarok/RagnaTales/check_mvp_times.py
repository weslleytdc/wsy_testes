import pandas as pd
from playwright.sync_api import sync_playwright
import re
from datetime import datetime

def extrair_dados_div(div_content):
    # Expressões regulares para extrair os dados
    nome_pattern = r"^(.*?) \(id:"
    id_pattern = r"\(id:(.*?)\)"
    data_pattern = r"Sua curta vida acabou em (.*?)\."
    jogador_pattern = r"Graças á (\w+)"
    mapa_pattern = r"no mapa (.*?)\."
    
    # Extrair dados usando expressões regulares
    nome_match = re.search(nome_pattern, div_content)
    id_match = re.search(id_pattern, div_content)
    data_match = re.search(data_pattern, div_content)
    jogador_match = re.search(jogador_pattern, div_content)
    mapa_match = re.search(mapa_pattern, div_content)

    # Atribuir None caso o padrão não seja encontrado
    nome = nome_match.group(1) if nome_match else None
    id = id_match.group(1) if id_match else None
    data = data_match.group(1) if data_match else None
    jogador = jogador_match.group(1) if jogador_match else None
    mapa = mapa_match.group(1) if mapa_match else None

    return nome, id, data, jogador, mapa

def main():
    # Inicializar o Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        df_null_tag = 'true'

        while df_null_tag == 'true':

            # Acessar o site
            page.goto("https://ragnatales.com.br/db/mvp-tombs")

            # Espera até que a página esteja completamente carregada
            page.wait_for_load_state('networkidle')

            # Extrair as divs com a classe mx-auto
            divs = page.query_selector_all('.mx-auto')

            # Criar uma lista para armazenar os dados extraídos
            dados = []

            # Iterar sobre as divs e extrair os dados
            for div in divs:
                div_content = div.inner_text()
                # print(div_content)

                nome, id, data, jogador, mapa = extrair_dados_div(div_content)
                dados.append([nome, id, data, jogador, mapa])

            # Criar o DataFrame
            df = pd.DataFrame(dados, columns=['Nome', 'ID', 'Data', 'Jogador', 'Mapa'])        

            # excluir linhas nulas
            df = df.dropna()

            # Converter a coluna 'Data' para o formato datetime
            df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y, %H:%M')
            df['Data'] = df['Data'].astype(str)

            # Adicionando uma nova coluna com a data e hora atuais no formato de string
            df['extract_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Apenas saíra desse loob se não for nulo.
            if df.empty:
                df_null_tag = 'true'
            else:
                df_null_tag = 'false'
        

        # Imprimir o DataFrame
        print(df)

        browser.close()

        return df

if __name__ == "__main__":
    main()