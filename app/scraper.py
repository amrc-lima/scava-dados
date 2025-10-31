import httpx
from bs4 import BeautifulSoup
from typing import List, Optional
from urllib.parse import urljoin
from . import schemas
import asyncio # Necessário para o 'await asyncio.sleep'

# A URL base do site
BASE_URL = "http://books.toscrape.com/"
# MUDANÇA PRINCIPAL: Começamos na página 1 do catálogo para consistência.
START_URL = "http://books.toscrape.com/catalogue/page-1.html"

# Usaremos o caminho '/catalogue/' como base para a junção, garantindo que o caminho seja sempre o correto.
CATALOGUE_BASE = "http://books.toscrape.com/catalogue/"

async def _scrape_single_page(url: str) -> tuple[List[schemas.DatasetCreate], Optional[str]]:
    """
    Função auxiliar para raspar uma única página.
    Retorna (lista de datasets, URL relativa para a próxima página).
    """
    datasets_found = []
    next_page_relative_url = None

    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
            }
            response = await client.get(url, headers=headers, follow_redirects=True)
            response.raise_for_status() 

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Encontra todos os livros em um artigo com a classe 'product_pod'
        dataset_items = soup.select("article.product_pod")

        for item in dataset_items:
            try:
                title_element = item.select_one("h3 a")
                description_element = item.select_one("p.price_color")
                
                if title_element and description_element:
                    title = title_element["title"]
                    description = description_element.text.strip()
                    relative_url = title_element["href"]
                    
                    # Constrói a URL absoluta
                    source_url = urljoin(BASE_URL, relative_url)

                    dataset_data = schemas.DatasetCreate(
                        title=title,
                        description=description, 
                        source_url=source_url
                    )
                    datasets_found.append(dataset_data)

            except Exception as e:
                print(f"Erro ao parsear um item na página {url}: {e}")
        
        # Encontra o link para a próxima página (li.next)
        next_link_element = soup.select_one("li.next a")
        if next_link_element and 'href' in next_link_element.attrs:
            # Retorna o link relativo (ex: 'page-2.html')
            next_page_relative_url = next_link_element['href']

        return datasets_found, next_page_relative_url

    except httpx.HTTPStatusError as e:
        print(f"Erro de HTTP ao acessar {url}: {e}")
        return [], None
    except Exception as e:
        print(f"Erro inesperado no scraping de {url}: {e}")
        return [], None

# Esta é a função principal chamada pelo app/main.py
async def scrape_gov_data() -> List[schemas.DatasetCreate]:
    """
    Função principal que itera por todas as páginas do catálogo (alto-volume).
    """
    all_data = []
    current_page_url = START_URL
    pages_scraped = 0
    
    print(f"Iniciando raspagem de alto-volume do catálogo. Buscando até 1000 itens.")

    while True:
        print(f"Raspando página {pages_scraped + 1}: {current_page_url}")
        
        data_on_page, next_page_relative_url = await _scrape_single_page(current_page_url)
        all_data.extend(data_on_page)
        pages_scraped += 1
        
        if next_page_relative_url:
            # Não precisamos de lógica condicional (if/else) complicada. 
            # Como todas as páginas de 1 em diante estão em /catalogue/, a junção será correta.
            current_page_url = urljoin(CATALOGUE_BASE, next_page_relative_url)
            
            # Limitamos a 50 páginas (o máximo do site) para não rodar infinitamente
            if pages_scraped >= 50: 
                 print("Limite de 50 páginas atingido. Parando a raspagem.")
                 break
        else:
            print("Não foi encontrado link para a próxima página. Fim da raspagem.")
            break
            
        # Pausa assíncrona para ser cortês ao servidor e simular latência de rede
        await asyncio.sleep(0.1) 
            
    print(f"Raspagem de alto-volume concluída. Total de páginas: {pages_scraped}. Total de itens: {len(all_data)}.")
    return all_data