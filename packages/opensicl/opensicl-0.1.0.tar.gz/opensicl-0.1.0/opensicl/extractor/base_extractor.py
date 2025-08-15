
class BaseExtractor:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

    def extract(self, audio):
        inputs = self.tokenizer(audio, return_tensors="pt")
        with torch.no_grad():
            embeddings = self.model(**inputs).last_hidden_state
        return embeddings
