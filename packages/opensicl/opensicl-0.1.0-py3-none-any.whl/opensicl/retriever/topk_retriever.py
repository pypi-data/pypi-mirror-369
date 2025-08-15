
import faiss
import torch
import numpy as np
class TopkRetriever:
    def __init__(self, 
                 candidates,
                 metric='l2',
                 num_gpus=torch.cuda.device_count(),
                 **kwargs
                 ):
        self.candidates = candidates # candidates is a list of embeddings
        self.metric = metric
        self.dim = self.candidates[0].shape[-1] 
        self.num_candidates = len(candidates)
        self.num_gpus = num_gpus
        
        self._build_faiss_index()
        
        
    def _build_faiss_index(self):
        if self.metric == 'l2':
            index = faiss.IndexFlatL2(self.dim)
        elif self.metric == 'cosine':
            index = faiss.IndexFlatIP(self.dim)
        else:
            raise ValueError(f"Unsupported metric: {self.metric}")
        
        index.add(self.candidates)
        self.faiss_indices = []
        if self.num_gpus > 0 and hasattr(faiss, 'StandardGpuResources'):
            res = faiss.StandardGpuResources()
            for i in range(self.num_gpus):
                gpu_index = faiss.index_cpu_to_gpu(res, i, index)
                self.faiss_indices.append(gpu_index)
        else:
            self.faiss_indices.append(index)
            
    def retrieve(self, query, k=10):
        raise NotImplementedError("This method should be implemented in subclasses.")
        selected_indices = []
        
        return selected_indices
    
    def retrieve_batch(self, queries, k=10, gpu_id=0):
        
        selected_items, selected_indices = self.faiss_indices[gpu_id].search(queries, k)
        return selected_items, selected_indices
        
    
    def retrieve_list(self, queries, k=10, batch_size=8):
        """
            queries is a long list of embeddings
        """
        queries_chunks = np.array_split(queries, self.num_gpus)
        selected_indices = []
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.num_gpus) as executor:
            futures = []
            for i, chunk in enumerate(queries_chunks):
                futures.append(executor.submit(self.retrieve_batch, chunk, k, i))
            for future in futures:
                items, indices = future.result()
                selected_indices.append(indices)
                
        selected_indices = np.concatenate(selected_indices, axis=0)
        
        return selected_indices
        
        
        
        
        