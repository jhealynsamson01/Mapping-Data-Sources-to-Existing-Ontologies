import torch
from sentence_transformers import SentenceTransformer, util
from datasource_mappings.reusable_modules.load_ontology import fetch_ontology_classes


def s_bert(onto, keywords_list):
    new_classes = fetch_ontology_classes(onto)

    # Task: Use S-Bert to match keywords to class names
    # Reference: https://www.sbert.net/docs/usage/semantic_textual_similarity.html
    model = SentenceTransformer('all-MiniLM-L6-v2')  # preTrained model

    # Compute embedding for both lists
    embeddings1 = model.encode(keywords_list, convert_to_tensor=True)
    embeddings2 = model.encode(new_classes, convert_to_tensor=True)

    # Compute cosine-similarities
    cosine_scores = util.cos_sim(embeddings1, embeddings2)

    # Task: Pick Top Scoring label that matches with keyword as per the cos_sim function, set a threshold and create new class if threshold is not met.
    result = dict()  # Dictionary with Result for SBert
    create_class = dict()
    temp_class = dict()
    choices = []

    k = torch.topk(cosine_scores, 5, dim=1, largest=True, sorted=True)
    for i in range(len(keywords_list)):
        for index in range(5):
            # print("Key Word:{} \tSuggested Class(label):{} \tScore:{:.4f}".format(keywords_list[i],
            #                                                                       new_classes[k.indices[i][index]],
            #                                                                       k.values[i][index]))
            if k.values[i][0] < 0.4:
                create_class.update({keywords_list[i]: keywords_list[i].replace(" ", "")})
            elif 0.8 > k.values[i][0] > 0.4:
                choices.append([keywords_list[i], new_classes[k.indices[i][index]], k.values[i][index]])
        if k.values[i][0] > 0.8:
            temp_class.update({keywords_list[i]: keywords_list[i].replace(" ", "")})
    return result, create_class, choices, temp_class
