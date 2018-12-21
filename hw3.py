import os
import re
import sys
import numpy as np
reload(sys)
sys.setdefaultencoding('utf-8')

pos_dict = {} # NN -> dog 0.5, cat 0.3, etc
state_dict = {} # Begin_S -> DT 0.5, JJ 0.3, etc
# special_letters = ["(",")","\'\'","``",",","#","$",":"]
previous_pos = "Begin_Sent"
set_pos_tags = set(["Begin_Sent","End_Sent"])
total_count = 0

with open("/Users/jason/Downloads/hw3 2/WSJ_02-21.pos") as instream:
    for line in instream:
        line = line.strip(os.linesep)
        line = line.rstrip()
        line = line.split("\t")
        if len(line) != 2:
            previous_pos = "Begin_Sent"
            continue
        word, pos = line

        # Fill up the POS Dict
        cur_dict = pos_dict.get(pos, {})
        cur_dict[word] =  cur_dict.get(word,0)+1
        pos_dict[pos] = cur_dict
        set_pos_tags.add(pos)


        # Fill up the previous state Dict
        cur_dict = state_dict.get(previous_pos, {})
        cur_dict[pos] = cur_dict.get(pos, 0)+1
        state_dict[previous_pos] = cur_dict



        previous_pos = pos

with open("/Users/jason/Downloads/hw3 2/WSJ_24.pos") as instream:
    for line in instream:
        line = line.strip(os.linesep)
        line = line.rstrip()
        line = line.split("\t")
        if len(line) != 2:
            previous_pos = "Begin_Sent"
            continue
        word, pos = line

        # Fill up the POS Dict
        cur_dict = pos_dict.get(pos, {})
        cur_dict[word] =  cur_dict.get(word,0)+1
        pos_dict[pos] = cur_dict
        set_pos_tags.add(pos)


        # Fill up the previous state Dict
        cur_dict = state_dict.get(previous_pos, {})
        cur_dict[pos] = cur_dict.get(pos, 0)+1
        state_dict[previous_pos] = cur_dict



        previous_pos = pos

# Converting the dict into percentages
for _,cur_dict in pos_dict.iteritems():
    count = 0.
    for key, value in cur_dict.iteritems():
        count += value
    for key,value in cur_dict.iteritems():
        cur_dict[key] = float(value)/count

for _,cur_dict in state_dict.iteritems():
    count = 0.
    for key, value in cur_dict.iteritems():
        count += value
    for key,value in cur_dict.iteritems():
        cur_dict[key] = float(value)/count

sentences = []
with open("/Users/jason/Downloads/hw3 2/WSJ_23.words") as instream:
    sent = []
    for line in instream:
        word = line.strip(os.linesep)
        if word == "":
            sentences.append(sent)
            sent = []
            continue
        else:
            sent.append(word)

pos_tags = list(set_pos_tags)
for x in range(len(pos_tags)):
    if pos_tags[x] == ".":
        end_sent_tag = x

def state_to_string(state_num):
    state_str = []
    for num in state_num:
        if num == 999:
            state_str.append(".")
        else:
            state_str.append(pos_tags[num])
    return state_str

def process_oov_words(tag, word, previous_pos,word_val):
    if tag.isalpha() and not word.isalpha():
        word_val = 0.
    elif tag == "NNP" and word[0].isupper() and previous_pos != "Begin_Sent":
        word_val = 1. #if word starts with caps lock and is OOV then it's probably NNP
    elif tag == "NNP" and not word[0].isupper():
        word_val = 0.

    return word_val


def find_max_of_last(matrix,prev_tags,num_tags):
    max_end_val = -1
    max_end_prev = -1
    for a in range(num_tags):
        if (matrix[a,num_words-1] > max_end_val):
            max_end_val = matrix[a,num_words-1]
            max_end_prev = prev_tags[a,num_words-1]

    return max_end_val, max_end_prev

counter = 0
all_states = []
for sentence in sentences:
    counter += 1
#     if counter > 10: break
    num_tags = len(pos_tags)
    num_words = len(sentence)+2
    matrix = np.zeros([num_tags,num_words],dtype=float)
    prev_tags = np.zeros([num_tags,num_words],dtype=int)


    #Fill up the beginning of the sentence
    for x in range(len(pos_tags)):
        if pos_tags[x] == "Begin_Sent":
            matrix[x,0] = 1

    previous_pos = "Begin_Sent"


    for y in range(1,num_words):

        # Handling the end
        if y == num_words-1:
            for z in range(len(pos_tags)):
                previous_pos = pos_tags[z]
                if previous_pos == "End_Sent": continue
                cur_val = state_dict[previous_pos].get(pos_tags[end_sent_tag],0) * matrix[z,y-1]
                cur_max = matrix[x,y]

                if (cur_val > cur_max):
                    matrix[x,y] = cur_val
                    prev_tags[x,y] = z
            break

        for x in range(len(pos_tags)):

    #       All other cases
            word = sentence[y-1]
            tag = pos_tags[x]
            if tag == "Begin_Sent" or tag == "End_Sent":
                matrix[x,y] = 0
                continue
            word_val = pos_dict[tag].get(word,1./1000)

            for z in range(len(pos_tags)):
                previous_pos = pos_tags[z]
                if previous_pos == "End_Sent":
                    continue
                elif tag == "End_Sent":
                    break
                state_transition_val = state_dict[previous_pos].get(tag,0)
                if state_transition_val == 0: continue #if the transition isn't possible then continue

                if (word_val == 1./1000): # OOV word
                    word_val = process_oov_words(tag, word, previous_pos,word_val)
                if word_val == 0: continue

                cur_val = state_transition_val * word_val * matrix[z,y-1]
                cur_max = matrix[x,y]

                if (cur_val > cur_max):
                    matrix[x,y] = cur_val
                    prev_tags[x,y] = z

    max_end_val,max_end_prev = find_max_of_last(matrix,prev_tags,num_tags)

    states = np.zeros(num_words,dtype=int)
    states[num_words-1] = 999
    previous = max_end_prev
    for x in range(num_words-2,-1,-1):
        states[x] = previous
        previous = prev_tags[previous, x]

    state = state_to_string(states)
    state = state[1:-1]
    all_states.append(state)

myfile = open("/Users/jason/Downloads/hw3 2/jjl625.pos","w")
for n in range(len(all_states)):
    state = all_states[n]
    sent = sentences[n]
    for x in range(len(state)):
        myfile.write("{}\t{}\n".format(sent[x],state[x]))
    myfile.write("\n")
myfile.close()
