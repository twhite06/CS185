import wikipedia as wiki
import requests
import string
import openai
from bs4 import BeautifulSoup

def getWord(lang, searchInput):
    ui = string.capwords(searchInput)
    lists = ui.split()
    word = "_".join(lists)

    if word == "QUIT":
        return 0
    else:
            return "https://" + lang + ".wikipedia.org/wiki/" + word


def get_paragraphs(soup):
    paragraphs = soup("p")
    paragraphs_texts = [p.text for p in paragraphs]
    # with open('output.txt', 'w', encoding='utf-8') as f:
    #     for paragraph in paragraphs_texts:
    #         f.write(paragraph + '\n\n')
    return paragraphs_texts

def get_paragraphs_navVer(soup, toc_section):
    # Find toc section in html
    toc_section.replace(' ', '_')
    print(toc_section)
    print("=============")
    print("=============")
    print("=============")
    target_section = soup.find('span', {'class': 'mw-headline', 'id': toc_section})
    
    if not target_section:
        return []

    # Get the parent <h2> tag of the target_section
    h2_tag = target_section.find_parent('h2')
    print(h2_tag)


    # Initialize an empty list to store the paragraph texts
    paragraphs_texts = []
    
    # Iterate through the next elements starting from the found <h2> tag
    current_element = target_section.find_next_sibling()
    print(current_element)
    while current_element:
        print(current_element)
        # Check if the current element is an <h2> tag
        if current_element.name == 'h2':
            break

        # If the current element is a <p> tag, add its text to the list
        if current_element.name == 'p':
            paragraphs_texts.append(current_element.text)

        # Move to the next element
        current_element = current_element.find_next_sibling()

    print(paragraphs_texts)
    return paragraphs_texts


def wikiSearch(url, toc_section=''):
    if url == 0:
        return ''
    else:
        searchReq = requests.get(url)
        soup = BeautifulSoup(searchReq.content, "html.parser")
        if toc_section == '':
            paragraphs = get_paragraphs(soup)
            navbar_elems = get_navbar_elems(soup)
            return paragraphs, navbar_elems
        else:
            paragraphs = get_paragraphs_navVer(soup, toc_section)
            navbar_elems = get_navbar_elems(soup)
            return paragraphs, navbar_elems       

def get_navbar_elems(soup):
    # Find the table of contents section of Wikipedia page
    navbar = soup.find('div', {'id': 'vector-toc'})
    # print(navbar)
    if not navbar:
        return None

    # Find the list of page categories for the table of contents
    category_list = navbar.find('ul', {'id': 'mw-panel-toc-list'})
    
    # Find all the "li" elements with the specified class
    cat_list_elems = category_list.find_all('li', class_=lambda x: x and 'vector-toc-list-item' in x and 'vector-toc-level-1' in x)

    # Extract ids of all found "li" elements
    li_ids = [li['id'] for li in cat_list_elems]
    
    # Remove "toc-" from the strings in the li_ids list
    li_ids_stripped = [li_id.replace('toc-', '') for li_id in li_ids]
    # print(li_ids_stripped)


    # with open('output.txt', 'w', encoding='utf-8') as f:
    #     for navElement in toc_items:
    #         f.write(navElement + '\n\n')

    # return toc_items
    return li_ids_stripped

def main(word_to_search, toc_section=''):
    langUI = 'en'
    url = getWord(langUI, word_to_search)
    paragraphs, navbar_elems = wikiSearch(url, toc_section)
    return paragraphs, navbar_elems

def gptSearch(word_to_search):
  openai.api_key = "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"
  response = openai.Completion.create(model="text-davinci-003", prompt=("Just write me a paragraph for the following word: " + word_to_search), temperature=.6, max_tokens=1024)
  return response.choices[0].text.strip()
