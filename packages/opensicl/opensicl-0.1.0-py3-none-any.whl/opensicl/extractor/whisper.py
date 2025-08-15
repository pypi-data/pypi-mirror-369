import torch
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from embedding_utils import compute_stats_embeddings, create_feature_mask

def chunk_dataset(dataset, num_chunks):
    """
    Split the dataset into chunks for parallel processing.
    
    Args:
        dataset: The dataset to be chunked
        num_chunks: Number of chunks to split the dataset into
    
    Returns:
        List of datasets, each representing a chunk
    """
    from torch.utils.data import Subset
    dataset_size = len(dataset)
    chunk_size = dataset_size // num_chunks
    return [Subset(dataset, range(i * chunk_size, min((i + 1) * chunk_size, dataset_size))) for i in range(num_chunks)]


class WhisperEmbeddingExtractor():
    """
    Extracts embeddings using the Whisper model.
    """
    def __init__(self, model_path=None):
        self.model_path = model_path
        self.num_gpus = torch.cuda.device_count()
        self.extractors = []
        self.processor = self.load_whisper_processor(model_path)
        
        if self.model_path is None:
            raise ValueError("Either encoder and processor must be provided, or model_path must be specified.")
        for device_id in range(self.num_gpus):
            # Load the encoder and processor for each GPU
            self.extractors.append(self.load_whisper_encoder(self.model_path, device=f"cuda:{device_id}"))
            
        


    @staticmethod
    def load_whisper_encoder(model_path, device="cuda"):
        # Normalize the device
        
        from transformers import WhisperModel
        whisper_model = WhisperModel.from_pretrained(
            model_path,
            attn_implementation="flash_attention_2"

        )
        whisper_encoder = whisper_model.get_encoder()
        return whisper_encoder.to(device)
    @staticmethod
    def load_whisper_processor(model_path):
        from transformers import AutoProcessor
        processor = AutoProcessor.from_pretrained(model_path)
        return processor
    
    @staticmethod
    def extract_fn(dataset, 
                   extractor, 
                   processor,
                   input_column="audio", 
                   batch_size=32,
                   num_workers=0,
                   use_masking=True
                   ):

        def collate_fn(batch):
            audios = [item[input_column]["array"] for item in batch]
            sampling_rate = batch[0][input_column]["sampling_rate"]
            inputs = processor(
                audios, 
                sampling_rate=sampling_rate, 
                return_tensors="pt", 
                return_attention_mask=True
            )
            return inputs
        
        dataloader = torch.utils.data.DataLoader(
            dataset,
            batch_size=batch_size,
            collate_fn=collate_fn,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=True
        )
        device_string = f"{extractor.device.type}:{extractor.device.index}" if extractor.device.type == "cuda" else extractor.device.type
        
        embeddings_list = []
        
        for batch in tqdm(dataloader, desc=f"Extracting Whisper embeddings on {device_string}", unit="batch"):
            # Ensure the device is set correctly
            batch = {k: v.to(device_string) if torch.is_tensor(v) else v for k, v in batch.items()}
            
            with torch.no_grad():
                with torch.amp.autocast(device_type=device_string, dtype=torch.float16):
                    embeddings = extractor(**batch).last_hidden_state
                
            attention_mask = batch["attention_mask"]
            stats_embeddings = compute_stats_embeddings(embeddings, attention_mask, use_masking=use_masking).cpu() # [B, D]

            embeddings_list.extend([emb.numpy() for emb in stats_embeddings])
            
        
        return embeddings_list
        
    
    def _load_model_from_config(self, config):
        
        pass
    
    
    
    def extract(self, dataset, input_column="audio", **kwargs):
        
        embeddings = []
        dataset_chunks = chunk_dataset(dataset, self.num_gpus)
        results = [None] * len(dataset_chunks)

        with ThreadPoolExecutor(max_workers=self.num_gpus) as executor:
            futures = []
            for i, chunk in enumerate(dataset_chunks):
                future = executor.submit(self.extract_fn, 
                                            chunk, 
                                            input_column=input_column,
                                            extractor=self.extractors[i], 
                                            processor=self.processor, 
                                            **kwargs)
                futures.append((i, future))
                
            for i, future in futures:
                results[i] = future.result()
                
        # dataset = concatenate_datasets(results)
        embeddings = np.concatenate([res for res in results], axis=0)
        
        return embeddings


if __name__ == "__main__":
    from datasets import load_dataset, Audio
    path = "MagicLuke/RedmondSentenceRecall"
    dataset = load_dataset(path,"fewshot",revision="cache",split="test")
    dataset = dataset.cast_column("audio", Audio(sampling_rate=16000))
    model_path = "openai/whisper-medium"
    extractor = WhisperEmbeddingExtractor(model_path=model_path)
    embeddings = extractor.extract(dataset, batch_size=48, num_workers=16)
    print(embeddings.shape)