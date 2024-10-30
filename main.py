from scholarly import scholarly, ProxyGenerator
import pandas as pd
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import unicodedata
import re
import extractText
from extractText import extract_text

pg = ProxyGenerator()
success = pg.FreeProxies()
scholarly.use_proxy(pg)

nlp = spacy.load('en_core_web_md')

def remove_punctations(text):
    standardized_text = unicodedata.normalize("NFKC", text)
    cleaned_text = re.sub(r"[\u2010-\u2015:;.,!?\"'(){}\[\]<>@#%^&*_+=|\\/]", " ", standardized_text).replace("  ", " ").replace("-", " ")
    doc = nlp(cleaned_text)
    removed_stop_words = [token.text for token in doc if not token.is_stop]
    return ' '.join(removed_stop_words)

scholar_id = ""
def get_title_pubs(author_sections):
    dict_array = []
    scholar_id=author_sections['scholar_id']
    for pub in author_sections['publications']:
        title = pub['bib']['title']
        num_citations = pub['num_citations']
        author_pub_id = pub['author_pub_id']
        url = f"https://scholar.google.ca/citations?view_op=view_citation&hl=en&user={scholar_id}&citation_for_view={author_pub_id}"
        dict_array.append({"Title": title.lower(), "Citations": num_citations, "URL": url})

    return dict_array
   

def get_citations_url(title_pubs_arr, paper_title):
    paper_title = paper_title.lower()
    for title in title_pubs_arr:
        sent1 = nlp(title)
        sent2 = nlp(paper_title)
        similarity = sent1.similarity(sent2)
        if similarity > 0.96:
            pubs_obj = title_pubs_arr.get(title)
            title_pubs_arr.pop(title)
            return pubs_obj
        
    return title_pubs_arr.get(paper_title, 0)
   
def main():
    citations = extract_text()
    df = pd.DataFrame(citations)
    pd.set_option('display.max_columns', None)
    df['Cleaned Title Resume'] = df['Title'].apply(remove_punctations)
    df.to_csv('cleaned_title_resume.csv', index=False)

    search_query = scholarly.search_author('Uyen Trang Nguyen')
    authorSections = scholarly.fill(next(search_query), sections=['publications', 'counts'])
    title_pubs_arr = get_title_pubs(authorSections) # an array of objects {'Title': 'Sample', 'Citations': 10}
    for i in range(len(title_pubs_arr)):
        title_pubs_arr[i]['Title'] = remove_punctations(title_pubs_arr[i]['Title']) # clean the titles got from scholarly api

    df2 = pd.DataFrame(title_pubs_arr)
    df2 = df2.loc[df2.groupby('Title')['Citations'].idxmax()] # if there are duplicates, delete the object that has lower # of citations
    df2.to_csv('cleaned_title_pubs_arr.csv', index=False)
    df2_array = df2.to_dict(orient='records') # change the dataframe back to array of objects
    df2_dict = {item['Title']: item['Citations'] for item in df2_array} # convert the array of objects to {}

    df['Citations'] = df['Cleaned Title Resume'].apply(lambda x: get_citations_url(df2_dict,x)) # for every row of Title, find the associated key 'Title' and get its citations value (these data is from the scholarly api)
    scholar_url_dict = {item['Title']: item['URL'] for item in df2_array} # convert the array of objects to {}
    df['URL'] = df['Cleaned Title Resume'].apply(lambda x: get_citations_url(scholar_url_dict,x)) 

    df.to_csv('Result.csv', index=False)

if __name__ == '__main__':
    main()
