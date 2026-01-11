import arxiv
import itertools
import json
from datetime import datetime

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

""" resultsList = list(results)

if resultsList:
    first_result = resultsList[0]
    all_items = vars(first_result)

    keys = list(all_items.keys())
    for i, key in enumerate(keys,1):
        print(f"{i}: {key}") """

def papers_processor(results, fields=elements):
    """
    Selección de campos y formateo.
    """

    results = results
    papers = []

    for i, result in enumerate(results, 1):
        
        paper = {'id': i}

        for field in fields:
            if hasattr(result, field):
                value = getattr(result, field)

                paper[field] = value
        
        papers.append(paper)
    
    return papers

if __name__ == '__main__':

    client = create_client()

    results = arxiv_search(client, 10, "AI")

    print(results)

    papers = papers_processor(results, elements)

    print(papers)

        






