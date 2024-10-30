import pdfplumber
import re
import pandas as pd

def extract_text(file_name):
    citations = []
    with pdfplumber.open(file_name) as pdf:
        for page in pdf.pages:
            text = page.extract_text().replace('\n', ' ')
            pattern = r'.\s\((?P<year>\d{4})\). (?P<title>[\w\s:,\-/]+). (?P<journal>[\w\s\-/]+)'
            # an example of this pattern is '. (2024). A Survey of Machine Learning in Anti-Money Laundering. IEEE Access.
            # exactly 4 digits for the year within the () and for the title it can have words, spaces, colons, commas, dash, slashes
            # and for the journal it can have words, spaces, and dashes.

            matches = re.findall(pattern, text)
            
            for match in matches:
                citation = {
                    "Title": match[1].lower(),
                    "Year": match[0],
                }
                citations.append(citation)
    return citations


       