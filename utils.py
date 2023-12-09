import requests
import xml.etree.ElementTree as ET
import pandas as pd

num_suggestions = 7
max_depth = 3

def fetch_suggestions(country, language, search_term, num_suggestions=num_suggestions):
    url = f'http://suggestqueries.google.com/complete/search?&output=toolbar&gl={country}&hl={language}&q={search_term}%20vs%20'
    response = requests.get(url)

    if response.status_code == 200:
        xml_data = ET.fromstring(response.text)
        suggestions = [suggestion.get('data') for suggestion in xml_data.findall('.//suggestion')[:num_suggestions] if suggestion.get('data')]
        return suggestions
        
    else:
        print(f"Error: Call Redouane {response.status_code}")
        return []

def extract_terms_after_vs(suggestions, search_term, accepted_terms):
    extracted_terms = []

    for suggestion in suggestions:
        terms = suggestion.split(' vs ')

        if (
            len(terms) == 2 and
            search_term.lower() not in terms[1].lower() and
            terms[1].lower() not in accepted_terms and
            terms[1].lower() not in extracted_terms and
            ' vs ' not in terms[1].lower() and
            all(extracted_term.lower() not in terms[1].lower() for extracted_term in extracted_terms)
        ):

            extracted_terms.append(terms[1])

    return extracted_terms


def build_dataframe(country, language, search_term, accepted_terms, num_suggestions=num_suggestions, depth=max_depth):
    result_list = []
    id_counter = 1
    source_terms = []

    def process_term(current_search_term, current_depth):
      nonlocal id_counter
      suggestions = fetch_suggestions(country, language, current_search_term, num_suggestions=num_suggestions)
      extracted_terms = extract_terms_after_vs(suggestions, current_search_term, accepted_terms)
      source_terms.append(current_search_term)
      
      for i, term in enumerate(extracted_terms):
          result_list.append({'source': current_search_term, 'target': term, 'weight': num_suggestions - i, 'id': id_counter})
          id_counter += 1

          if current_depth < depth and term not in source_terms:
              process_term(term, current_depth + 1)

    process_term(search_term, 1)

    result_df = pd.DataFrame(result_list, columns=['source', 'target', 'weight', 'id'])
    return result_df.sort_values(by='id').reset_index(drop=True)


def generate_node_df(dataframe,column = 'target'):
    term_counts = dataframe[column].value_counts()
    unique_terms  = term_counts.index 

    nodes = pd.DataFrame({'term': unique_terms, 'count': term_counts}).reset_index(drop=True)
    return nodes


def generate_edges_df(dataframe,num_suggestions = num_suggestions):

    dataframe[['source', 'target']] = dataframe.apply(lambda row: sorted([row['source'], row['target']]), axis=1, result_type='expand')
    grouped = dataframe.groupby(['source', 'target'])

    edges = pd.DataFrame(columns=['source', 'target', 'weight', 'distance'])

    for (source, target), group in grouped:
        total_weight = group['weight'].sum()
        distance = 2 * num_suggestions + 1 - total_weight

        edges = pd.concat([edges, pd.DataFrame({'source': [source], 'target': [target], 'weight': [total_weight], 'distance': [distance]})])
        

    edges = edges.reset_index(drop=True)
    return edges

