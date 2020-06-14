# -*- coding: utf-8 -*-

import nltk
nltk.download('vader_lexicon',quiet=True)
from nltk.sentiment.vader import SentimentIntensityAnalyzer


def getSelection(sorted_dict, number=-1):
        if number <= 0:
                number = round(0.5+len(sorted_dict)*0.15)
        sel = []
        for x in list(sorted_dict)[-number:]:
            sel.append(x)
        return sel

def isPeriodSentenceEnd(perLoc, string):
        if string[perLoc] != '.':
                return False
        if perLoc > 0 and string[perLoc-1].isupper():
                return False
        if perLoc >= len(string) - 1:
                return True
        if string[perLoc + 1].isnumeric():
                return False
        return True
def getQuotationMarks(char):
        if len(char) <= 1:
                marks = '«‹»›„“‟”’’❝❞❮❯⹂〝〞〟＂‚‘‛❛❜❟"'
                if char in marks and len(char) > 0:
                        return 1
                return 0
        else:
                return getQuotationMarks(char[0]) + getQuotationMarks(char[1:])
def getNextEndingLocation(string):
        i = 0
        while i < len(string)-1:
                i += 1
                if isPeriodSentenceEnd(i, string):
                        if i < len(string)-1 and getQuotationMarks(string[i+1]) > 0:
                                return i+2
                        elif i < len(string)-2:
                                return i+1
        return len(string)
def sentenceSplit(string):
        ss = []
        '''
        curS = ''
        for i in range(len(string)):
                if string[i] == '.' and isPeriodSentenceEnd(i, string):
                        ss.append((str(curS) + '.').lstrip())
                        curS = ''
                else:
                        curS = str(curS) + string[i]
        if len(curS) > 0:
                ss.append((str(curS) + '.').lstrip())
        '''
        while len(string.lstrip()) > 0:
                end = getNextEndingLocation(string)
                ss.append(string[:end].replace('\n',' ').strip())
                string = string[end:].lstrip()
        return ss
def getQuotes(string):
        sentences = sentenceSplit(string)
        quotes = []
        for s in sentences:
                if getQuotationMarks(s) >= 2:
                        quotes.append(s)
        return quotes
def getQuotesDict(string):
        sentences = sentenceSplit(string)
        if len(sentences) <= 1:
                return None

        quotes = dict()
        prevSentence = sentences[0]
        for i in range(1,len(sentences)):
                if getQuotationMarks(sentences[i]) >= 2:
                        if prevSentence in quotes:
                                quotes[prevSentence].append(sentences[i])
                        else:
                                quotes[prevSentence] = [sentences[i]]
                else:
                        prevSentence = sentences[i]
        return quotes
def getQuotesDictFromSelectSentences(string, topic_sentences):
        sentences = sentenceSplit(string)
        if len(sentences) <= 1:
                return None

        quotes = dict()
        prevSentence = topic_sentences[0]
        for i in range(1,len(sentences)):
                if getQuotationMarks(sentences[i]) >= 2:
                        if prevSentence in quotes:
                                quotes[prevSentence].append(sentences[i])
                        else:
                                quotes[prevSentence] = [sentences[i]]
                elif sentences[i] in topic_sentences:
                        prevSentence = sentences[i]
        return quotes
def getEmotionalDict(string):
        emotions = dict()
        for word in sentenceSplit(string):
            emotions[word] = abs(sid.polarity_scores(word)['compound'])
        return emotions

def getEmotionalSelection(string, number=-1):
        unsort = getSelection(sorted(getEmotionalDict(string)), number=number) # Returns it in the wrong order
        sort = [] # Therefore, we sort
        for s in sentenceSplit(string):
                if s in unsort:
                        sort.append(s)
        return sort
def getEmotionalSelectionFromList(sentences, number=-1):
        unsort = getSelection(sorted(getEmotionalDict('. '.join(sentences))), number=number) # Returns it in the wrong order
        sort = [] # Therefore, we sort
        for s in sentences:
                if s in unsort:
                        sort.append(s)
        return sort

sid = SentimentIntensityAnalyzer()

if __name__ == "__main__":
        string = ""
        with open('input.txt', 'r') as file:
                string = file.read()
        
        print(getEmotionalSelection(string))
        print('')
        print(getQuotesDictFromSelectSentences(string, getEmotionalSelection(string)))
        
