import math
#from PIL import Image
from flask import Flask
from flask import jsonify
from flask import request

from waitress import serve

app = Flask(__name__)

import bing
from functools import lru_cache
@lru_cache(maxsize=36)
@app.route('/api/storm/<query>')
def brainstorm(query):
    if len(query.lstrip()) <= 1:
        return jsonify({'keywords': dict(),'summary': list(),})
    
    slugs, summary = bing.getSearchSummary(query)
    slugs = bing.processSlugs(slugs, query)
    for k in slugs:
        if not isinstance(slugs[k], list):
            slugs[k] = [slugs[k]]
        if 'http' in str(k) or 'videos' in str(k):
            slugs.pop(k)
    
    maxVal = slugs[max(slugs, key=lambda k: slugs[k][0])]
    if isinstance(maxVal, list):
        maxVal = maxVal[0]
    
    for k in slugs:
        slugs[k][0] = int(round(100*math.pow(slugs[k][0]/maxVal,0.2)))
    
    return jsonify({
        'keywords': slugs,
        'summary': summary,
    })

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5565)
 
