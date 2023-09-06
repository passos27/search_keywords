# Importando bibliotecas necessárias
# 'os' para interação com o sistema operacional, 'requests' para fazer requisições HTTP,
# 'BeautifulSoup' para análise de HTML, 'urljoin' para manipulação de URLs,
# 'PdfFileReader' para leitura de PDFs, 'BytesIO' para manipulação de bytes e 'datetime' para data e hora.
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PyPDF2 import PdfFileReader
from io import BytesIO
from datetime import datetime

# Definição da função 'crawl_website' que rastreia um site em busca de palavras-chave
def crawl_website(base_url, keywords, max_pages=100):
    # Inicializando conjuntos para armazenar links visitados e links a serem visitados
    # Isso evita a visita repetida a páginas já analisadas.
    visited_links = set()
    links_to_visit = set([base_url])
    pages_visited = 0
    keyword_links = set()

    # Loop principal: continua enquanto houver links para visitar e o número máximo de páginas não for atingido
    while links_to_visit and pages_visited < max_pages:
        # Pega o próximo link da fila para visitar
        current_link = links_to_visit.pop()

        # Tentativa de fazer uma requisição HTTP ao link
        # Se falhar (por exemplo, página não encontrada), o loop continua com o próximo link
        try:
            print(f'Verificado: {current_link}...')
            response = requests.get(current_link)
            response.raise_for_status()
        except (requests.HTTPError, requests.ConnectionError):
            continue

        # Incrementa o contador de páginas visitadas
        pages_visited += 1

        # Tentativa de analisar o HTML da página
        # Se falhar, o loop continua com o próximo link
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error parsing HTML at {current_link}: {e}")
            continue

        # Verifica se alguma das palavras-chave está presente no texto da página
        # Se sim, adiciona o link ao conjunto 'keyword_links'
        if any(keyword.lower() in soup.get_text().lower() for keyword in keywords):
            print(f'Keywords {keywords} found at {current_link}')
            keyword_links.add(current_link)

        # Procura todos os links na página e os adiciona à fila de links a serem visitados
        for link in soup.find_all('a'):
            absolute_link = urljoin(base_url, link.get('href'))

            # Verifica se o link é um arquivo PDF
            if absolute_link.endswith('.pdf'):
                try:
                    response = requests.get(absolute_link)
                    # Ignora arquivos PDF maiores que 10MB para economizar tempo e recursos
                    if response.content_length > 10_000_000:
                        continue

                    # Lê o conteúdo do PDF e procura pelas palavras-chave
                    with BytesIO(response.content) as open_pdf_file:
                        read_pdf = PdfFileReader(open_pdf_file)
                        for page_number in range(read_pdf.getNumPages()):
                            page = read_pdf.getPage(page_number)
                            content = page.extractText()
                            if any(keyword.lower() in content.lower() for keyword in keywords):
                                print(f'Keywords {keywords} found in PDF at {absolute_link}')
                                keyword_links.add(absolute_link)
                except:
                    continue

            # Se o link ainda não foi visitado e pertence ao mesmo domínio base, adiciona à fila
            elif base_url in absolute_link and absolute_link not in visited_links:
                links_to_visit.add(absolute_link)

        # Marca o link atual como visitado
        visited_links.add(current_link)

    # Salva os links visitados e os links onde as palavras-chave foram encontradas em arquivos de texto
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    with open(f'visited_links_{date_str}.txt', 'w') as f:
        for link in visited_links:
            f.write(link + '\n')

    with open(f'keyword_links_{date_str}.txt', 'w') as f:
        for link in keyword_links:
            f.write(link + '\n')

# Inicializa as palavras-chave e o URL base para o rastreamento
keywords = ['palavra chave aqui']  # Substitua por suas palavras-chave
base_url = '#'  # Substitua pelo URL do site desejado

# Chama a função de rastreamento com o URL base, palavras-chave e limite de páginas
crawl_website(base_url, keywords, max_pages=10000)  # Definir o limite de páginas visitadas 
