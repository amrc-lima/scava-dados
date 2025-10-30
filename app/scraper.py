import httpx
from bs4 import BeautifulSoup
from typing import List
from . import schemas


TARGET_URL = "http://books.toscrape.com/"

async def scrape_gov_data() -> List[schemas.DatasetCreate]:
    """
    Raspa o site 'books.toscrape.com'
    (Agora com um site que funciona com nossas ferramentas)
    """
    print(f"Iniciando scraping de {TARGET_URL}...")
    
    datasets_found = []

    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
            }
            response = await client.get(TARGET_URL, headers=headers, follow_redirects=True)
            response.raise_for_status() 

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Cada livro está num <article class="product_pod">
        dataset_items = soup.select("article.product_pod")
        print(f"Encontrados {len(dataset_items)} itens de dataset.")

        for item in dataset_items:
            try:
                # O título está no 'title' de um link dentro de um <h3>
                title_element = item.select_one("h3 a")
                # O preço (nossa 'descrição') está num <p class="price_color">
                description_element = item.select_one("p.price_color")
                
                if title_element and description_element:
                    title = title_element["title"]
                    description = description_element.text.strip()
                    # O link do livro
                    source_url = TARGET_URL + title_element["href"]

                    dataset_data = schemas.DatasetCreate(
                        title=title,
                        description=description, # Vamos usar o preço como descrição
                        source_url=source_url
                    )
                    datasets_found.append(dataset_data)

            except Exception as e:
                print(f"Erro ao parsear um item: {e}")
        
        print(f"Scraping concluído. {len(datasets_found)} datasets formatados.")
        return datasets_found

    except httpx.HTTPStatusError as e:
        print(f"Erro de HTTP ao acessar {TARGET_URL}: {e}")
        return []
    except Exception as e:
        print(f"Erro inesperado no scraping: {e}")
        return []