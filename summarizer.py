from transformers import pipeline
import torch

class AISummarizer:
    def __init__(self, model_name="sshleifer/distilbart-cnn-12-6"):
        print(f"Initializing summarizer with model: {model_name}...")
        device = 0 if torch.cuda.is_available() else -1
        self.summarizer = pipeline("summarization", model=model_name, device=device)
        print("Summarizer initialized.")

    def summarize(self, text, max_len=150, min_len=50):
        """
        Summarizes the input text. Handles long texts by chunking.
        """
        if not text or len(text.split()) < 20:
            return text

        # Simple chunking logic (approx 800 words per chunk to stay under token limits)
        words = text.split()
        chunks = [" ".join(words[i:i + 800]) for i in range(0, len(words), 800)]
        
        summaries = []
        for chunk in chunks:
            try:
                summary = self.summarizer(chunk, max_length=max_len, min_length=min_len, do_sample=False)
                summaries.append(summary[0]['summary_text'])
            except Exception as e:
                print(f"Error summarizing chunk: {e}")
                continue

        return " ".join(summaries)

    def extract_keywords(self, text, num_keywords=10):
        """
        Very basic keyword extraction logic (using word frequency for now).
        In a production app, we might use KeyBERT or Rake-NLTK.
        """
        from collections import Counter
        import re

        # Simple stop words list
        stop_words = {"the", "and", "is", "of", "in", "to", "it", "that", "this", "for", "on", "with", "as", "are"}
        
        words = re.findall(r'\w+', text.lower())
        filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
        
        counts = Counter(filtered_words)
        return [word for word, count in counts.most_common(num_keywords)]

    def extract_key_points(self, summary_text):
        """
        Converts the summary into a list of key points.
        """
        # Simple logic: split summary by sentences and treat them as points
        sentences = summary_text.split('. ')
        key_points = [s.strip() + '.' for s in sentences if len(s) > 20]
        return key_points[:7] # Return top 7 points
