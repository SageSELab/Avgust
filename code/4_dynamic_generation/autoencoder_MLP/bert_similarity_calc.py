from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class SimilarityCalculator_BERT:
    def __init__(self):
        self.model = SentenceTransformer('bert-base-nli-mean-tokens')

    def calc_similarity(self, s1, s2):
        s1_embedding = self.model.encode(s1)
        s2_embedding = self.model.encode(s2)
        return cosine_similarity([s1_embedding], [s2_embedding])

if __name__ == '__main__':
    menu = 'account order cart customer home service browse profile information support history story login menu settings'
    home = 'topic start list add continue trial show sign interested setup free follow'
    test = 'ui homescreen HomescreenTabsActivity'
    sentences = [ test, menu, home ]
    simcalc = SimilarityCalculator_BERT()
    for i in range(3):
        print(sentences[0], sentences[i], simcalc.calc_similarity(sentences[0], sentences[i]))

