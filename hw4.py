#!/usr/bin/env python

"""Text generation from Green, Eggs, and Ham using a first-order Markov chain

Source text: https://www.clear.rice.edu/comp200/resources/texts/Green%20Eggs%20and%20Ham.txt
"""

__author__ = "Ina Tang"
__date__ = "2025-04-23"

import math
import random
import numpy as np
import pandas as pd


########################################
# Read file & Create transition matrix #
########################################

green_eggs_ham: list[str] = []
count_df: pd.DataFrame = pd.DataFrame(columns=['state', 'count'])
transition_df: pd.DataFrame = pd.DataFrame()

# Read the text file and split it into words
with open('greenEggsHam.txt', 'rt', encoding='utf-8') as f: 
    simple_split: list[str] = f.read().split()

    # Separate punctuations from words
    for state in simple_split:
        decomposed: list[str] = []
        alpha_word: str = ''
        for c in state:
            if c in ('!', '?', '.', ',', "'", '"'):
                if alpha_word: decomposed.append(alpha_word)
                decomposed.append(c)
                alpha_word = ''
            else:
                if c: alpha_word += c

        if alpha_word: decomposed.append(alpha_word)
        green_eggs_ham.extend(decomposed)
    
    # Count the number of occurrences of each state
    for state in green_eggs_ham: 
        seen: np.ndarray = count_df['state'].values
        if state in seen: 
            count_df.loc[count_df['state'] == state, ['count']] += 1
        else:
            count_df = pd.concat([count_df, pd.DataFrame({'state': [state], 'count': [1]})], ignore_index=True)

count_df = count_df.sort_values(by='count', ascending=False)
# count_df.to_csv('word_count.csv', index=False, header=True)
# print("Successfully saved word_count.csv")


# Count the transition frequencies of each word
# Transition matrix: Let row be the previous word and let column be the current word. 
# Then a_{rc} = frequency of c given r is previous word. 
transition_df = pd.DataFrame(0, columns=count_df['state'].values, index=count_df['state'].values)

previous_word = green_eggs_ham[0]
for state in green_eggs_ham[1:]:  # inefficient, but simple
    transition_df.loc[previous_word,state] += 1
    previous_word = state

transition_df['total_freq'] = count_df['count'].values  # works w/o sorting df
# transition_df.to_csv('transition_freq.csv', index=True, header=True)
# print("Successfully saved transition_freq.csv")


# Compute the transition probabilities
transition_df = transition_df.astype('float')

for w1 in transition_df.columns:
    for w0 in transition_df.index:
        # Accept zero division as zero probability
        if transition_df.loc[w0, 'total_freq'] == 0: 
            transition_df.loc[w0, w1] = 0
            continue

        transition_df.loc[w0, w1] /= transition_df.loc[w0, 'total_freq']

# transition_df.to_csv('transition_matrix.csv', index=True, header=True)
# print("Successfully saved transition_matrix.csv")


#######################
# Sequence generation #
####################### 

def generate_sequence(start_word: str, length: int) -> list[str]:
    def helper(length: int, sequence: list[str]=[start_word]) -> list[str]: 
        if len(sequence) == length: 
            return sequence
        
        rand: float = random.random()

        cdf: float = 0
        last_state: str = start_word if len(sequence) == 1 else sequence[-1]
        word_row_df: pd.DataFrame = transition_df.loc[last_state]
        for next_state in transition_df.columns[:-1]:  # loop through column in row of last state
            p: float = word_row_df[next_state]
            cdf += p
            if cdf > rand or math.isclose(cdf, 1.0): 
                sequence.append(next_state)
                print(next_state)
                break

        return helper(length, sequence)
    
    return " ".join(helper(length))  # convert to paragraph


##############
# Submission #
##############

# Tokens
count_df['state'].to_csv('tokens.csv', header=False, index=False, )

# Transition matrix
transition_df.to_csv('transition_matrix.csv', header=True, index=True)

# Paragraphs
NUMBER_OF_PARAGRAPHS: int = 3
START_WORD: str = 'I'
LENGTH: int = 150

with open('paragraphs.txt', mode='wt', encoding='utf-8') as f: 
    for i in range(NUMBER_OF_PARAGRAPHS): 
        f.write(generate_sequence(START_WORD, LENGTH) + '\n')  # for readability
