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
    def __init__(self, data, lang=None, binary=True, columns=None):
        '''
        :param data pd.DataFrame : the data. So far only two columns dataframes are allowed. I am assuming that the first is the id, the second is the text. 
        :param lang string: the language to be analyzed. Default is English.
        :param binary bool: if the analysis should be based on a binary or weighted bipartite network. Default is binary
        :param columns list: list of the columns to use in the case of pandas DataFrames. It is a list of integers.
        '''
        
        # read data
        self.data=data
        
        if str(type(self.data))=="<class 'pandas.core.frame.DataFrame'>":
            # data is a pandas DataFrame
            self.data_type='pandas_dataframe'
            self.data_col=data.columns
            
            if len(self.data_col)>2 and columns==None:
                raise Exception('Too many columns in the DataFrame: select the columns with the text to be analysed.')
            elif len(self.data_col)>2:
                assert type(columns)==list, 'Columns should be a list of integers, selecting the proper columns to be analysed. The first one is going to be the identifier of the text (i.e. the id), the second one the text to be analysed'
                assert all([type(c)==int for c in columns]), 'Columns should be a list of integers, selecting the proper columns to be analysed. The first one is going to be the identifier of the text (i.e. the id), the second one the text to be analysed'
                assert all([c<len(self.data_col) for c in columns]), "Not all entries in the 'columns' list are in the proper interval"
                self.data_col=data.columns[columns]
                self.data=data[columns]
                
                
        elif str(type(self.data))=="<class 'pandas.core.series.Series'>":
            # data is a pandas Series
            self.data_type='pandas_series'
        
        elif type(self.data)==list:
            if type(self.data[0])==str:
                # data is a list
                self.data_type='list'
            elif type(self.data[0])==list:
                # data is a list of list
                self.data_type='lol'
                if columns==None:
                    assert all([len(c)==2 for c in self.data]), 'Too many columns in the list: select the columns with the text to be analysed.'
                else:
                    assert all([c<len(self.data[0]) for c in columns]), "Not all entries in the 'columns' list are in the proper interval"
                    self.data=[[data[c] for c in columns] for data in self.data]
        else:
            raise Exception('I cannot recognize the input data type')
                    
                

        
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
        self.get_ball()
        
    
    def get_ball(self):
        '''
        It returns the biadjacency list associated to the bipartite network of id and tokens
        '''
        self.biadj_list={}
        for i in range(self.l_data):
            if self.data_type=='pandas_dataframe':
                _text=self.data.iloc[i][self.data_col[1]]
                tokens=self.text2tokens(_text)  
                _id=self.data.iloc[i][self.data_col[0]]
                self.biadj_list[_id]=tokens
            elif self.data_type=='pandas_series':
                _text=self.data.iloc[i]
                tokens=self.text2tokens(_text)  
                self.biadj_list[i]=tokens
            elif self.data_type=='list':
                _text=self.data[i]
                tokens=self.text2tokens(_text)  
                self.biadj_list[i]=tokens
            elif self.data_type=='lol':
                _text=self.data[i]
                tokens=self.text2tokens(_text)  
                self.biadj_list[self.data[i][0]]=tokens
                    
        
    
    def text2tokens(self, text):
        stop_words = list(stopwords.words(self.lang))
        bad_char=['©', '–', '‘', '’', '“', '”', "''", "'s",'``']
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
            aux=np.unique(out, return_counts=True)
            return dict(zip(aux[0], aux[1]))
        
    def get_bicm(self, **kwrds):
        '''
        It takes as parameters the same ones as in bicm.
        '''
        self.MyGraph = BiG()
        self.MyGraph.set_adjacency_list(self.biadj_list)
        self.MyGraph.solve_tool(**kwrds)
        
        
    def get_projection(self, **kwrds):
        '''
        It takes as parameters the same ones as in bicm.
        '''

        if not hasattr(self, 'MyGraph'):
            self.get_bicm()

        self.MyGraph.compute_projection(**kwrds)
        if self.MyGraph.rows_projection:
            if hasattr(self.MyGraph, 'projected_rows_adj_list'):
                self.id_proj={}
                # I want to return an explicit dictionary
                for key in self.MyGraph.projected_rows_adj_list.keys():
                    new_key=self.MyGraph.rows_dict[key]
                    self.id_proj[new_key]=[self.MyGraph.rows_dict[other_key] for other_key in self.MyGraph.projected_rows_adj_list[key]] 
 
        if self.MyGraph.cols_projection::
            if hasattr(self.MyGraph, 'projected_columns_adj_list'):
                self.token_proj={}
                # I want to return an explicit dictionary
                for key in self.MyGraph.projected_columns_adj_list.keys():
                    new_key=self.MyGraph.columns_dict[key]
                    self.token_proj[new_key]=[self.MyGraph.columns_dict[other_key] for other_key in self.MyGraph.projected_columns_adj_list[key]]  

            
    def save_me(self):
        pass
        
