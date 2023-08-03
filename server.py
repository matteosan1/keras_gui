import logging, os, json, pandas as pd

from os.path import join

from flask import Flask, request, render_template, url_for, flash
from flask import redirect, jsonify, Response, stream_with_context
from werkzeug.utils import secure_filename

from model_api import ModelAPI
from message_announcer import MessageAnnouncer, format_sse

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()
app.config['UPLOAD_FOLDER'] = "/tmp/"
app.config['UPLOAD_EXTENSIONS'] = ['.css', '.csv']
app.config['MAX_CONTENT_LENGTH'] = 1024*1024

m = ModelAPI()
announcer = MessageAnnouncer()

@app.route('/update_training_status')
def update_training_status():
  if request.args.get("status") == "END":
      msg = format_sse(data="", event="end")
  else:
    if request.args.get('loss') is not None:
      json_data = json.dumps({'loss':request.args.get('loss'),
                              'epoch':request.args.get('epoch')})
    else:
      json_data = "inf" #json.dumps({'loss':"inf"})
    msg = format_sse(data=json_data, event="loss")
  announcer.announce(msg=msg)
  return {}, 200

@app.route('/listen', methods=['GET'])
def listen():
  print ("CAZZO")
  def stream():
    messages = announcer.listen() 
    while True:
      msg = messages.get()
      yield msg
  return Response(stream(), mimetype='text/event-stream')
  
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

@app.route('/create', methods=('GET', 'POST'))
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
  m.filename = output_filename
  return cols

@app.route('/start_training', methods=['GET'])
def start_training():
  m.fit()
  return "OK", 200

@app.route('/train_model/', methods=['GET'])
def train_model():
  return render_template("training.html")

@app.route('/create_model/', methods=['POST'])
def create_model():
  data = request.form.to_dict(flat=False)
  vars = [k for k in data.keys() if k.endswith("_x") or k.endswith("_y")]
  
  inputs = set([data[i][0] for i in data.keys() if i.endswith("_x")])
  outputs = set([data[i][0] for i in data.keys() if i.endswith("_y")])
  common = list(inputs.intersection(outputs))

  msg = 'OK'
  typ = ''
  
  if len(inputs) < 2:
    msg = f"Need to select at least 2 input parameters."
    typ = 'variableError'
  elif 'nnname' not in data:
    data['nnname'] = 'test'
  elif len(outputs) == 0:
    msg = f"This tool works only for supervised training, please select at least 1 output."
    typ = 'variableError'
  elif len(common) > 0:
    msg = f"Parameter(s): {common} both in input and output."
    typ = 'variableError'
  elif len(outputs) != int(data['neurons'][-1]):
    msg = f"Number outputs doesn't match output-layer neurons."
    typ = 'variableError'
  elif 'type' not in data or 'neurons' not in data or 'activation' not in data:
    msg = f"No layer has been defined."
    typ = 'layerError'
  elif not (len(data['type']) == len(data['neurons']) == len(data['activation'])):
    msg = f"Incorrect layer definition."
    typ = 'layerError'
  elif 'optimizer' not in data:
    msg = f"Optimizer not set."
    typ = 'optimizerError'
  elif 'loss' not in data:
    msg = f"Loss function not set."
    typ = 'lossError'

  if msg == "OK":
    m.create_model(data, inputs, outputs)

  return jsonify({'msg':msg, 'type':typ}), 200

if __name__ == "__main__":
    print (("* Loading Keras model and Flask starting server..."
            "please wait until server  has fully started"))
    app.run(debug=True, threaded=True)

