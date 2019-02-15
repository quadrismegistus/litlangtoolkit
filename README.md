# llp

Literary Language Processing (LLP): Corpora, models, and tools for the digital humanities. Written in Python.

## Make a corpus in two lines

If you have a folder of plain text files, a 

```python
from llp.corpus.default import PlainTextCorpus

corpus = PlainTextCorpus(
	path_txt='texts',              # path to a folder of txt files
	path_metadata='metadata.xls',  # path to a metadata CSV, TSV, XLS, XLSX file
	col_fn='filename'              # column in meadatta pointing to txt file (relative to `path_txt`)
)
```

## Corpora

Now that you have a corpus object,

```python

# Get the texts as a list
texts = corpus.texts()

# Get the metadata as a list of dictionaries
metadata = corpus.meta

# Save a list of the most frequent words
corpus.gen_mfw()

# Save a term-document matrix for the top 10000 most frequent words
corpus.gen_freq_table(n=10000)

# Generate a word2vec model with gensim
w2v_model = corpus.word2vec()
w2v_model.model()

# Save a list of possible duplicate texts in corpus, by title similarity
corpus.rank_duplicates_bytitle()

# Save a list of possible duplicate texts in corpus, by the content of the text (MinHash)
corpus.rank_duplicates()
```

## Texts

With any text object,

```python
# For every text in the corpus...
for text in corpus.texts():

	# Get the full text as a string
	text_as_string = text.txt
	
	# Get its metadata as a dictionary
	text_metadata_dicionary = text.meta
	
	# Get its word tokens as a list
	tokens = text.tokens
	
	# Get its word counts as a dictionary
	counts = text.freqs()
	
	# Get its n-gram counts as a dictionary
	bigrams = text.freqs_ngram(n=2)
	
	# Get a list of passages mentioning a phrase (Key Word In Context)
	passages = text.get_passages(phrases=['labour'])
	
	# Get its spacy (spacy.io) representation
	text_as_spacy_object = text.spacy()
```

