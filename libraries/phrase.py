# From https://gist.github.com/karimkhanp/4b7626a933759d0113d54b09acef24bf
# This helps too https://stackoverflow.com/questions/15388831/what-are-all-possible-pos-tags-of-nltk

import nltk

nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

from nltk.corpus import stopwords


sentence_re = r"""
            (?x)                   # set flag to allow verbose regexps
            (?:[A-Z]\.)+           # abbreviations, e.g. U.S.A.
            |\d+(?:\.\d+)?%?       # numbers, incl. currency and percentages
            |\w+(?:[-']\w+)*       # words w/ optional internal hyphens/apostrophe
            |(?:[+/\-@&*])         # special characters with meanings
            |\.
            """ #Fromhttps://stackoverflow.com/questions/35118596/python-regular-expression-not-working-properly
#Old regex r'(?:(?:[A-Z])(?:.[A-Z])+.?)|(?:\w+(?:-\w+)*)|(?:\$?\d+(?:.\d+)?%?)|(?:...|)(?:[][.,;"\'?():-_`])'
lemmatizer = nltk.WordNetLemmatizer()
stemmer = nltk.stem.porter.PorterStemmer()
grammar = r"""
    NNUMB:
        {(\$.*)? <CD>}
    NBAR:
        {<NN.* | JJ.* | NNUMB>*<NN.*>}  # Nouns and Adjectives and numbers, terminated with Nouns
        
    NP:
        {<NBAR><IN><NBAR>}  # Above, connected with in/of/etc...
        {<NBAR>}
"""
chunker = nltk.RegexpParser(grammar)
stopwords = stopwords.words('english')

def leaves(tree):
    for subtree in tree.subtrees(filter = lambda t: t.label()=='NP'):
        yield subtree.leaves()

def normalise(word):
    word = word.lower()
    word = lemmatizer.lemmatize(word)
    return word

def get_terms(tree):
    for leaf in leaves(tree):
        #term = [ normalise(w) for w,t in leaf ] Uncomment to revert words to their stem
        term = [ w for w,t in leaf ]
        yield term

def addWordNet(wn, words=[]):
    for net in wn:
        for l in net.lemmas():
            word = l.name().replace('_',' ')
            if not (word in words):
                words.append(word)
    return words

# The method to call to get a list of all noun phrases
def get_phrases(text):
    toks = nltk.regexp_tokenize(text, sentence_re)
    postoks = nltk.tag.pos_tag(toks)
    tree = chunker.parse(postoks)
    terms = get_terms(tree)
    phrases = [" ".join(term) for term in terms]
    return phrases

def get_similar(nounPhrase):
    similar = []
    
    net = nltk.corpus.wordnet.synsets(nounPhrase.replace(' ','_'))
    for syn in net:
        addWordNet(syn.substance_holonyms(), similar)
        addWordNet(syn.part_holonyms(), similar)
        addWordNet(syn.part_meronyms(), similar)
        addWordNet(syn.substance_meronyms(), similar)
        addWordNet(syn.entailments(), similar)
            
    #don't trust caller: get noun phrases and rerun
    for np in get_phrases(nounPhrase):
        net = nltk.corpus.wordnet.synsets(np.replace(' ','_'))
        for syn in net:
            # Holonym - denotes a membership to something
            # Part holonym: atom -> chemical element
            # Substance holonym: hydrogen -> water
            addWordNet(syn.substance_holonyms(), similar)
            addWordNet(syn.part_holonyms(), similar)
            # Meronym - components of the hole
            # Part meronym: Tree - crown
            # Substance meronym: Tree - heartwood
            addWordNet(syn.part_meronyms(), similar)
            addWordNet(syn.substance_meronyms(), similar)
            # Entailments - what words entail
            # Eating entails chewing
            addWordNet(syn.entailments(), similar)
    return similar

if __name__ == "__main__":
        string = 'the quick brown fox jumped over the lazy dog. sphinx of black quartz hear my vow. 10 cats and 20 dogs fell from the bright blue sky. We are operating at 99.8 percent capacity. Daily, 50% of U.S. Population recieves $50.23.'
        print(get_phrases(string))
        print(get_similar('tree'))
