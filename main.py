from scholarly import scholarly, ProxyGenerator
import pandas as pd
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import unicodedata
import re
import time
import sys
import extractText
from extractText import extract_text

def initialize_proxy():
    pg = ProxyGenerator()   # Set up a ProxyGenerator object to use free proxies
    success = pg.FreeProxies(wait_time=70)  # This needs to be done only once per session
    scholarly.use_proxy(pg)
    return success

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
    sent2 = nlp(paper_title)    # since paper_title is consistent, use nlp() once for efficiency 
    for index, title in enumerate(title_pubs_arr):
        sent1 = nlp(title['Title'])
        similarity = sent1.similarity(sent2)
        if similarity > 0.97:
            citations = title['Citations']  # get matched both 'Citations' and 'URL' from scholarly api at once
            scholar_url = title['URL']  
            del title_pubs_arr[index]       # remove element to iterate array less times
            return pd.Series({"Citations": citations, "URL": scholar_url})
        
    return pd.Series({"Citations": 0, "URL": "N/A"})
   
def main():
    file_name = ""
    author_name = ""
    if len(sys.argv) < 3:
        print("Please provide your resume file and/or your name (if you have google scholar profile)\n\nexample command line:\tpython test.py sample.pdf 'you-name'")
    else:
        file_name = sys.argv[1]
        author_name = sys.argv[2] # if you have an existing google scholar profile
        # e.g. of command line      python main.py sample.pdf 'James Smith'    

        initialized_proxy = initialize_proxy()
        if initialized_proxy:
            beginning_time = time.time()
            citations = extract_text(file_name)
            df = pd.DataFrame(citations)
            pd.set_option('display.max_columns', None)
            df['Cleaned Title Resume'] = df['Title'].apply(remove_punctations)
            df.to_csv('cleaned_title_resume.csv', index=False)  # for your reference
            
            start_time = time.time()    # start timer    
            search_query = scholarly.search_author(author_name)
            authorSections = scholarly.fill(next(search_query), sections=['publications', 'counts'])
            title_pubs_arr = get_title_pubs(authorSections) # an array of objects {'Title': 'Sample', 'Citations': 10}
            end_time = time.time()      # end timer
            elapsed_time = end_time - start_time
            print("completed scholarly api", elapsed_time)

            start_time = time.time()    # start timer    
            for i in range(len(title_pubs_arr)):
                title_pubs_arr[i]['Title'] = remove_punctations(title_pubs_arr[i]['Title']) # clean the titles got from scholarly api
            end_time = time.time()      # end timer    
            elapsed_time = end_time - start_time
            print("completed cleaning scholarly api titles", elapsed_time)

            df2 = pd.DataFrame(title_pubs_arr)
            df2 = df2.loc[df2.groupby('Title')['Citations'].idxmax()] # if there are duplicates, delete the object that has lower # of citations
            df2.to_csv('cleaned_title_pubs_arr.csv', index=False)   # for your reference
            df2_array = df2.to_dict(orient='records') # change the dataframe back to array of objects
            
            start_time = time.time()    # start timer    
            df[['Citations', 'URL']] = df['Cleaned Title Resume'].apply(lambda x: get_citations_url(df2_array,x)) # for every row of Title, find the associated key 'Title' and get its citations/urls value (these data is from the scholarly api)
            end_time = time.time()      # end timer
            elapsed_time = end_time - start_time
            print("completed getting citations and urls", elapsed_time)

            df.drop('Cleaned Title Resume',axis='columns', inplace=True)
            df.to_excel(f'{file_name}_result.xlsx', index=False)
            ending_time = time.time()
            total_time = ending_time - beginning_time
            print("Total Time: ", total_time )

if __name__ == '__main__':
    main()
