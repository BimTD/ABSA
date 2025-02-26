from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import copy

app = Flask(__name__)
CORS(app)

data = {}
num_cmt = 0

@app.route('/predict', methods=['GET'])
def predict():
    pred = list(data.values())
    pred.sort(key=lambda x: x['num'], reverse=True)
    return jsonify(pred)

@app.route('/', methods=['GET', 'POST'])
def home():
    global data, num_cmt
    
    if request.method == 'POST':
        req = request.json
        print("Received request:", req)

        cmtid = req.get('cmtid', 'unknown_id')
        rating_star = req.get('rating_star', 3)
        comment = req.get('comment', 'No comment')
        sentiment = req.get('sentiment', 'neutral')
        begin = req.get('begin', 0)
        end = req.get('end', 0)
        label = req.get('label', 'review')
        
        if cmtid not in data:
            data[cmtid] = {
                "rating_star": rating_star,
                "comment": comment,
                "labels": [],
                'sentiment': sentiment,
                'num': copy.deepcopy(num_cmt)
            }
            num_cmt += 1
        
        data[cmtid]['labels'].append([
            begin,
            end,
            label
        ])
    
    return render_template('index.html', data=data)

@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
