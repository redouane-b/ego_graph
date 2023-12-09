from flask import Flask, render_template, request
from datetime import datetime
from utils import fetch_suggestions, extract_terms_after_vs, build_dataframe, generate_node_df, generate_edges_df
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['GET', 'POST'])
def process():
    if request.method == 'POST':
        country = request.form['country']
        language = request.form['language']
        search_term = request.form['search_term']
        max_depth = int(request.form['max_depth'])
        num_suggestions = int(request.form['num_suggestions'])

        suggestions = fetch_suggestions(country, language, search_term, num_suggestions=num_suggestions)
        accepted_terms = extract_terms_after_vs(suggestions, search_term, [])

        result_dataframe = build_dataframe(country, language, search_term, accepted_terms, num_suggestions=num_suggestions, depth=max_depth)

        nodes = generate_node_df(result_dataframe)
        edges = generate_edges_df(result_dataframe)

        # Save dataframes with the current date in the filename
        current_date = datetime.now().strftime("%Y-%m-%d")
        nodes.to_csv(f'static/points_{current_date}.csv', index=False)
        edges.to_csv(f'static/links_{current_date}.csv', index=False)

        return render_template('result.html', nodes=f'points_{current_date}.csv', edges=f'links_{current_date}.csv')

    # Render the main page for GET requests
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
