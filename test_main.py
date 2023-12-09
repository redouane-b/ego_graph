import sys
from datetime import datetime
from utils import *

if __name__ == "__main__":
    # Check if the correct number of command line arguments is provided
    if len(sys.argv) != 6:
        print("Usage: python main.py country language search_term max_depth num_suggestions")
        sys.exit(1)

    country = sys.argv[1]
    language = sys.argv[2]
    search_term = sys.argv[3]
    max_depth = int(sys.argv[4])
    num_suggestions = int(sys.argv[5])

    suggestions = fetch_suggestions(country, language, search_term, num_suggestions=num_suggestions)
    accepted_terms = extract_terms_after_vs(suggestions, search_term, [])

    result_dataframe = build_dataframe(country, language, search_term, accepted_terms, num_suggestions=num_suggestions, depth=max_depth)

    nodes = generate_node_df(result_dataframe)
    edges = generate_edges_df(result_dataframe)

    # Save dataframes with the current date in the filename
    current_date = datetime.now().strftime("%Y-%m-%d")
    nodes.to_csv(f'points_{current_date}.csv', index=False)
    edges.to_csv(f'links_{current_date}.csv', index=False)
