import os 
import networkx as nx
import plotly.graph_objects as go
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import webbrowser
from flask import request
import requests

from collections import Counter
import threading

from src.base.base_generator import BaseGenerator
from src.util.env_initializer import initialize_env
from src.util.directory_creator import create_directory_if_not_exists
from src.util.data_saver import save_graph
from src.util.read_data import read_data

class GraphGeneration(BaseGenerator):
    def __init__(self):
        # Load .env file 
        initialize_env()

        BASE_PATH = os.path.dirname(os.path.abspath(__file__))

        # Get the dataoutput to save the trated data from the .env file
        data_out_path = os.path.join(BASE_PATH,os.getenv("DATA_OUTPUT_FOLDER"))
        self.data_out_path = os.path.normpath(data_out_path)
        create_directory_if_not_exists(self.data_out_path)

        # Input cleaned data from dataloader 
        mention_dict_path = os.path.join(BASE_PATH,os.getenv("MENTION_DICT_OUTPUT_FILE"))
        self.mention_dict_path = os.path.normpath(mention_dict_path)
        self.mention_dict = read_data(self.mention_dict_path)


        OUTPUT_FILE = os.path.join(BASE_PATH,os.getenv("GRAPH_OUTPUT_PATH"))
        self.OUTPUT_FILE = os.path.normpath(OUTPUT_FILE)
        self.graph = self.generate_graph()

    def generate_graph(self):
        try:
            graph = nx.Graph()

            # Iterate over drugs and their mentions
            for drug, mentions in self.mention_dict.items():
                graph.add_node(drug)

                # Iterate over mentions for each data source
                for source, mention_list in mentions.items():
                    # Add nodes for the source (e.g., 'pubmed', 'clinical_trials')
                    graph.add_node(source)

                    # Connect drug to the source with the mention date as an attribute
                    for mention in mention_list:
                        date = mention['date']
                        journal = mention['journal']
                        graph.add_node(journal)
                        graph.add_edge(drug, source, mention_date="reference")
                        graph.add_edge(source, journal, mention_date=date)
                        graph.add_edge(journal, drug, mention_date=date)

            save_graph(graph, self.OUTPUT_FILE)
            return graph
        except Exception as e:
            raise ValueError(f"Error generating graph: {str(e)}")
    
    def find_most_mentioned_journal(self):
        journal_counts = Counter()

        for drug, mentions in self.mention_dict.items():
            for source, articles in mentions.items():
                if source == 'pubmed':
                    for article in articles:
                        journal_counts[article['journal']] += 1

        most_common_journal = journal_counts.most_common(1)
        return most_common_journal[0][0] if most_common_journal else None
    
    def find_drugs_in_common_journals(self, target_drug):
        target_journals = set(article['journal'] for article in self.mention_dict[target_drug]['pubmed'])
        common_drugs = set()

        for drug, mentions in self.mention_dict.items():
            if drug != target_drug:
                drug_journals = set(article['journal'] for article in mentions['pubmed'])
                if target_journals.intersection(drug_journals):
                    common_drugs.add(drug)

        return common_drugs
    
    def display_click_data(self, clickData, show_only_drugs=False):
        # Determine the node that was clicked
        node_id = clickData['points'][0]['text'] if clickData else None

        if node_id:
            neighbors = list(self.graph.neighbors(node_id)) + [node_id]
            subgraph = self.graph.subgraph(neighbors)
        elif show_only_drugs:
            subgraph = self.graph.subgraph(self.mention_dict.keys())
        else:
            subgraph = self.graph

        pos = nx.spring_layout(subgraph)

        edge_trace, node_trace = [], []

        for edge in subgraph.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace.append(go.Scatter(x=[x0, x1, None], y=[y0, y1, None], mode='lines', line=dict(width=2)))

            # Add edge labels for dates
            edge_midpoint = [(x0 + x1) / 2, (y0 + y1) / 2]
            mention_date = edge[2].get('mention_date', '')
            edge_trace.append(go.Scatter(
                x=[edge_midpoint[0]], y=[edge_midpoint[1]],
                text=[mention_date], mode='text',
                showlegend=False
            ))

        for node in subgraph.nodes():
            x, y = pos[node]
            node_trace.append(go.Scatter(x=[x], y=[y], mode='markers+text', text=[node], marker=dict(size=10)))

        figure = go.Figure(data=edge_trace + node_trace, layout=go.Layout(
            title=f"Graph centered on: {node_id}" if node_id else "Full Graph",
            showlegend=False,
            hovermode='closest'
        ))

        return figure
    
    def run_app(self):
        app = dash.Dash(__name__, server=True)

        drug_options = [{'label': drug, 'value': drug} for drug in self.mention_dict.keys()]

        app.layout = html.Div([
            dcc.Graph(id='network-graph', figure=self.display_click_data(None)),
            dcc.Checklist(id='drug-node-selector', options=[{'label': 'Show only drug nodes', 'value': 'SHOW_DRUGS'}], value=[]),
            html.Button('Reset Graph', id='reset-button'),
            dcc.Dropdown(id='analysis-selector', options=[{'label': 'Most Mentioned Journal', 'value': 'MOST_MENTIONED_JOURNAL'}, {'label': 'Common Drugs in Journals', 'value': 'COMMON_DRUGS'}], value='MOST_MENTIONED_JOURNAL'),
            dcc.Dropdown(id='drug-selector', options=drug_options, value=list(self.mention_dict.keys())[0] if self.mention_dict else None),
            html.Div(id='analysis-result'),
            html.Button('Shutdown Server', id='shutdown-button'),
            html.Div(id='shutdown-placeholder')
        ])

        @app.callback(
        Output('network-graph', 'figure'),
        [Input('network-graph', 'clickData'),
            Input('drug-node-selector', 'value'),
            Input('reset-button', 'n_clicks')]
        )

        # @app.callback(Output('network-graph', 'figure'), [Input('network-graph', 'clickData'), Input('drug-node-selector', 'value'), Input('reset-button', 'n_clicks')])
        def update_graph(clickData, drug_node_selection, n_clicks):
            ctx = dash.callback_context
            if ctx.triggered and ctx.triggered[0]['prop_id'] == 'reset-button.n_clicks':
                return self.display_click_data(None, 'SHOW_DRUGS' in drug_node_selection)

            show_only_drugs = 'SHOW_DRUGS' in drug_node_selection
            return self.display_click_data(clickData, show_only_drugs)

        @app.callback(Output('analysis-result', 'children'), [Input('analysis-selector', 'value'), Input('drug-selector', 'value')])
        def update_analysis(selected_analysis, selected_drug):
            if selected_analysis == 'MOST_MENTIONED_JOURNAL':
                journal = self.find_most_mentioned_journal()
                return f"Most Mentioned Journal: {journal}"
            elif selected_analysis == 'COMMON_DRUGS':
                common_drugs = self.find_drugs_in_common_journals(selected_drug)
                return f"Common Drugs for {selected_drug}: {', '.join(common_drugs)}"
            return "Select an analysis"
        
        @app.server.route('/shutdown', methods=['POST'])
        def shutdown():
            func = request.environ.get('werkzeug.server.shutdown')
            if func is not None:
                func()
            return 'Server shutting down...'

        # Callback for the shutdown button
        @app.callback(
            Output('shutdown-placeholder', 'children'),
            [Input('shutdown-button', 'n_clicks')],
            prevent_initial_call=True
        )
        def shutdown_callback(n_clicks):
            if n_clicks:
                try:
                    requests.post('http://localhost:8050/shutdown')
                    return "Server shutting down..."
                except Exception as e:
                    print(f"Error sending shutdown request: {e}")
                    return "Error in shutting down server"
        # def run_dash():
        # dash_url = "http://127.0.0.1:8050"
        # webbrowser.open(dash_url)
        app.run_server(debug=True, host='0.0.0.0', port=8050)

       