import arxiv
import itertools
import json
from datetime import datetime
import os

## Crea la carpeta donde se almacenan los ficheros JSON si no existe. ##

os.makedirs("papers_jsonFiles", exist_ok=True)


## Definición de variables. ##

elements = ['published','title','authors','summary','primary_category',
            'categories','link','pdf_url']


## Creación del cliente ##

def create_client():
    """
    Crear el cliente de arXiv.
    """
    try:
        client = arxiv.Client()

    except:
        print("Error desplegando el cliente.")
    
    if client:

        return client

## Utilidades ##

def arxiv_search(client, max_results, query):
    """
    Función para realizar las distintas consultas a la API de arXiv.
    """

    search = arxiv.Search(
    query = query,
    max_results = max_results,
    sort_by = arxiv.SortCriterion.SubmittedDate
    )

    results = client.results(search)

    return results

## Conocer los campos que devuelve la llamada ##

def result_fields(results):
    """
    Devuelve el listado de campos devueltos por la llamada API.
    """

    resultsList = list(results)

    if resultsList:
        first_result = resultsList[0]
        all_items = vars(first_result)

        keys = list(all_items.keys())
        for i, key in enumerate(keys,1):
            print(f"{i}: {key}")

def papers_processor(results, fields=elements):
    """
    Selección de campos y formateo mejorado.
    """

    papers = []

    for i, result in enumerate(results, 1):
        
        paper = {
            'id': i,
            'arxiv_id': result.entry_id.split('/')[-1],
            'processed_date': datetime.now().isoformat()
            }

        for field in fields:
            if hasattr(result, field):
                value = getattr(result, field)

                if field == 'authors':
                    paper[field] = [author.name for author in value]

                elif field in ['published']:
                    paper[field] = value.isoformat()
                else:
                    paper[field] = value
            
            else:
                paper[field] = None
        
        papers.append(paper)
    
    return papers

def save_papers(papers, filename=None):
    """
    Guardar papers en JSON.
    """

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"papers_{timestamp}.json"
    
    path = f'papers_jsonFiles/{filename}'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)
    
    print(f"Guardados {len(papers)} papers en {filename}")

if __name__ == '__main__':

    client = create_client()

    results = arxiv_search(client, 10, ["AI"])

    papers = papers_processor(results, elements)

    save_papers(papers)

        






