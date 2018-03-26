# -*- coding: utf-8 -*-
'''
svakulenko
17 Mar 2018

Basic LSTM architecture in Keras with pre-trained embeddings in the input layer
for classification of dialogues given DBpedia concept annotations as input:
    1 - real (coherent) dialogue
    0 - fake (incoherent) dialogue
    generated by corrupting (preturbing) training samples

https://machinelearningmastery.com/use-word-embedding-layers-deep-learning-keras/
'''
import numpy as np
import gensim

from keras.models import Sequential
# from keras.layers import Flatten
from keras.layers import Dense, Dropout, Embedding, Activation
from keras.layers import Conv1D, GlobalMaxPooling1D
from keras.callbacks import EarlyStopping, ModelCheckpoint

from preprocess import populate_emb_matrix_from_file

# PATH_EMBEDDINGS = './embeddings/data.dws.informatik.uni-mannheim.de/rdf2vec/models/DBpedia/2015-10/noTypes/db2vec_sg_200_5_25_5'

# define the model params
# vocab_size = len(vocabulary)


# def load_embeddings(vocabulary, emb_path=PATH_EMBEDDINGS):
#     # load pre-trained KG entity embeddings
#     vector_model = gensim.models.Word2Vec.load(emb_path)
#     print('Loaded %s entity vectors.' % len(vector_model.wv))

#     # create a weight matrix for entities in training docs
#     embedding_matrix = zeros((vocab_size, embeddings_dim))
#     for entity, i in vocabulary.items():
#         embedding_vector = vector_model.wv.get(entity)
#         if embedding_vector is not None:
#             embedding_matrix[i] = embedding_vector

#     del vector_model
#     # save embedding_matrix for entities in the training dataset
#     return embedding_matrix


def get_cnn_architecture(vocabulary_size, embedding_matrix, input_length, embeddings_dim):
    # define the CNN model architecture
    # adopted from https://github.com/keras-team/keras/blob/master/examples/imdb_cnn.py
    
    # model parameters:
    filters = 250
    kernel_size = 3
    hidden_dims = 250

    model = Sequential()
    model.add(Embedding(vocabulary_size, embeddings_dim, weights=[embedding_matrix],
                        input_length=input_length, trainable=False))
    model.add(Dropout(0.2))
    # we add a Convolution1D, which will learn filters
    # word group filters of size filter_length:
    model.add(Conv1D(filters,
                     kernel_size,
                     padding='valid',
                     activation='relu',
                     strides=1))
    # we use max pooling:
    model.add(GlobalMaxPooling1D())
    # We add a vanilla hidden layer:
    model.add(Dense(hidden_dims))
    model.add(Dropout(0.2))
    model.add(Activation('relu'))
    # We project onto a single unit output layer, and squash it with a sigmoid:
    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    # # compile the model
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    
    return model


def train(X_train, y_train, X_val, y_val, vocabulary_size, input_length, embeddings, label, batch_size=128, epochs=5):
    '''
    Train CNN for classification of dialogues as entity sets
    '''
    # embedding_matrix = populate_emb_matrix_from_file(vocabulary)
    # load saved embeddings matrix for the input layer
    embedding_matrix = np.load(embeddings['matrix_path'])

    # number of non-zero rows, i.e. entities with embeddings
    print len(np.where(embedding_matrix.any(axis=1))[0])
    # print embedding_matrix

    model = get_cnn_architecture(vocabulary_size, embedding_matrix, input_length, embeddings['dims'])
    # # summarize the model
    # print(model.summary())

    early_stopping = EarlyStopping(monitor='val_loss', patience=42)
    best_weights_filepath = 'models/%s.h5' % label
    model_checkpoint = ModelCheckpoint(best_weights_filepath, monitor='val_loss', verbose=0, save_best_only=True, save_weights_only=True, mode='auto')

    # begin training validation_split=0.2, 
    model.fit(X_train, y_train, epochs=epochs, verbose=1, batch_size=batch_size, validation_data=(X_val, y_val), callbacks=[early_stopping, model_checkpoint])
    
    #reload best weights
    model.load_weights(best_weights_filepath)
    return model
