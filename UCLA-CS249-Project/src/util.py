#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import tqdm
import string
import pandas as pd
import numpy as np
from nltk.corpus import stopwords #nlp库
from gensim.models.doc2vec import LabeledSentence
from gensim import utils

'''
#loading original data
@return: 
	all_data, the raw data with 4 fields: [ID, Gene, Variation, Text]
	train_size, 
	test_size

'''
def loadData():

	train_variant = pd.read_csv("../data/training_variants")
	test_variant = pd.read_csv("../data/stage2_test_variants.csv")
	train_text = pd.read_csv("../data/training_text", sep = "\|\|", engine = 'python', header=None, skiprows=1, names=["ID","Text"])
	test_text = pd.read_csv("../data/stage2_test_text.csv", sep = "\|\|", engine = 'python', header=None, skiprows=1, names=["ID","Text"])
	train1 = pd.merge(train_variant, train_text, how = 'inner', on = 'ID')

	#train2 is that we use some labeled 1st stage test data as training data too 
	train2_variant = pd.read_csv("../data/test_variants")
	train2_text = pd.read_csv("../data/test_text", sep = "\|\|", engine = 'python', header=None, skiprows=1, names=["ID","Text"])
	train2_solution = test_solution = pd.read_csv("../data/stage1_solution_filtered.csv", sep = ",")
	train2_id = train2_solution['ID'].values
	train2_tmp = np.array(train2_solution.drop('ID', axis = 1))
	train2_tmp2 = np.argmax(train2_tmp, axis = 1) + 1
	train2 = pd.DataFrame(np.vstack((train2_id, train2_tmp2)).T, columns = ['ID', 'Class'])
	train2 = pd.merge(train2_variant, train2, how = 'inner', on = 'ID')
	train2 = pd.merge(train2, train2_text, how = 'inner', on = 'ID')

	train = pd.DataFrame(np.concatenate((train1, train2), axis=0))
	train.columns = ["ID", "Gene", "Variation", "Class", "Text"]

	train_y = train['Class'].values
	train_y = np.array(train_y, dtype = int)
	train_x = train.drop('Class', axis = 1)
	train_size = len(train_x)

	test_x = pd.merge(test_variant, test_text, how = 'inner', on = 'ID')
	test_size = len(test_x)
	test_index = test_x['ID'].values

	all_data = np.concatenate((train_x, test_x), axis=0)
	all_data = pd.DataFrame(all_data)
	all_data.columns = ["ID", "Gene", "Variation", "Text"]
	print(all_data.head())
	return [all_data, train_size, test_size, train_x, train_y, test_x]

class Doc2VecParam:
	def __init__(self, min_count=1, window=5, size=200, sample=1e-4, negative=5, workers=4, iter=30, seed=1):
		self.min_count = min_count
		self.window = window
		self.size = size
		self.sample = sample
		self.negative = negative
		self.workers = workers
		self.iter = iter
		self.seed = seed

def Doc2VecWrapper(param):
	text_model = Doc2Vec(min_count=param.min_count, window=param.window, size=param.size, sample=param.sample, negative=param.negative, workers=param.workers, iter=param.iter, seed=param.seed)
	return text_model

