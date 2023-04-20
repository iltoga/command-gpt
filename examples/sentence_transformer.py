from sentence_transformers import SentenceTransformer, util
import torch

def cosine_similarity(model):
    #
    # Cosine similarity 1
    # Use case: Compute cosine similarity between two lists of sentences
    # Practical use case: Semantic search (option 1)
    #
    print("Cosine similarity 1:")

    # Two lists of sentences
    sentences1 = ['The cat sits outside',
                'A man is playing guitar',
                'The new movie is awesome']

    sentences2 = ['The dog plays in the garden',
                'A woman watches TV',
                'The new movie is so great']

    #Compute embedding for both lists
    embeddings1 = model.encode(sentences1, convert_to_tensor=True)
    embeddings2 = model.encode(sentences2, convert_to_tensor=True)

    #Compute cosine-similarities
    cosine_scores = util.cos_sim(embeddings1, embeddings2)

    #Output the pairs with their score
    for i in range(len(sentences1)):
        print("{} \t\t {} \t\t Score: {:.4f}".format(sentences1[i], sentences2[i], cosine_scores[i][i]))

def cosine_similarity2(model):
    #
    # Cosine similarity 2
    # Use case: Find the 10 pairs of sentences with the highest cosine similarity scores
    # Practical use case: Find duplicate questions on StackOverflow
    #
    print("\n\nCosine similarity 2:")

    # Single list of sentences
    sentences = ['The cat sits outside',
                'A man is playing guitar',
                'I love pasta',
                'The new movie is awesome',
                'The cat plays in the garden',
                'A woman watches TV',
                'The new movie is so great',
                'Do you like pizza?']

    #Compute embeddings
    embeddings = model.encode(sentences, convert_to_tensor=True)

    #Compute cosine-similarities for each sentence with each other sentence
    cosine_scores = util.cos_sim(embeddings, embeddings)

    #Find the pairs with the highest cosine similarity scores
    pairs = []
    for i in range(len(cosine_scores)-1):
        for j in range(i+1, len(cosine_scores)):
            pairs.append({'index': [i, j], 'score': cosine_scores[i][j]})

    #Sort scores in decreasing order
    pairs = sorted(pairs, key=lambda x: x['score'], reverse=True)

    for pair in pairs[0:10]:
        i, j = pair['index']
        print("{} \t\t {} \t\t Score: {:.4f}".format(sentences[i], sentences[j], pair['score']))

def semantic_search(model):
    #
    # Semantic search
    #
    print("\n\nSemantic search:")

    # Corpus with example sentences
    corpus = ['A man is eating food.',
            'A man is eating a piece of bread.',
            'The girl is carrying a baby.',
            'A man is riding a horse.',
            'A woman is playing violin.',
            'Two men pushed carts through the woods.',
            'A man is riding a white horse on an enclosed ground.',
            'A monkey is playing drums.',
            'A cheetah is running behind its prey.'
            ]
    corpus_embeddings = model.encode(corpus, convert_to_tensor=True)

    # Query sentences:
    queries = ['A man is eating pasta.', 'Someone in a gorilla costume is playing a set of drums.', 'A cheetah chases prey on across a field.']


    # Find the closest 5 sentences of the corpus for each query sentence based on cosine similarity
    top_k = min(5, len(corpus))
    for query in queries:
        query_embedding = model.encode(query, convert_to_tensor=True)

        # We use cosine-similarity and torch.topk to find the highest 5 scores
        cos_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
        top_results = torch.topk(cos_scores, k=top_k)

        print("\n\n======================\n\n")
        print("Query:", query)
        print("\nTop 5 most similar sentences in corpus:")

        for score, idx in zip(top_results[0], top_results[1]):
            print(corpus[idx], "(Score: {:.4f})".format(score))

        """
        # Alternatively, we can also use util.semantic_search to perform cosine similarty + topk
        hits = util.semantic_search(query_embedding, corpus_embeddings, top_k=5)
        hits = hits[0]      #Get the hits for the first query
        for hit in hits:
            print(corpus[hit['corpus_id']], "(Score: {:.4f})".format(hit['score']))
    """


if __name__ == '__main__':
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    # ask user for input: what test do you want to run?
    # 1. Cosine similarity 1: Compute cosine similarity between two lists of sentences
    # 2. Cosine similarity 2: Find the 10 pairs of sentences with the highest cosine similarity scores
    # 3. Semantic search: Find the pairs with the highest cosine similarity scores
    choice = input("What test do you want to run? (1, 2, 3): ")
    if choice == "1":
        cosine_similarity(model)
    elif choice == "2":
        cosine_similarity2(model)
    elif choice == "3":
        semantic_search(model)
