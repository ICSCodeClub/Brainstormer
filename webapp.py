import math
#from PIL import Image
from flask import Flask
from flask import jsonify
from flask import request

from waitress import serve

app = Flask(__name__)

import bing
from functools import lru_cache
@lru_cache(maxsize=24)
@app.route('/api/storm/<query>')
def brainstorm(query):
    if len(query.lstrip()) <= 1:
        return jsonify({'keywords': dict(),'summary': list(),})
    slugs, summary = bing.getSearchSummary(query)
    slugs = bing.processSlugs(slugs, query)
    maxVal = slugs[max(slugs, key=slugs.get)]
    print(maxVal)
    for k in slugs:
        slugs[k] = int(round(100*math.pow(slugs[k]/maxVal,0.2)))
    
    return jsonify({
        'keywords': slugs,
        'summary': summary,
    })

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5565)
 
