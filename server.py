import pickle, numpy as np

from os import urandom
from os.path import join
from flask import Flask, request, render_template, url_for, flash, redirect
from werkzeug.utils import secure_filename
#from keras.models import load_model

app = Flask(__name__)
app.config['SECRET_KEY'] = urandom(24).hex()
app.config['UPLOAD_FOLDER'] = "/tmp/"
app.config['UPLOAD_EXTENSIONS'] = ['.css']
app.config['MAX_CONTENT_LENGTH'] = 1024*1024

messages = [{'title': 'Message One',
             'content': 'Message One Content'},
            {'title': 'Message Two',
             'content': 'Message Two Content'}
            ]

class ModelAPI:
    def __init__(self):
        self.x_names = []
        self.y_names = []
        self.scaler_x = None
        self.scaler_y = None
        self.name = "test"
        
    def save(self):
        data = {"x_names":self.x_names, "y_names":self.y_names,
                "x_scaler":self.scaler_x, "y_scaler":self.scaler_y}
        pickle.dump(data, open(f"{self.name}_data.pkl", "wb"))
        return "Data saved"
        #self.model.save(self.name)
        
    def load(self):
        data = pickle.load(open(f"{self.name}_data.pkl", "rb"))
        self.x_names = data["x_names"]
        self.y_names = data["y_names"]
        self.scaler_x = data["x_scaler"]
        self.scaler_y = data["y_scaler"]
        #model = load_model(self.name)
        return "Data loaded"

m = ModelAPI()

@app.route("/", methods=['GET'])
def index():
    return render_template("index.html", messages=messages)

@app.route("/load", methods=['GET'])
def load_data():
    global m
    name = request.args.get('filename') #, default = 1, type = int)
    m.name = name
    m.load()
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

if __name__ == "__main__":
    print (("* Loading Keras model and Flask starting server..."
            "please wait until server  has fully started"))
    app.run()

