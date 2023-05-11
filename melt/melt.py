import os, sys, json
import numpy as np
import pandas as pd

from tqdm import tqdm, trange

import string

import nltk
nltk.download('stopwords')
nltk.download('punkt')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from nltk.stem.snowball import SnowballStemmer

from bicm import BipartiteGraph as BiG

class melt:
    """
    
    """
    def __init__(self, data, lang=None, binary=True):
        '''
        :param data pd.DataFrame : the data. So far only two columns dataframes are allowed. I am assuming that the first is the id, the second is the text. 
        :param lang string: the language to be analyzed. Default is English.
        :param binary bool: if the analysis should be based on a binary or weighted bipartite network. Default is binary
        '''
        
        # read data
        self.data=data
        self.data_col=data.columns
        
        # read language
        if lang is None:
            self.lang="english"
        else:
            # check that english is among the accepted languages by nltk
            self.lang=lang
            
        # is the analysis intended to work on binary or weighted bipartite networks?
        # default is binary
        self.binary=binary
        
        # basics
        self.l_data=len(self.data)
        # get the stemmer 
        self.stemmer = SnowballStemmer(self.lang, ignore_stopwords=True)
        
        # get the biadjacency llist
        #self.get_ball()
        
        # randomize the bipartite network using the "celebrated" BiCM
        #self.get_bicm()
        
    
    def get_ball(self):
        '''
        It returns the biadjacency list associated to the bipartite network of id and tokens
        '''
        self.biadj_list={}
        for i in range(self.l_data):
            _id=self.data.iloc[i][self.data_col[0]]
            _text=self.data.iloc[i][self.data_col[1]]
            self.biadj_list[_id]=self.text2tokens(_text)  
    
    
    def text2tokens(self, text):
        stop_words = list(stopwords.words(self.lang))
        bad_char=['©', '–', '‘', '’', '“', '”']
        word_tokens = [wt.lower() for wt in word_tokenize(text)]
        out=[]
        for w in word_tokens:
            if not (w in stop_words) and not (w in bad_char) and not (w in string.punctuation) and not ('.' in w) and not (',' in w) and not w.isnumeric():
                # I am removing:
                # - stop words;
                # - punctuation
                # - fractional numbers
                out.append(self.stemmer.stem(w))
        if self.binary:
            return np.unique(out)
        else:
            return np.unique(out, return_counts=True)
        
    def get_bicm(self, **kwrds):
        '''
        It takes as parameters the same one as in bicm.
        '''
        self.MyGraph = BiG()
        self.MyGraph.set_adjacency_list(self.biadj_list)
        self.MyGraph.solve_tool(**kwrds)
        
        
    def get_projection(self, **kwrds):
        '''
        It takes as parameters the same one as in bicm.
        '''
        self.MyGraph.compute_projection(**kwrds)
        if self.MyGraph.rows_projection:
            self.id_proj={}
            # I want to return an explicit dictionary
            for key in self.MyGraph.projected_rows_adj_list.keys():
                new_key=self.MyGraph.rows_dict[key]
                self.id_proj[new_key]=[self.MyGraph.rows_dict[other_key] for other_key in self.MyGraph.projected_rows_adj_list[key]]  
        else:
            self.token_proj={}
            # I want to return an explicit dictionary
            for key in self.MyGraph.projected_columns_adj_list.keys():
                new_key=self.MyGraph.columns_dict[key]
                self.token_proj[new_key]=[self.MyGraph.columns_dict[other_key] for other_key in self.MyGraph.projected_columns_adj_list[key]]  

            
    def save_me(self):
        pass
        
