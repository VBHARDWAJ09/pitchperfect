import faiss
import numpy as np
import os
import pickle

INDEX_PATH = "faiss.index"
METADATA_PATH = "metadata.pkl"

def load_index():
    if not os.path.exists(INDEX_PATH):
        index = faiss.IndexFlatL2(384)  # 384 for MiniLM
        metadata = []
    else:
        index = faiss.read_index(INDEX_PATH)
        with open(METADATA_PATH, "rb") as f:
            metadata = pickle.load(f)
    return index, metadata

def save_index(index, metadata):
    faiss.write_index(index, INDEX_PATH)
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)

def add_to_index(embedding, meta):
    index, metadata = load_index()
    index.add(np.array([embedding]).astype('float32'))
    metadata.append(meta)
    save_index(index, metadata)

def search_similar(embedding, top_k=3):
    index, metadata = load_index()
    if index.ntotal == 0:
        return []
    top_k = min(top_k, index.ntotal)
    D, I = index.search(np.array([embedding]).astype('float32'), top_k)
    seen = set()
    results = []
    for i in I[0]:
        if i < len(metadata) and i not in seen:
            seen.add(i)
            results.append(metadata[i])
    
    return results