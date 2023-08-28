def getKey():
    with open("key.txt") as file: # Use file to refer to the file object
        data = file.read()
        return data.replace('\n','').replace(' ','')
    return ''

# From https://stackoverflow.com/questions/9662346/python-code-to-remove-html-tags-from-a-string
def cleanhtml(raw_html):
    import re
    cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});') 
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


subscription_key = getKey()
assert subscription_key
print(subscription_key)

search_url = "https://api.bing.microsoft.com/v7.0/search"

import requests
import libraries.splitter as splitter
def getSearchSummary(query):
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    params = {"q": query, "textDecorations": True, "textFormat": "HTML", "answerCount": 1000, "responseFilter": "Webpages",}
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()
    try:
        slugs = []
        emotionDict = dict()
        originDict = dict() #stores keyword, url
        for responses in search_results['webPages']['value']:
            slug = cleanhtml(str(responses['snippet'])).lower().replace(query.lower().strip()+' ','').strip()
            slugs.append([slug, responses['url']])

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


from libraries.phrase import get_phrases, get_similar
def processSlugs(slugs, query):
    phraseFreqs = dict()
    raw_slugs = [s[0] for s in slugs] # Ignore source for now
    for slug in raw_slugs:
        slug = cleanStr(slug)
        getPhraseFreqs(get_phrases(slug), phraseFreq=phraseFreqs)
    getPhraseFreqs(get_similar(query), phraseFreq=phraseFreqs, multiplier=1.3)
    
    # Add source to dictionary
    for k in phraseFreqs:
        # if key is in slug sources, add source
        for i in range(len(raw_slugs)):
            if k in raw_slugs[i]:
                phraseFreqs[k] = [phraseFreqs[k], slugs[i][1]]
                break
    return phraseFreqs

import json
if __name__ == "__main__":
    term = input('What term should be serached for? ')
    slugs, summary = getSearchSummary(term)
    print(slugs)
    phraseFreqs = processSlugs(slugs, term)
    print('\nKeywords:\n'+str(phraseFreqs))
    print('\nSummary:\n'+str(summary))
        
