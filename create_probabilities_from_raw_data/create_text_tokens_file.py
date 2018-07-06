import glob
import codecs
from tokenize_text import tokenize_word
import os


def create(dundee_path, tokenized_corpus_filename, tokenized_line_filename):
    sentence_end = set(['?', '!', '.'])
    sentence_begin = True

    word_string = ''
    word_num_token_list = []
    n_tokens = 0

    # Change a few symbols that cause issues with tokenization
    # Output two files:
    #   One corpus file with one sentence per line
    #   One corpus file with one token per line
    #       Punctuation constitutes a separate token
    for word_file in glob.glob(dundee_path):
        print('Processing file {}'.format(word_file))
        file_id = os.path.basename(word_file)[2:4]
        with codecs.open(word_file, 'r', encoding='utf-8', errors='ignore') as word_list:
            for index, line in enumerate((word_list)):
                if sentence_begin:
                    sentence_begin = False
                word_info = line.split()
                word = word_info[0]
                # break word into tokens
                token_list = []
                if word == "...":
                    token_list = ['.']
                elif word == ".":
                    token_list = ["."]
                elif word == "-":
                    token_list = ['-']
                else:
                    tokenize_word(word, token_list)

                n_tokens += len(token_list)

                for token in token_list:
                    word_string += '{} '.format(token)
                    word_num_token_list.append([file_id, index+1, "\"{}\"".format(token)])

                # if any of the tokens are sentence-ending punctuation
                ## add sentence terminal </s>, and new line
                ## </s> has no index
                if any(i in token_list for i in sentence_end):
                    word_string += " \n"
                    n_tokens += 1
                    word_num_token_list.append([file_id, "NA", "</s>"])
                    sentence_begin = True
                # reset token_list
                token_list.clear()

    print('{} tokens'.format(n_tokens))

    # print one tokenized sentence per line
    with open(tokenized_corpus_filename, 'w') as outf:
        outf.write(word_string)

    # print one token per line
    with open(tokenized_line_filename, 'w') as linef:
        for token_index in word_num_token_list:
            linef.write('{},{},{}\n'.format(token_index[0], token_index[1], token_index[2]))

    return word_string