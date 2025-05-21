#TODO: coonsider using more sophisticated html embedding things

from fastapi.responses import HTMLResponse

from bs4 import BeautifulSoup
import string
import datetime

import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def construct_search_results_page(uris, thumbnails):
    assert len(uris) == len(thumbnails), "URIs and thumbnails must match in length"

    list_items = "\n".join(
        f'<li><a href="{uri}" target="_blank">{thumb}</a></li>'
        for uri, thumb in zip(uris, thumbnails)
    )

    html_template = f"""
    <html>
    <head>
        <title>Search Results</title>
    </head>
    <body>
        <h1>Search Results</h1>
        <ul>
            {list_items}
        </ul>
    </body>
    </html>
    """

    return HTMLResponse(content=html_template)

def construct_empty_search_page():
    html_template = f"""
    <html>
    <head>
        <title>Search Results</title>
    </head>
    <body>
        <h1>No documents matching the query!</h1>
    </body>
    </html>
    """
    
    return  HTMLResponse(content=html_template)

def construct_elastic_entry(input_raw_html: str, page_uri: str, page_title: str = None):
    
    soup = BeautifulSoup(input_raw_html, "html.parser")
    
    title = page_title if page_title is not None else (soup.title.string.strip() if soup.title and soup.title.string else f"Untitled:{page_uri}")
    
    text = soup.get_text()
    text = text.translate(str.maketrans('', '', string.punctuation))

    tokens = word_tokenize(text.lower())
    filtered_html = [w for w in tokens if w not in stopwords.words("english")]

    document = {
        "title":title,
        "date": datetime.datetime.now(),
        "author": "anonymous_cappy",
        "uri":page_uri,
        "content":filtered_html
    }
    
    return document
    
