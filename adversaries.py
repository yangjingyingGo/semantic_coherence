# -*- coding: utf-8 -*-
'''
svakulenko
31 Mar 2018

Different negative sampling strategies to produce adversary samples by corrupting true positive samples
'''
import numpy as np
import random
from keras.preprocessing.sequence import pad_sequences

from prepare_dataset import load_vocabulary
from prepare_dataset import LATEST_SAMPLE
from sample291848 import entity_distribution, word_distribution


def generate_uniform_random(folder, sample=LATEST_SAMPLE, test='test/', **kwargs):
    '''
    Pick items from the vocabulry unifromly at random using the same length as of a positive example
    '''
    # load vocabulary
    vocabulary = load_vocabulary('./%s/%s/vocab.pkl' % (sample, folder))
    # load positive samples
    positives = np.load('./%s/%s/%spositive_X.npy' % (sample, folder, test))

    adversaries = []
    
    for dialogue in positives:
        adversaries.append(random.sample(xrange(0, len(vocabulary)), len(dialogue)))

    assert len(adversaries) == len(positives)
    np.save('./%s/%s/%srandom_X.npy' % (sample, folder, test), adversaries)


def generate_vocabulary_distribution(folder, vocabulary_distribution, sample=LATEST_SAMPLE, test='test/'):
    '''
    Pick items from the vocabulry unifromly at random using the same length as of a positive example
    '''
    # load vocabulary
    vocabulary = load_vocabulary('./%s/%s/vocab.pkl' % (sample, folder))
    # load positive samples
    positives = np.load('./%s/%s/%spositive_X.npy' % (sample, folder, test))

    adversaries = []

    # prepare probabilities from vocabulary counts distribution
    entities = vocabulary_distribution.keys()
    entities_counts = vocabulary_distribution.values()
    entities_probs = [count / float(sum(entities_counts)) for count in entities_counts]

    
    for dialogue in positives:
        adversaries.append(np.random.choice(entities, replace=False, size=len(dialogue), p=entities_probs))

    assert len(adversaries) == len(positives)
    np.save('./%s/%s/%sdistribution_X.npy' % (sample, folder, test), adversaries)


def generate_sequence_disorder(folder, sample=LATEST_SAMPLE, test='test/', **kwargs):
    '''
    Randomly rearrange (permute) the original sequence (sentence ordering task)
    '''
    # load positive samples
    positives = np.load('./%s/%s/%spositive_X.npy' % (sample, folder, test))

    adversaries = []
    
    for dialogue in positives:
        # randomly permute list of ids
        adversaries.append(random.shuffle(dialogue))

    assert len(adversaries) == len(positives)
    np.save('./%s/%s/%sdisorder_X.npy' % (sample, folder, test), adversaries)


def generate_adversaries(generator):
    vocabulary_distributions = [entity_distribution, word_distribution]
    for i, folder in enumerate(['entities', 'words']):
        # development
        generator(folder, test='', vocabulary_distribution=vocabulary_distributions[i])
        # test set
        generator(folder, vocabulary_distribution=vocabulary_distributions[i])


if __name__ == '__main__':
    generate_adversaries(generate_vocabulary_distribution)
