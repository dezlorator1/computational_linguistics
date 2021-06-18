import csv
import io
import random
import re
import string

from nltk import FreqDist, NaiveBayesClassifier
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from pymongo import MongoClient


def remove_noise(tweet_tokens,stop_words=()):
  cleaned_tokens=[]
  for token, tag in pos_tag(tweet_tokens):
    token=re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
'(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
    token=re.sub("(@[A-Za-z0-9_]+)","", token)
    if tag.startswith("NN"):
      pos='n'
    elif tag.startswith('VB'):
      pos='v'
    else:
      pos='a'
    lemmatizer=WordNetLemmatizer()
    token=lemmatizer.lemmatize(token,pos)
    if len(token)>0 and token not in string.punctuation and token.lower() not in stop_words:
      cleaned_tokens.append(token.lower())
  return cleaned_tokens

def get_all_words(cleaned_tokens_list):
  for tokens in cleaned_tokens_list:
    for token in tokens:
      yield token

def get_tweets_for_model(cleaned_tokens_list):
  for tweet_tokens in cleaned_tokens_list:
    yield dict([token, True] for token in tweet_tokens)

if __name__ == "__main__":

  client = MongoClient('localhost',27017)
  db = client['bloknot']
  collection_sentence = db['sentence']
  collection_tonality_sentence = db['tonality']
  
  collection_tonality_sentence.delete_many({})

  
  positive_tweet_tokens =[]
  negative_tweet_tokens =[]
  
  stop_words = stopwords.words('russian')
    
  with open('/home/vagrant/tomita-parser/build/bin/data/positive.csv',encoding='utf-8', newline='') as csvfile:
    data = csvfile.read()
  data = data.replace("\0", "")      
  csvfile_repl = io.StringIO(data)   
  
  reader = csv.DictReader(csvfile_repl,delimiter=';') 
  for row in reader:
    tweet = row['t_4']
    tokens = word_tokenize(tweet)
    positive_tweet_tokens.append(tokens)
      
  with open('/home/vagrant/tomita-parser/build/bin/data/negative.csv',encoding='utf-8', newline='') as csvfile:
    data = csvfile.read()
  data = data.replace("\0", "")      
  csvfile_repl = io.StringIO(data)
  reader = csv.DictReader(csvfile_repl,delimiter=';')
    
  for row in reader:
    tweet = row['t_4']
    tokens = word_tokenize(tweet)
    negative_tweet_tokens.append(tokens)

  positive_cleaned_tokens_list = []
  negative_cleaned_tokens_list = []

  for tokens in positive_tweet_tokens:
    positive_cleaned_tokens_list.append(remove_noise(tokens, stop_words))

  for tokens in negative_tweet_tokens:
    negative_cleaned_tokens_list.append(remove_noise(tokens, stop_words))

  all_pos_words = get_all_words(positive_cleaned_tokens_list)

  freq_dist_pos = FreqDist(all_pos_words)
  print(freq_dist_pos.most_common(10))

  positive_tokens_for_model = get_tweets_for_model(positive_cleaned_tokens_list)
  negative_tokens_for_model = get_tweets_for_model(negative_cleaned_tokens_list)

  positive_dataset = [(tweet_dict, "Positive")
                         for tweet_dict in positive_tokens_for_model]

  negative_dataset = [(tweet_dict, "Negative")
                         for tweet_dict in negative_tokens_for_model]

  dataset = positive_dataset + negative_dataset

  random.shuffle(dataset)

  train_data = dataset[:156692]
  test_data = dataset[156692:]

  classifier = NaiveBayesClassifier.train(train_data)
  messages =[]
  cursor_sentence = collection_sentence.find({})
  for document in cursor_sentence:
    messages.append(document["sentence"])
  for sentence in messages:
    custom_tweet = sentence
    custom_tokens = remove_noise(word_tokenize(custom_tweet))
    custom_tweet_tonality = classifier.classify(dict([token, True] for token in custom_tokens))
    print(custom_tweet)
    print(custom_tweet_tonality)
    data = {'sentence':custom_tweet,
          'tonality':custom_tweet_tonality}
    collection_tonality_sentence.insert_one(data).inserted_id