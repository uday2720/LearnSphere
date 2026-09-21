from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class LocalRetriever:
    def __init__(self, chunks):
        self.chunks=list(chunks); self.vectorizer=None; self.matrix=None
        texts=[r['text'] for r in self.chunks]
        if texts:
            self.vectorizer=TfidfVectorizer(stop_words='english',ngram_range=(1,2))
            self.matrix=self.vectorizer.fit_transform(texts)
    def search(self,query,top_k=3):
        if self.matrix is None:return []
        scores=cosine_similarity(self.vectorizer.transform([query]),self.matrix)[0]
        return [{'page':self.chunks[i]['page_number'],'text':self.chunks[i]['text'],'score':float(scores[i])} for i in scores.argsort()[::-1][:top_k] if scores[i]>0]

def answer_locally(question,context):
    if not context:return 'I could not find a strong match in your study material. Try using terminology from the uploaded notes.'
    out=['Based on your study material:']
    for x in context:
        s=' '.join(x['text'].split()); s=s[:420]+'…' if len(s)>420 else s
        out.append(f"\n• Page {x['page']}: {s}")
    out.append('\n\nStudy tip: explain the idea in your own words, then test yourself with a small example.')
    return '\n'.join(out)
