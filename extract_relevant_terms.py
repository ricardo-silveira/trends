from __future__ import print_function, division
from pyspark import SparkContext
from pyspark.sql import SparkSession, Row
import json
import numpy as np
import re
import sys


def tf_idf(N, tf, df):
    result = []
    for key, value in tf.items():
        doc = key[0]
        term = key[1]
        df = document_frequency[term]
        if (df>0):
            tf_idf = float(value)*np.log(number_of_docs/df)
        result.append({"doc":doc, "term":term, "score":tf_idf})
    return result


def tokenize(s):
    return re.split("\\W+", s.lower())


def search(query, topN):
    """
    Given a query phrase (Q) find the most similar Document using tf-idf scores
    These scores are ranked and used to retrieve the most similar documents
    from the corpus
    We Define A search function
    1) Search(Query, TopN): TopN_Documents
    2) Tokenize(Query)
    3) Perform a broadcast to efficiently filter out 'interesting' documents.
    4) Use aggregateByKey to compute the Similarity score.
    5) Return the topN documents.
    A function that provides results in realtime
    """
    tfidf_RDD = sc.parallelize(tf_idf_output).map(lambda x: (x['term'],
                                                             (x['doc'],
                                                              x['score'])))
    tokens = sc.parallelize(tokenize(query)).map(lambda x: (x,1) ).collectAsMap()
    bcTokens = sc.broadcast(tokens)
    joined_tfidf = tfidf_RDD.map(lambda (k,v): (k,bcTokens.value.get(k,'-'),v)).\
        filter(lambda (a,b,c): b != '-' )
    scount = joined_tfidf.map(lambda a: a[2]).\
        aggregateByKey((0,0),(lambda acc, value: (acc[0] +value,acc[1]+1)),
                       (lambda acc1,acc2: (acc1[0]+acc2[0],acc1[1]+acc2[1])) )
    scores = scount.map(lambda (k,v): ( v[0]*v[1]/len(tokens), k) ).top(topN)
    return scores

if __name__ == "__main__":
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    sc = SparkContext(appName="TFIDF")  # SparkContext
    spark = SparkSession(sc)
    tech_text = sc.wholeTextFiles(input_path, 8).\
        map(lambda (a,b): Row(title = a.replace("dbfs:%s" % input_path, ""),\
                              text=b)).toDF(["doc","text"])
    number_of_docs = tech_text.count()
    tokenized_text = tech_text.rdd.map(lambda (text,title): (title,\
                                                             tokenize(text)) )
    term_frequency = tokenized_text.flatMapValues(lambda x: x).countByValue()
    document_frequency = tokenized_text.flatMapValues(lambda x: x).distinct()\
        .filter(lambda x: x[1] != '')\
        .map(lambda (title,word): (word,title)).countByKey()
    tf_idf_output = tf_idf(number_of_docs, term_frequency, document_frequency)
    # storing results in temporary file
    with open(output_path, "wb") as out:
        json.dump(tf_idf_output, out)
    sc.stop()
