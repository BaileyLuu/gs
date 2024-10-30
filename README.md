# GSResRec (Google Scholar Resume/Research Records)

## Problem Description

Google Scholar allows authors to export their published works in BibTex/EndNote/RefMan/CSV but without including the number of citations (e.g Cited By #) for each of their work. What if a scholar put their selected articles (in citation format) on resume and want to know the total of citations?

## Project Structure
``` sh
. ├── .gitignore
  ├── extractText.py  
  ├── main.py 
  ├── README.md 
  └── requirements.txt
```

`extractText.py` will extract the works' titles and years from the given resume pdf file

## Installation (on Linux/Mac)
1. Clone the repository
    ```sh
    git clone https://github.com/BaileyLuu/gs.git
    cd gs
    ```

2. Create a virtual environment and activate it
    ```sh
    python -m venv .venv
    source .venv/bin/activate
    ```

3. Install the dependencies
    ```sh
    pip install -r requirements.txt
    ```

4. Provide your resume in pdf format on your local project folder and modify the file_name in main.py
    ```sh
    def main():
        file_name = 'your_resume.pdf'
    ```

## Usage
Start the application by providing the command line arguments (your resume pdf file and name of your google scholar profile)

```sh
python main.py 'your-resume.pdf' 'your-name'
```

## Approaches
1. Extract text from pdf using `pdfplumber` library.

2. Given the references/citation format (Author Name, Year, Article's Name, Journal, etc) in the extracted text, continue to extract the work's title using regular expression and clean the text by standardizing and removing punctuation and stop words.

3. Use `scholarly` module to retrieve author using *_search_author()_* and publication information from Google Scholar.

4. If the list of titles extracted from the resume are founded in the scholarly api data, retrieve the number of citations according to its titles. For text matching, `spaCy` sentence similarity feature is used to compare title from resume against title from scholarly api.

## Acknowledgement

```bibtex
@software{cholewiak2021scholarly,
  author  = {Cholewiak, Steven A. and Ipeirotis, Panos and Silva, Victor and Kannawadi, Arun},
  title   = {{SCHOLARLY: Simple access to Google Scholar authors and citation using Python}},
  year    = {2021},
  doi     = {10.5281/zenodo.5764801},
  license = {Unlicense},
  url = {https://github.com/scholarly-python-package/scholarly},
  version = {1.5.1}
}
```

See [scholarly](https://scholarly.readthedocs.io/en/stable/index.html) documentation for more details

