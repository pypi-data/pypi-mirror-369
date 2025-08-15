import re
import spacy

# Load spaCy English NER model
nlp = spacy.load("en_core_web_sm")

def clean_text(text: str) -> str:
    """
    Cleans text while preserving important capitalization for named entities and acronyms.
    """
    doc = nlp(text)
    preserved_tokens = set()

    # Collect named entities
    for ent in doc.ents:
        preserved_tokens.add(ent.text)

    words = []
    for token in doc:
        word = token.text

        # Preserve named entities and acronyms
        if word in preserved_tokens or (word.isupper() and len(word) <= 5):
            words.append(word)
        else:
            words.append(word.lower())

    cleaned = " ".join(words)
    cleaned = re.sub(r'[^A-Za-z0-9\s]', '', cleaned)  # Remove punctuation
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()   # Remove extra spaces
    return cleaned
