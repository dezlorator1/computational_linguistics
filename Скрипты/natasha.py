import pymongo
from pymongo import MongoClient
from sys import argv
from itertools import groupby
from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,    
    PER,
    NamesExtractor,
    Doc
)


segmenter = Segmenter()
morph_vocab = MorphVocab()

emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
syntax_parser = NewsSyntaxParser(emb)
ner_tagger = NewsNERTagger(emb)

names_extractor = NamesExtractor(morph_vocab)

path1, element = argv

client = MongoClient('localhost',27017)
db = client['bloknot']
collection_objects = db['person']
  
text=[] 
f = open('/home/vagrant/tomita-parser/build/bin/change_sentences.txt', 'r')
for line in f:
  a={"num_object" : element}
  n = collection_objects.find_one(a)
  a = n["name_object"]
  text.append(line.replace('\n','').replace(element, a))
text1=[] 
for sen in text:
  doc = Doc(sen)
  doc.segment(segmenter)
  doc.tag_morph(morph_tagger)
  for token in doc.tokens:
    token.lemmatize(morph_vocab)
  doc.parse_syntax(syntax_parser)
  for token in doc.tokens:
    if(token.text== a):
      n = token.head_id
      for token in doc.tokens:
        if(token.id== n):
          text1.append(token.text)

new_x = [el for el, _ in groupby(text1)]
woduplicates = set(text1)
f = open('/home/vagrant/tomita-parser/build/bin/syn1.txt', 'w+')
f.seek(0)
for it in woduplicates:
  f.write(it +'\n')
f.close()  


  
  
  
