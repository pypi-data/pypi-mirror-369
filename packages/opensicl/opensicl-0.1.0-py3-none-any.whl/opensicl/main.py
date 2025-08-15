from datasets import load_dataset
from extractor import WhisperExtractor
from retriever import TopkRetriever

test_dataset = load_dataset("your_dataset_name")
candidate_dataset = load_dataset("your_candidate_dataset_name")

extractor = WhisperExtractor(model_path="openai/whisper-large-v2")

test_embeddings = extractor.extract_embeddings(test_dataset, input_column="audio")
candidate_embeddings = extractor.extract_embeddings(candidate_dataset, input_column="audio")

retriever = TopkRetriever(candidates=candidate_embeddings, metric='cosine', num_gpus=1)
selected_indices = retriever.list_retrieve(test_embeddings, k=10, batch_size=8)



