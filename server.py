import logging, os, json, pandas as pd

from os.path import join, isfile

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

@app.route("/", methods=['GET'])
def index():
    return render_template("index.html")#, messages=messages)

@app.route('/loaddata', methods=['POST'])
def testfn():
  f = request.files['file']
  output_filename = join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename))
  f.save(output_filename)
  m.filename = output_filename
  return df_columns(output_filename)

def df_columns(filename):
  df = pd.read_csv(filename)
  cols = [c for c in df.columns if "Unnamed" not in c]
  return cols

@app.route('/look_for_template', methods=['GET'])
def look_for_template():
  nnname = request.args.get('nnname')
  filename = f"{nnname}.json"
  if isfile(filename):
    with open(filename) as f:
      data = json.load(f)
  else:
    data = {}
  return jsonify(data), 200

@app.route('/create_model', methods=['POST'])
def create_model():
  data = request.form.to_dict(flat=False)
  print (data)
  vars = [k for k in data.keys() if k.endswith("_x") or k.endswith("_y")]
  
  inputs = set([data[i][0] for i in data.keys() if i.endswith("_x")])
  outputs = set([data[i][0] for i in data.keys() if i.endswith("_y")])
  common = list(inputs.intersection(outputs))

  msg = 'OK'
  typ = ''

  if data['nnname'][0] == '':
    data['nnname'][0] = 'test'

  if len(inputs) < 2:
    msg = f"Need to select at least 2 input parameters."
    typ = 'variableError'
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
    data['filename'] = m.filename
    data['cols'] = df_columns(m.filename)
    with open(f"{data['nnname'][0]}.json", "w") as f:
      json.dump(data, f)

  return jsonify({'msg':msg, 'type':typ}), 200

@app.route('/train_model/', methods=['GET'])
def train_model():
  return render_template("training.html")

@app.route('/update_training_status')
def update_training_status():
  if request.args.get("status") == "END":
    json_data = json.dumps({'loss':request.args.get('loss'),
                            'val_loss':request.args.get('val_loss'),
                            'epochs':request.args.get('epochs')})
    msg = format_sse(data=json_data, event="end")
  else:
    if request.args.get('loss') is not None:
      json_data = json.dumps({'loss':request.args.get('loss'),
                              'val_loss':request.args.get('val_loss'),
                              'epoch':request.args.get('epoch')})
    else:
      json_data = "inf" 
    msg = format_sse(data=json_data, event="loss")
  announcer.announce(msg=msg)
  return {}, 200

@app.route('/listen', methods=['GET'])
def listen():
  def stream():
    messages = announcer.listen() 
    while True:
      msg = messages.get()
      yield msg
  return Response(stream(), mimetype='text/event-stream')
  
@app.route('/start_training', methods=['GET'])
def start_training():
  m.fit()
  return "OK", 200

@app.route("/save_model", methods=['GET'])
def save_model():
  exit_code, msg = m.save()
  print (exit_code, msg)
  if exit_code:
    msg = f"Model {msg} correctly saved.",  
    return jsonify({'msg':msg, 'status':"OK"}), 200
  else:
    return jsonify({'msg':msg, 'status':"ERROR"}), 200

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


if __name__ == "__main__":
    print (("* Loading Keras model and Flask starting server..."
            "please wait until server  has fully started"))
    app.run(debug=True, threaded=True)

