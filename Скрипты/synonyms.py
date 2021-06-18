import datetime
import os
import re
import traceback
from pprint import pprint
from sys import argv

import pymongo
from pymongo import MongoClient
from pyspark.ml.feature import CountVectorizer
from pyspark.ml.feature import IDF
from pyspark.ml.feature import StopWordsRemover
from pyspark.ml.feature import Tokenizer
from pyspark.ml.feature import Word2Vec
from pyspark.ml.feature import Word2VecModel
from pyspark.sql import SparkSession

path1, element = argv
#Путь к моделям
PATH = '/home/vagrant/tomita-parser/build/bin/packs_text_news/models'

spark = SparkSession \
    .builder \
    .appName("SimpleApplication") \
    .getOrCreate()

model = Word2VecModel.load(PATH)
name = element

#Получить синонимы
def get_synonyms(elements, count, model, spark):
    result = []
    for elem in elements:
        try:
            elementDF = spark.createDataFrame([
                (elem.lower().split(" "),)], ["words"])
            transform_elem = model.transform(elementDF)
            synonyms = model.findSynonyms(
                transform_elem.collect()[0][1], count).collect()
            result.append(synonyms)
        except:
            print('[Ошибка]')

    return result

#Записать результат в файл
f = open('/home/vagrant/tomita-parser/build/bin/syn.txt', 'w+')
f.seek(0)
for it in get_synonyms([name], 6, model, spark)[0]:
    a = it[0].replace(name, '')
    f.write(a + '\n')
f.close()

spark.stop()
