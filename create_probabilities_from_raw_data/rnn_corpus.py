import timeit
from csv import reader
from csv import writer
from google_lm import GoogleLanguageModel
from tokenize_text import tokenize_word
from tokenize_text import punctuation_set
import glob
import os
import codecs
from string import punctuation
os.environ['TF_CPP_MIN_LOG_LEVEL']='3' # suppress build warnings

sentence_end = set(['?', '!', ';', ',', ':']) #set(['.', '?', '!', ';', ',', ':']) #no comma?


def create(token_corpus_line_file, rnn_probability_file):
    # initialize lstm
    tic = timeit.default_timer()
    glm = GoogleLanguageModel()
    glm.load_affine_transformation()
    toc = timeit.default_timer()
    print("Model built in {} seconds".format(toc - tic))

    inputs, char_ids_inputs, feed_dict, lstm, lstm_state = glm.process_init()

    # loop through corpus
    with open(token_corpus_line_file, 'r') as token_file:
        with open(rnn_probability_file, 'w') as rnn_file:
            csv_reader = reader(token_file)
            for token_line in csv_reader:
                file_id = token_line[0]
                token_index = token_line[1]
                token = token_line[2]
                # print(token_index)

                # calculate probability of each token and sum
                # update model with each token
                token_probability = glm.get_logprob(lstm_state, token)

                inputs, char_ids_inputs, feed_dict, lstm, lstm_state = \
                    glm.process_word(token, inputs, char_ids_inputs, feed_dict, lstm)

                rnn_file.write('{},{},\"{}\",{}\n'.format(file_id, token_index, token, token_probability))

                # when the sentence changes (sentence-ending punctuation is detected), reinitialize the model
                if token == "</s>":
                    inputs, char_ids_inputs, feed_dict, lstm, lstm_state = glm.process_init()
                    # print('Reinitializing')

    toc = timeit.default_timer()
    print("Elapsed time: {} seconds".format(toc - tic))