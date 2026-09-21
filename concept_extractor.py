import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer


STOP_WORDS = {
    "the", "and", "for", "with", "that", "this", "from", "are", "was",
    "were", "have", "has", "had", "into", "than", "then", "their", "there",
    "which", "when", "where", "what", "your", "you", "our", "they", "them",
    "using", "used", "use", "can", "may", "will", "also", "such", "each",
    "more", "most", "some", "any", "not", "but", "its", "is", "in", "of",
    "to", "a", "an", "on", "as", "by", "be", "or", "at", "it", "we"
}


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_concepts(pages, top_k=12):
    """
    Lightweight local concept extraction.

    This is intentionally an MVP heuristic. Later we can replace it with
    a local model while keeping the same interface.
    """
    documents = [clean_text(text) for _, text in pages if text.strip()]
    if not documents:
        return []

    combined = " ".join(documents)

    # Single words and useful two-word phrases.
    candidates = re.findall(
        r"\b[A-Za-z][A-Za-z0-9-]{2,}(?:\s+[A-Za-z][A-Za-z0-9-]{2,})?\b",
        combined
    )

    counts = Counter(
        c.lower()
        for c in candidates
        if all(word.lower() not in STOP_WORDS for word in c.split())
    )

    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=200
        )
        matrix = vectorizer.fit_transform(documents)
        scores = matrix.mean(axis=0).A1
        terms = vectorizer.get_feature_names_out()
        ranked = sorted(zip(terms, scores), key=lambda x: x[1], reverse=True)
    except ValueError:
        ranked = []

    merged = []
    seen = set()

    for term, score in ranked:
        normalized = term.lower().strip()
        if normalized in STOP_WORDS or normalized in seen:
            continue
        if len(normalized) < 4:
            continue
        seen.add(normalized)
        merged.append((term.title(), float(score)))
        if len(merged) >= top_k:
            break

    # Fallback if TF-IDF gives too little information.
    if len(merged) < min(5, top_k):
        for term, count in counts.most_common(top_k * 2):
            if term not in seen and len(term) >= 4:
                seen.add(term)
                merged.append((term.title(), float(count)))
            if len(merged) >= top_k:
                break

    return merged[:top_k]
