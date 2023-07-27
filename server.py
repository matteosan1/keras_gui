import pickle, numpy as np, pandas as pd

#from keras.models import Sequential
#from keras.layers import Dense

from os import urandom
from os.path import join

from flask import Flask, request, render_template, url_for, flash, redirect, jsonify
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config['SECRET_KEY'] = urandom(24).hex()
app.config['UPLOAD_FOLDER'] = "/tmp/"
app.config['UPLOAD_EXTENSIONS'] = ['.css', '.csv']
app.config['MAX_CONTENT_LENGTH'] = 1024*1024

messages = [{'title': 'Message One',
             'content': 'Message One Content'},
            {'title': 'Message Two',
             'content': 'Message Two Content'}
            ]
import threading
import time
#from tqdm import tqdm

# replace with train model - suppose it takes 3 seconds to train
def _trainModel():
  time.sleep(3)
  return
# replace with load data function - suppose it takes 2 seconds to load
def _loadData():
  time.sleep(2)
  return

# assume we loop 10 times
epochs = 10

#class TrainModel (threading.Thread):
#    def __init__(self, data):
#        threading.Thread.__init__(self)
#        self.data = data
#    def run(self):
#        # return model loss
#        self._return = _trainModel()    
#    def join(self):
#        threading.Thread.join(self)
#        return self._return
#    
#class LoadData (threading.Thread):
#    def __init__(self, filenames):
#        threading.Thread.__init__(self)
#        self.filenames = filenames
#    def run(self):        
#        # return data
#        self._return = _loadData()
#    def join(self):
#        threading.Thread.join(self)
#        return self._return

# with multithreading
# use with for tqdm to properly shut tqdm down if exception appears
#with tqdm(range(epochs)) as epochLoop:
#  for _ in epochLoop:
#    # loadData
#    loadThread = LoadData(None)
#    loadThread.start()
#    
#    # trainModel
#    trainThread = TrainModel(None)
#    trainThread.start()
#    
#    # only continue if both threads are done
#    modelLoss = trainThread.join()
#    data = loadThread.join()
#
#class ModelAPI:
#    def __init__(self):
#        self.x_names = []
#        self.y_names = []
#        self.scaler_x = None
#        self.scaler_y = None
#        self.name = "test"
#        
#    def save(self):
#        data = {"x_names":self.x_names, "y_names":self.y_names,
#                "x_scaler":self.scaler_x, "y_scaler":self.scaler_y}
#        pickle.dump(data, open(f"{self.name}_data.pkl", "wb"))
#        return "Data saved"
#        #self.model.save(self.name)
#        
#    def load(self):
#        data = pickle.load(open(f"{self.name}_data.pkl", "rb"))
#        self.x_names = data["x_names"]
#        self.y_names = data["y_names"]
#        self.scaler_x = data["x_scaler"]
#        self.scaler_y = data["y_scaler"]
#        #model = load_model(self.name)
#        return "Data loaded"
#
#    def predict(self):
#        x0 = 1
#        x_transf = scale_X.transform([[x0]])
#        print (scale_y.inverse_transform(model.predict(x_transf)))
#
#    def check_overfit(self):
#        eval_train = model.evaluate(X_train, y_train)
#        print('Training: {}'.format(eval_train))
#        eval_test = model.evaluate(X_test, y_test)
#        print('Test: {}'.format(eval_test))
#
#    def create_model(self):
#        x = X_train[:, 0]
#        y = X_train[:, 1]
#        model = Sequential()
#        model.add(Dense(15, input_dim=1, activation='sigmoid'))
#        model.add(Dense(5, activation='sigmoid'))
#        model.add(Dense(1, activation='sigmoid'))
#
#    def fit(self):
#        model.compile(loss='mse', optimizer='adam')
#        model.fit(x, y, epochs=5000, verbose=1)
#        
#m = ModelAPI()

@app.route("/", methods=['GET'])
def index():
    return render_template("index.html")#, messages=messages)

@app.route("/load", methods=['GET'])
def load_data():
    #global m
    name = request.args.get('filename') #, default = 1, type = int)
    #m.name = name
    #m.load()
    return "Ciao Mondo\n"

@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if request.files['model'].filename == "":
            flash('You need to select a model')
        elif request.files['datafile'].filename == "":
            flash('Need some data to predict !')
        else:
            f = request.files['datafile']
            f.save(join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            messages.append({'title':"pIPPO", 'content':content})
            return redirect(url_for('index'))
    
    return render_template('create.html')

@app.route('/loaddata', methods=['POST'])
def testfn():
  f = request.files['file']
  output_filename = join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename))
  f.save(output_filename)
  df = pd.read_csv(output_filename)
  cols = [c for c in df.columns if "Unnamed" not in c]
  return cols
  
@app.route('/create_model', methods=('POST',))
def create_model():
  data = request.form.to_dict(flat=False)
  inputs = set([data[i][0] for i in data.keys() if i.endswith("_x")])
  outputs = set([data[i][0] for i in data.keys() if i.endswith("_y")])
  if len(inputs) < 2:
    msg = f"Need to select at least 2 input parameters."
    return jsonify({'msg':msg}), 400
  
  if len(outputs) == 0:
    msg = f"This tool works only for supervised training, please select at least 1 output."
    return jsonify({'msg':msg}), 400
  
  common = list(inputs.intersection(outputs))
  if len(common) > 0:
    msg = f"Parameter(s): {common} both in input and output."
    return jsonify({'msg':msg}), 400
  
  if len(outputs) != int(data['neurons'][-1]):
    msg = f"Number outputs doesn't match output-layer neurons."
    return jsonify({'msg':msg}), 400
  
  return  jsonify({'msg':"OK"}), 200

  #return render_template('create_model.html')

if __name__ == "__main__":
    print (("* Loading Keras model and Flask starting server..."
            "please wait until server  has fully started"))
    app.run()

