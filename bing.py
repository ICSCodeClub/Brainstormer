def getKey():
    with open("key.txt") as file: # Use file to refer to the file object
        data = file.read()
        return data
    return ''

def cleanhtml(raw_html):
    import re
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


subscription_key = getKey()
assert subscription_key

search_url = "https://api.cognitive.microsoft.com/bing/v7.0/search"
search_term = "drag the labels onto the flowchart to show the sequence of events that occurs once the membrane potential reaches threshold. you may use a label once or not at all."

import requests

headers = {"Ocp-Apim-Subscription-Key": subscription_key}
params = {"q": search_term, "textDecorations": True, "textFormat": "HTML", "answerCount": 1000, "responseFilter": "Webpages",}
response = requests.get(search_url, headers=headers, params=params)
response.raise_for_status()
search_results = response.json()

for responses in search_results['webPages']['value']:
    print(cleanhtml(str(responses['snippet']))[len(search_term):])


