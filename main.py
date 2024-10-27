from scholarly import scholarly, ProxyGenerator
import pandas as pd
import spacy
import extractText
from extractText import extract_text

pg = ProxyGenerator()
success = pg.FreeProxies()
scholarly.use_proxy(pg)

nlp = spacy.load('en_core_web_md')

def get_title_pubs(author_sections):
    dict_array = []
    for pub in author_sections['publications']:
        title = pub['bib']['title']
        num_citations = pub['num_citations']
        dict_array.append({"Title": str.title(title), "Citations": num_citations})

    return dict_array
   
def get_citations(title_pubs_arr, paper_title):
    paper_title = paper_title.lower()
    for title in title_pubs_arr:
        sent1 = nlp(title)
        sent2 = nlp(paper_title)
        similarity = sent1.similarity(sent2)
        if similarity > 0.96:
            pubs_obj = title_pubs_arr.get(title)
            title_pubs_arr.pop(title)
            print(title_pubs_arr.keys())
            return pubs_obj
        
    return title_pubs_arr.get(paper_title, 0)
   
def main():
    citations = extract_text()
    df = pd.DataFrame(citations)
    pd.set_option('display.max_columns', None)

    search_query = scholarly.search_author('Uyen Trang Nguyen')
    authorSections = scholarly.fill(next(search_query), sections=['publications', 'counts'])
    title_pubs_arr = get_title_pubs(authorSections) # an array of objects {'Title': 'Sample', 'Citations': 10}

    df2 = pd.DataFrame(title_pubs_arr)
    df_unique = df2.loc[df2.groupby('Title')['Citations'].idxmax()] # if there are duplicates, delete the object that has lower # of citations
    unique_title_pubs_arr = df_unique.to_dict(orient='records') # change the dataframe back to array of objects
    array_to_dict = {item['Title'].lower().replace('-', '‐'): item['Citations'] for item in unique_title_pubs_arr} # convert the array of objects to {}

    df['Citations'] = df['Title'].apply(lambda x: get_citations(array_to_dict,x)) # for every row of Title, find the associated key 'Title' and get its citations value (these data is from the scholarly api) 
    df.to_csv('Result.csv', index=False)

if __name__ == '__main__':
    main()
