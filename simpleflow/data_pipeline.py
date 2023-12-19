import os 

from src.data_processing.dataloader import Dataloader
from src.pipeline.mention_extraction import MentionExtraction
from src.pipeline.graph_generation import GraphGeneration
from src.output.json_writer import JsonWriter

def main():
    # Load and clean data
    loader = Dataloader()
    loaded_data = loader.load_data()
    cleaned_data = loader.clean_data(loaded_data)

    # Extract mentions
    extractor = MentionExtraction()
    mention_dict = extractor.extract()

    # Generate graph
    graph_generator = GraphGeneration()
    graph = graph_generator.generate_graph()


    # Write to JSON
    json_writer = JsonWriter()
    json_writer.write()

    #generate graph 
    graph_generator.run_app()

    print("Data processing pipeline completed successfully.")

if __name__ == "__main__":
    main()