import numpy as np

# Предположим, что мы уже обучили упрощённые двумерные векторы слов
embeddings = {
    "king": np.array([0.9, 0.8]),
    "queen": np.array([0.9, 0.2]),
    "man": np.array([0.7, 0.9]),
    "woman": np.array([0.7, 0.3])
}

def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm_product = np.linalg.norm(vec1) * np.linalg.norm(vec2)
    return dot_product / norm_product

# king - man + woman
result_vec = embeddings["king"] - embeddings["man"] + embeddings["woman"]

# Вычисляем сходство результирующего вектора с "queen"
sim = cosine_similarity(result_vec, embeddings["queen"])

print(f"Результирующий вектор king - man + woman: {result_vec}")
print(f"Сходство результата с 'queen': {sim:.4f}")
