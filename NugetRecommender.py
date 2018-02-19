import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

def _compute_description_scores(df):
    vectorizer = TfidfVectorizer(ngram_range=(1, 3),
                                 stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(df['description'])
    cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)
    return cosine_similarities

def _compute_tags_scores(df):
    vectorizer = TfidfVectorizer()
    space_separated_tags = [tags.replace(',', ' ') for tags in df['tags']]
    tfidf_matrix = vectorizer.fit_transform(space_separated_tags)
    cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)
    return cosine_similarities

class NugetRecommender(object):
    def __init__(self, weights={'description': 0.7, 'tags': 0.3}):
        self.weights_ = weights

    def fit(self, df):
        # Let m be the number of packages. For each relevant feature like shared tags or similar names/descriptions,
        # compute a m x m matrix called M, where M[i][j] represents how relevant package j is to package i based on
        # that feature alone.
        # Set self.scores_ to an m x m matrix of aggregate scores by taking a weighted average of these matrices.
        self._df = df

        feature_scores = [
            _compute_description_scores(df),
            _compute_tags_scores(df),
        ]

        feature_weights = [
            self.weights_['description'],
            self.weights_['tags'],
        ]

        self.scores_ = np.average(feature_scores, weights=feature_weights, axis=0)

    def predict(self, top_n):
        dict = {}
        for index, row in self._df.iterrows():
            package_id = self._df['id'][index]
            recommendation_indices = self.scores_[index].argsort()[:-top_n:-1]
            recommendations = [self._df['id'][i] for i in recommendation_indices]
            dict[package_id] = recommendations

        return dict
