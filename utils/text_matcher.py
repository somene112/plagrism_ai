import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util
import os
import torch
import time
import hashlib

CACHE_DIR = "data/embeddings"
os.makedirs(CACHE_DIR, exist_ok=True)

_model = None
def get_model():
    global _model
    if _model is None:
        if not torch.cuda.is_available():
            raise RuntimeError("❌ Không tìm thấy GPU! Vui lòng kiểm tra lại thiết bị hoặc driver.")
        print("🚀 Đang tải SentenceTransformer vào GPU...")
        start = time.time()
        _model = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            device="cuda"
        )
        print(f"✅ Mô hình đã tải trong {time.time() - start:.2f}s")
    return _model

def tfidf_similarity(input_text, compare_texts):
    texts = [input_text] + compare_texts
    vectorizer = TfidfVectorizer().fit(texts)
    vectors = vectorizer.transform(texts)
    cosine_scores = cosine_similarity(vectors[0:1], vectors[1:]).flatten()
    return cosine_scores.tolist()

def get_cached_text_embedding(text):
    model = get_model()
    hash_id = hashlib.md5(text.encode('utf-8')).hexdigest()
    cache_path = os.path.join(CACHE_DIR, f"full_{hash_id}.npy")
    if os.path.exists(cache_path):
        return np.load(cache_path)
    emb = model.encode(text, convert_to_numpy=True)
    np.save(cache_path, emb)
    return emb

def deep_similarity(input_text, compare_texts):
    model = get_model()
    input_emb = model.encode(input_text, convert_to_tensor=True)
    compare_embs = [get_cached_text_embedding(t) for t in compare_texts]
    compare_embs = torch.tensor(np.stack(compare_embs), device=input_emb.device)
    cosine_scores = util.cos_sim(input_emb, compare_embs).cpu().numpy().flatten()
    return cosine_scores.tolist()

def sliding_window_tokens(text, window_size=30, stride=15):
    tokens = text.split()
    windows = []
    for i in range(0, len(tokens) - window_size + 1, stride):
        window_text = " ".join(tokens[i:i + window_size])
        windows.append(window_text)
    return windows

def get_cached_segment_embeddings(text, segments):
    model = get_model()
    hash_id = hashlib.md5(text.encode('utf-8')).hexdigest()
    cache_path = os.path.join(CACHE_DIR, f"segments_{hash_id}.npy")
    if os.path.exists(cache_path):
        return np.load(cache_path)
    emb = model.encode(segments, convert_to_numpy=True, batch_size=16)
    np.save(cache_path, emb)
    return emb

def deep_segment_similarity(input_text, compare_text,input_emb=None, input_segments=None,threshold=0.7, window_size=50, stride=25):
    model = get_model()

    if input_segments is None:
        input_segments = sliding_window_tokens(input_text, window_size, stride)
    if input_emb is None:
        input_emb = model.encode(input_segments, convert_to_tensor=True, batch_size=16)

    compare_segments = sliding_window_tokens(compare_text, window_size, stride)
    compare_emb = get_cached_segment_embeddings(compare_text, compare_segments)

    if isinstance(compare_emb, np.ndarray):
        compare_emb = torch.tensor(compare_emb, device=input_emb.device)
    else:
        compare_emb = compare_emb.to(input_emb.device)

    sim_matrix = util.cos_sim(input_emb, compare_emb)

    matches = []
    seen_segment = set()
    seen_position = set()
    for i in range(len(input_segments)):
        for j in range(len(compare_segments)):
            if sim_matrix[i][j] >= threshold:
                seg_text = input_segments[i]
                start_pos = input_text.find(seg_text)
                end_pos = start_pos + len(seg_text)
                if seg_text in seen_segment or start_pos in seen_position:
                    continue
                seen_segment.add(seg_text)
                seen_position.add(start_pos)
                matches.append({
                    'text': seg_text,
                    'start_pos': start_pos,
                    'end_pos': end_pos
                })
    return matches