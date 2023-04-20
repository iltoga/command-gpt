from sentence_transformers import SentenceTransformer, util
import torch


class CosineSimilarity:
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def _encode_sentences(self, sentences):
        # TODO - Implement caching of embeddings to avoid recomputing them via vector database (eg. Chroma)
        return self.model.encode(sentences, convert_to_tensor=True)

    def _compute_cosine_similarity(self, embeddings1, embeddings2):
        return util.cos_sim(embeddings1, embeddings2)

    def similarity_between_two_lists(self, sentences1, sentences2):
        embeddings1 = self._encode_sentences(sentences1)
        embeddings2 = self._encode_sentences(sentences2)
        cosine_scores = self._compute_cosine_similarity(embeddings1, embeddings2)

        results = []
        for i in range(len(sentences1)):
            results.append((sentences1[i], sentences2[i], cosine_scores[i][i].item()))
        return results

    def top_similar_pairs(self, sentences, top_k=10):
        embeddings = self._encode_sentences(sentences)
        cosine_scores = self._compute_cosine_similarity(embeddings, embeddings)

        pairs = []
        for i in range(len(cosine_scores) - 1):
            for j in range(i + 1, len(cosine_scores)):
                pairs.append({'index': [i, j], 'score': cosine_scores[i][j].item()})

        pairs.sort(key=lambda x: x['score'], reverse=True)
        return [(sentences[pair['index'][0]], sentences[pair['index'][1]], pair['score']) for pair in pairs[:top_k]]

    def semantic_search(self, corpus, query, top_k=5):
        corpus_embeddings = self._encode_sentences(corpus)

        query_embedding = self._encode_sentences([query])
        cos_scores = self._compute_cosine_similarity(query_embedding, corpus_embeddings)[0]
        top_results = torch.topk(cos_scores, k=top_k)

        query_results = []
        for score, idx in zip(top_results[0], top_results[1]):
            query_results.append((corpus[idx], score.item()))

        return query_results



if __name__ == '__main__':
    cosine_similarity = CosineSimilarity()

    # ask user for input: what test do you want to run?
    choice = input("What test do you want to run? (1, 2, 3): ")

    if choice == "1":
        sentences1 = ['The cat sits outside', 'A man is playing guitar', 'The new movie is awesome']
        sentences2 = ['The dog plays in the garden', 'A woman watches TV', 'The new movie is so great']

        results = cosine_similarity.similarity_between_two_lists(sentences1, sentences2)
        for result in results:
            print(f"{result[0]} \t\t {result[1]} \t\t Score: {result[2]:.4f}")

    elif choice == "2":
        sentences = ['The cat sits outside', 'A man is playing guitar', 'I love pasta', 'The new movie is awesome',
                     'The cat plays in the garden', 'A woman watches TV', 'The new movie is so great', 'Do you like pizza?']

        results = cosine_similarity.top_similar_pairs(sentences)
        for result in results:
            print(f"{result[0]} \t\t {result[1]} \t\t Score: {result[2]:.4f}")

    elif choice == "3":
        corpus = ['A man is eating food.', 'A man is eating a piece of bread.',
        'The girl is carrying a baby.', 'A man is riding a horse.', 'A woman is playing violin.',
        'Two men pushed carts through the woods.', 'A man is riding a white horse on an enclosed ground.',
        'A monkey is playing drums.', 'A cheetah is running behind its prey.']
        queries = ['A man is eating pasta.', 'Someone in a gorilla costume is playing a set of drums.',
                   'A cheetah chases prey on across a field.']

        results = cosine_similarity.semantic_search(corpus, queries)
        for i, query_results in enumerate(results):
            print(f"\n\n======================\n\n")
            print(f"Query: {queries[i]}\n")
            print("Top 5 most similar sentences in corpus:")
            for result in query_results:
                print(f"{result[0]} (Score: {result[1]:.4f})")
