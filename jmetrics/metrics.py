import pandas as pd
import os
import sys
import glob
from jmetrics.utils import _get_facet_data
from datetime import datetime
from datetime import date
from operator import itemgetter
import numpy as np

class Metrics(object):
    """

    """
    def __init__(self, config={}):
        """
        Initializes the class
        """
        # ============================= INITIALIZATION ==================================== #
        from adsputils import setup_logging, load_config
        proj_home = os.path.realpath(os.path.join(os.path.dirname(__file__), '../'))
        self.config = load_config(proj_home=proj_home)
        if config:
            self.config = {**self.config, **config}
        self.logger = setup_logging(__name__, proj_home=proj_home,
                                level=self.config.get('LOGGING_LEVEL', 'INFO'),
                                attach_stdout=self.config.get('LOG_STDOUT', False))
        # The names of output files will have a date string in them
        self.dstring = datetime.today().strftime('%Y%m%d')
    # ============================= MAIN FUNCTIONALITY ================================ #
    def get_metrics(self, year):
        """
        For a given year and metrics type, generate journal metrics
    
        param: year: year for which metrics are calculated
        """
        self.journal_data = {}

    def _get_journal_data(self, year):
        """
        Get publication data on journal level
        """
        query = 'property:refereed doctype:article year:{0}-{1}'.format(year-5, year-1)
        self.journal_data = _get_facet_data(self.config, query, 'bibstem_facet')

class Eigenfactor(Metrics):
    def __init__(self, config={}):
        """
        Initializes the class and prepares a (temporary) lookup facility for
        curators reporting. This lookup facility will be replaced by an API
        query eventually
        """
        super(Eigenfactor, self).__init__(config=config)
    
    def get_metrics(self, year):
        """
        param: year: year for which metrics are calculated
        """
        super(Eigenfactor, self).get_metrics(year)
        # Get some necessary data for this calculation
        # Get a dictionary mapping journal abbreviations to
        # article counts for the 5-year publication window
        self._get_journal_data(int(year))
        # The journal set is determined from the keys of the dictionary
        # A length restriction is applied to the keys to filter out
        # entries we're not interested in (like refereed books and tmp bibstems)
        self.journals = [j for j in self.journal_data.keys() if len(j)<=5]
        # Determine adjacency matrix for these journals and time frame
        adj = self._get_adjacency_matrix(year)
        # Get the article vector a
        a = self._get_article_vector()
        # Normalize adjacency matrix
        adj_norm, d = self._normalize_adjacency_matrix(adj)
        # Determine the (stationary) Influence Vector
        pi = self._get_influence_vector(adj_norm, a, d)
        # The Influence Vector determines the Eigenfactors
        top_term = adj_norm @ pi
        ef = 100 * (top_term / top_term.sum(0))
        # Finally get the journal rankings
        ranks = self._get_journal_ranking(ef)
    
    def _get_adjacency_matrix(self, year):
        c = np.zeros((len(self.journals), len(self.journals)))
        with open(self.config.get('ADS_CITATION_DATA')) as fh:
            for line in fh:
                citing, cited = line.strip().split('\t')
                try:
                    i = self.journals.index(citing[4:9])
                    j = self.journals.index(cited[4:9])
                except:
                    continue
                c[i,j] += 1
        # Self-citations are disregarded, so we will remove these
        np.fill_diagonal(c, 0)
        return c
    
    def _get_article_vector(self):
        # Instantiate the article vector with zeros
        a = np.zeros((len(self.journals), 1))
        # Get the vector of article counts for the journals in the set
        for key, val in self.journal_data.items():
            try:
                i = self.journals.index(key)
            except:
                continue
            a[i, 0] = val
        # Normalize each entry by the total number of articles in the set
        art_norm = a / sum(a)
        return art_norm

    def _normalize_adjacency_matrix(self, A):
        # H will store the normalized adjacency matrix
        H = np.zeros_like(A)
        # d will be a vector indicating which columns represent dangling nodes
        d = np.zeros((1, H.shape[0]), dtype=int)
        # For all columns that have a non-zero column sum, we normalize
        # otherwise we add a value 1 to the "dangling vector"
        for i, val in enumerate(A.sum(axis=0).tolist()):
            if val:
                H[:,i] = A[:,i] / val
            else:
                d[0,i] = 1
        return H, d
    
    def _get_influence_vector(self, H, a, d):
        # Instantiate the influence vector
        pi = np.ones((H.shape[0], 1)) / H.shape[0]
        # Get some of the algorithm parameters
        max_iter = self.config('MAX_INTEREATIONS')
        alpha = self.config('ALPHA')
        epsilon = self.config('EPSILON')
        # Iterate the update equation till convergence has been reached
        for i in range(0, max_iter):
            pi_next = alpha*H @ pi + (alpha * (d @ pi) + (1-alpha)).item(0)*a
            norm = np.linalg.norm(pi_next - pi, ord=1)
            if norm < epsilon:
                break
            pi = pi_next
        return pi_next
    
    def _get_journal_ranking(self, EF):
        scores = {}
        ranking = {}
        for i, sc in enumerate(EF):
            scores[sc.item(0)] = self.journals[i]

        ranks = OrderedDict(sorted(scores.items(), key=lambda t: t[0], reverse=True))
        for i, (k, v) in enumerate(ranks.items()):
            ranking[v] = {'rank': (i+1), 'score': k}
        return ranking
            



    