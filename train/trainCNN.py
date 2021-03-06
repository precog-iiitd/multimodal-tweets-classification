

import json
import sys ; sys.path.insert(0, '..')
import numpy as np

import Models , ProcessData , Datasets , Config 

nVocab = ProcessData.Tweets.nVocab
model = Models.ReccurentLanguage.simpleGRU( nVocab )

from keras.optimizers import SGD
cnn_model = Models.GAP.VGG_GAP( useWeights=False , nFreez=13 , nClasses= 2  , optimizer=SGD(lr=0.0006, momentum=0.9)   )
cnn_model.load_weights(  Config.project_root +  "/model_weights/5_epochs_90_percent.w"  )

def getGen( cvsFiles=[] , splitPercentage=0.2 , split='train' , downsampeling=False ):

	positives , negatives = Datasets.SensitiveTweets.getTweets(  cvsFiles ,  splitPercentage , split , downsampeling  , out='pairs' )


	def getSentences():
		while True:
			p = positives.pop(0)
			n = negatives.pop(0)
			positives.append(p)
			negatives.append(n)

			yield p , n

	def gen():
		batch_size = 32
		G = getSentences()
		while True:
			X = []
			Y = []
			XI = []
			
			for i in range(batch_size):
				p , n = G.next()
				X.append( ProcessData.Tweets.getSentenceVec(p['text']) )
				X.append( ProcessData.Tweets.getSentenceVec(n['text']) )

				XI.append( ProcessData.Images.getImageVec(p['img']  , width=224 , height=224 ) )
				XI.append( ProcessData.Images.getImageVec(n['img']  , width=224 , height=224 ) )

				Y.append(  np.array([0,1]) )
				Y.append(  np.array([1,0]) )

			yield   np.array(XI) , np.array( Y )

	return gen()

import glob

files = glob.glob( "../../data/prepped/tweets_annotated_2/*.prepped.json" ) #+ glob.glob( "data/t1/*.csv" )
 

v = getGen(cvsFiles=files , downsampeling=False   )
v2 = getGen(  cvsFiles=files , split='val')

cnn_model.fit_generator( v , samples_per_epoch=500 , validation_data=v2  , nb_val_samples=200,  nb_epoch=100 )





