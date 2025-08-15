import random
import numpy as np
class RandomRetriever:
    def __init__(self, 
                    candidates,
                    seed=77,
                    **kwargs
                    ):
        self.candidates = candidates
        self.seed = seed
        self.num_candidates = len(candidates)

    def retrieve(self, query, top_k=10, seed=None):
        # Randomly sample top_k examples from the dataset
        random.seed(seed if seed is not None else self.seed)
        return random.sample(self.candidates, k=top_k)

    def retrieve_batch(self, queries, k=10, seed=None):
        rng = np.random.default_rng(seed if seed is not None else self.seed)
        selected_indices = rng.integers(0, self.num_candidates, size=(len(queries), k))
        return selected_indices

    def retrieve_list(self, queries, k=10):
        rng = np.random.default_rng(self.seed)
        selected_indices = rng.integers(0, self.num_candidates, size=(len(queries), k))
        
        return selected_indices