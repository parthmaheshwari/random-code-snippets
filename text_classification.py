import re
from nltk.tokenize import sent_tokenize, word_tokenize 
import nltk
from nltk.corpus import stopwords
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import tensorflow as tf
import pandas as pd
import numpy as np
import string
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
import os
import tempfile
import matplotlib.pyplot as plt
from tensorflow.python.keras.preprocessing import sequence

#natural language processing on text sequences
def preprocessing(input_str):
    input_str = input_str.lower() # lower case
    input_str = re.sub(r"\d+", "", input_str) # remove numbers
    input_str = re.sub(r"[^a-zA-Z0-9]+", ' ', input_str) #remove special characters
    input_str = input_str.strip() # remove whitespaces
    input_str = ' '.join(word for word in input_str.split() if word not in stop_words) # remove stopwords from text
#     result = [i for i in tokens if not i in stop_words] #remove stopwords
    return input_str
#     tokens = word_tokenize(input_str) #tokenize

#captures length of unpadded sequences to be used later
def parser(x, length, y):
    features = {"x": x, "len": length}
    return features, y

#Convert training data from numpy arrays to tensor slices, split it into batches
def train_input_fn():
    dataset = tf.data.Dataset.from_tensor_slices((x_train, x_len_train, y_train))
    dataset = dataset.shuffle(buffer_size=len(x_train))
    dataset = dataset.batch(100)
    dataset = dataset.map(parser)
    dataset = dataset.repeat()
    iterator = dataset.make_one_shot_iterator()
    return iterator.get_next()

# Convert test data from numpy array to tensor slices, split it into batches
def eval_input_fn():
    dataset = tf.data.Dataset.from_tensor_slices((x_test, x_len_test, y_test))
    dataset = dataset.batch(100)
    dataset = dataset.map(parser)
    iterator = dataset.make_one_shot_iterator()
    return iterator.get_next()

# function that (was supposed to) trains the classifier and additionally creates a precision-recall curve
def train_and_evaluate(classifier):
    classifier.train(input_fn=train_input_fn, steps=10000)
    eval_results = classifier.evaluate(input_fn=eval_input_fn)

    predictions = np.array([p['logistic'][0] for p in classifier.predict(input_fn=eval_input_fn)])
        
    # Reset the graph to be able to reuse name scopes
    tf.reset_default_graph() 
    # Add a PR summary in addition to the summaries that the classifier writes
    pr = summary_lib.pr_curve('precision_recall', predictions=predictions, labels=y_test.astype(bool), num_thresholds=21)
    with tf.Session() as sess:
        writer = tf.summary.FileWriter(os.path.join(classifier.model_dir, 'eval'), sess.graph)
        writer.add_summary(sess.run(pr), global_step=0)
        writer.close()

#This function builds the model        
def lstm_model_fn(features, labels, mode):    
    # [batch_size x sentence_size x embedding_size]
    inputs = tf.contrib.layers.embed_sequence(
        features['x'], vocab_size, embedding_size,
        initializer=tf.random_uniform_initializer(-1.0, 1.0))

    # create an LSTM cell of size 100
    lstm_cell = tf.nn.rnn_cell.BasicLSTMCell(100)
    
    # create the complete LSTM
    _, final_states = tf.nn.dynamic_rnn(
        lstm_cell, inputs, sequence_length=features['len'], dtype=tf.float32)

    # get the final hidden states of dimensionality [batch_size x sentence_size]
    outputs = final_states.h

    logits = tf.layers.dense(inputs=outputs, units=5)

    # This will be None when predicting
    if labels is not None:
        labels = tf.reshape(labels, [-1, 5])

    optimizer = tf.train.AdamOptimizer()
    def _train_op_fn(loss):
        return optimizer.minimize(
            loss=loss,
            global_step=tf.train.get_global_step())

    return head.create_estimator_spec(
        features=features,
        labels=labels,
        mode=mode,
        logits=logits,
        train_op_fn=_train_op_fn)


vocab_size = 5000 #limit size of vocabulary to avoid overfitting due to sparsity 
sentence_size = 20000 #arbitrary number, max text sequence length 32000(too large) 
embedding_size = 100 
model_dir = tempfile.mkdtemp()

#Initialize stopwords
nltk.download('stopwords')
nltk.download('punkt')
stop_words = set(stopwords.words('english'))

#Read and preprocess data
df = pd.read_csv("bbc-text.csv")
df['text'] = df['text'].apply(preprocessing)

#Tokenize and pad input sentences/sequences
tokenizer = Tokenizer(num_words=vocab_size, filters='!"#$%&()*+,-./:;<=>?@[\]^_`{|}~', lower=True)
tokenizer.fit_on_texts(df['text'].values)
word_index = tokenizer.word_index
print('Found %s unique tokens.' % len(word_index))
X = tokenizer.texts_to_sequences(df['text'].values)
X = pad_sequences(X, maxlen=sentence_size)
print('Shape of data tensor:', X.shape)

# One hot encode output labels
Y = pd.get_dummies(df['category']).values
print('Shape of label tensor:', Y.shape)

#test train split(70-30)
x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=88)

print(len(y_train), "train sequences")
print(len(y_test), "test sequences")

# print("Pad sequences (samples x time)")
# x_train = sequence.pad_sequences(x_train, 
#                                  maxlen=sentence_size, 
#                                  padding='post', 
#                                  value=0)
# x_test = sequence.pad_sequences(x_test, 
#                                 maxlen=sentence_size, 
#                                 padding='post', 
#                                 value=0)
# print("x_train shape:", x_train.shape)
# print("x_test shape:", x_test.shape)


x_len_train = np.array([min(len(x), sentence_size) for x in x_train])
x_len_test = np.array([min(len(x), sentence_size) for x in x_test])

#head computes predictions, loss, default metric and export signature.
head = tf.contrib.estimator.multi_class_head(n_classes=5)
lstm_classifier = tf.estimator.Estimator(model_fn=lstm_model_fn,
                                         model_dir=os.path.join(model_dir, 'lstm'))
train_and_evaluate(lstm_classifier)
