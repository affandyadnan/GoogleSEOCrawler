import csv
import time
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import pandas as pd
import plotly.graph_objs as go

# Function to get search results for a keyword
def get_search_results(keyword, num_results):
    results = []
    for result in search(keyword, num=num_results, stop=num_results, pause=2):
        results.append(result)
    return results

# Function to export data to CSV
def export_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Keyword', 'Ranking', 'Title', 'URL', 'Snippet']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

# Function to process keywords and get rankings
def process_keywords(keywords, num_results_per_keyword):
    results_data = []
    for keyword in keywords:
        print(f"Processing keyword: {keyword}")
        results = get_search_results(keyword, num_results_per_keyword)
        for i, url in enumerate(results, start=1):
            # Get title and snippet
            title = ""
            snippet = ""
            try:
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                title_tag = soup.find('title')
                if title_tag:
                    title = title_tag.text
                snippet_tag = soup.find('meta', attrs={'name': 'description'})
                if snippet_tag and 'content' in snippet_tag.attrs:
                    snippet = snippet_tag['content']
            except Exception as e:
                print(f"Error retrieving data for URL: {url}. {e}")
                continue  # Skip to the next URL if there's an error
            
            results_data.append({'Keyword': keyword, 'Ranking': i, 'Title': title, 'URL': url, 'Snippet': snippet})
            time.sleep(2)  # Adding a delay to avoid hitting Google's rate limits
    return results_data

# Function to plot interactive chart
def plot_chart(data):
    df = pd.DataFrame(data)
    fig = go.Figure()

    for keyword in df['Keyword'].unique():
        keyword_data = df[df['Keyword'] == keyword]
        fig.add_trace(go.Scatter(x=keyword_data['Ranking'], y=keyword_data['Keyword'], mode='lines+markers', name=keyword))

    fig.update_layout(title='SEO Rankings',
                      xaxis_title='Ranking',
                      yaxis_title='Keyword',
                      xaxis=dict(type='category'),
                      yaxis=dict(type='category'))
    
    fig.show()

if __name__ == "__main__":
    # Prompt the user to enter keywords
    keywords_input = input("Enter keywords separated by commas: ")
    keywords = [keyword.strip() for keyword in keywords_input.split(',')]

    # Number of search results per keyword
    num_results_per_keyword = 10

    # Process keywords and get rankings
    results_data = process_keywords(keywords, num_results_per_keyword)

    # Export data to CSV
    export_to_csv(results_data, 'seo_rankings.csv')

    # Plot interactive chart
    plot_chart(results_data)
