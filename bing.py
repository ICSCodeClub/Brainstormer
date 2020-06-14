def getKey():
    with open("key.txt") as file: # Use file to refer to the file object
        data = file.read()
        return data
    return ''

# From https://stackoverflow.com/questions/9662346/python-code-to-remove-html-tags-from-a-string
def cleanhtml(raw_html):
    import re
    cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});') 
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


subscription_key = getKey()
assert subscription_key

search_url = "https://api.cognitive.microsoft.com/bing/v7.0/search"

import requests
import splitter
def getSearchSummary(query):
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    params = {"q": query, "textDecorations": True, "textFormat": "HTML", "answerCount": 1000, "responseFilter": "Webpages",}
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()
    try:
        slugs = []
        emotionDict = dict()
        for responses in search_results['webPages']['value']:
            slugs.append(cleanhtml(str(responses['snippet'])).lower().replace(query.lower(),'').lstrip())

            slugDict = splitter.getEmotionalDict(cleanhtml(str(responses['snippet'])))
            for k in slugDict:
                if k in emotionDict:
                    emotionDict[k] += slugDict[k]
                else:
                    emotionDict[k] = slugDict[k]
            
        return slugs, splitter.getSelection(sorted(emotionDict))
    except:
        return list(),dict()


import string
valid_characters = string.ascii_letters + string.digits + ' '
def cleanStr(str):
    return ''.join(ch for ch in str if ch in valid_characters)

def scoreStr(str):
    score = len(str)
    for ch in str:
        if ch in string.digits:
            score += 1
    return score
        

def getPhraseFreqs(phrases,phraseFreq=dict(), multiplier=1):
    if len(phrases) <= 0:
        return dict()
    maxLen = len(max(phrases, key=scoreStr))
    for phrase in phrases:
        if phrase in phraseFreq:
            phraseFreq[phrase] += multiplier * max(1-(scoreStr(phrase)/maxLen),0.01)
        else:
            phraseFreq[phrase] = multiplier * max(1-(scoreStr(phrase)/maxLen),0.01)
    return phraseFreq

def getRawPhraseFreqs(phrases,phraseFreq=dict(), value=1):
    for phrase in phrases:
        if phrase in phraseFreq:
            phraseFreq[phrase] += value
        else:
            phraseFreq[phrase] = value
    return phraseFreq


from phrase import get_phrases, get_similar
def processSlugs(slugs, query):
    phraseFreqs = dict()
    for slug in slugs:
        slug = cleanStr(slug)
        getPhraseFreqs(get_phrases(slug), phraseFreq=phraseFreqs)
    getPhraseFreqs(get_similar(query), phraseFreq=phraseFreqs, multiplier=1.3)
    return phraseFreqs

import json
if __name__ == "__main__":
    term = 'mass of the sun'
    slugs, summary = getSearchSummary(term)
    phraseFreqs = processSlugs(slugs, term)
    print(phraseFreqs)
    freqsSorted = sorted(phraseFreqs.items(), key=lambda x: x[1], reverse=True)
    print(json.dumps(dict(freqsSorted), sort_keys=False))
    print(summary)
        
