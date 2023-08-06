import requests, pickle, os, traceback
import pandas as pd
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from keras.models import Sequential
from keras.layers import Dense
from keras.callbacks import Callback
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

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


class TrainingPlot(Callback):
  def __init__(self):
    self.epochs = 0
  
  def on_train_begin(self, logs={}):
    self.losses = []
    self.acc = []
    self.val_losses = []
    self.val_acc = []
    self.logs = []
    
  def on_epoch_end(self, epoch, logs={}):
    self.logs.append(logs)
    self.losses.append(logs.get('loss', 0))
    #self.acc.append(logs.get('acc', 0))
    self.val_losses.append(logs.get('val_loss', 0))
    #self.val_acc.append(logs.get('val_acc', 0))

    plot = False
    if self.epochs >= 100 and epoch%10 == 1:
      plot = True
    else:
      plot = True
        
    if plot:
      URL = "http://localhost:5000/update_training_status"
      PARAMS = {'loss': '{:0.4e}'.format(logs.get('loss', "")),
                'val_loss': '{:0.4e}'.format(logs.get('val_loss', "")),
                'epoch':epoch}
      r = requests.get(url = URL, params = PARAMS)

  def on_train_end(self, logs):
    URL = "http://localhost:5000/update_training_status"
    PARAMS = {'status':'END', 'epochs':self.epochs,
              'loss': '{:0.4e}'.format(self.losses[-1]),
                'val_loss': '{:0.4e}'.format(self.val_losses[-1]),}
    r = requests.get(url = URL, params = PARAMS)

    
class ModelAPI:
  def __init__(self):
    self.x_names = []
    self.y_names = []
    self.scaler_x = None
    self.scaler_y = None
    self.name = ""
    self.filename = ""
    self.do_scaling = False
    self.callback = TrainingPlot()
    self.model = None

  def prepare_sample(self, testfrac):
    df = pd.read_csv(self.filename)
    
    if self.do_scaling:
      self.scaler_x = MinMaxScaler()
      self.scaler_y = MinMaxScaler()
      self.x = self.scaler_x.fit_transform(df[self.x_names])
      self.y = self.scaler_y.fit_transform(df[self.y_names])
    else:
      self.x = df[self.x_names]
      self.y = df[self.y_names]
    
    self.x_train, self.x_test,self.y_train, self.y_test = train_test_split(self.x,
                                                                           self.y,
                                                                           test_size=testfrac)

  def create_model(self, data, inputs, outputs):
    self.name = data['nnname'][0]
    if 'loaded_file' in data:
      self.filename = data['loaded_file'][0]
    self.x_names = list(inputs)
    self.y_names = list(outputs)
    if 'scaling' in data:
      self.do_scaling = True
    self.epochs = int(data['epochs'][0])
    self.batch_size = int(data['batchsize'][0])
    self.optimizer = data['optimizer'][0]
    self.loss = data['loss'][0]
    self.prepare_sample(int(data['traintest'][0])/100)
    self.callback.epochs = self.epochs

    # FIXME use functional API is it better ?
    #ins = keras.Input(shape=(len(inputs),))
    
    self.model = Sequential()
    for i in range(len(data['type'])):
      if i == 0:
        if data['type'][i] == 'Linear':
          self.model.add(Dense(int(data['neurons'][i]), input_dim=len(inputs), activation=data['activation'][i]))
      else:
        if data['type'][i] == 'Linear':
          self.model.add(Dense(int(data['neurons'][i]), activation=data['activation'][i]))
    self.model.summary()
    self.model.compile(loss=self.loss,
                       optimizer=self.optimizer)

  def save(self):
    try:
      data = {"x_names":self.x_names, "y_names":self.y_names,
              "do_scaling":self.do_scaling,
              "x_scaler":self.scaler_x, "y_scaler":self.scaler_y}
      pickle.dump(data, open(f"{self.name}_data.pkl", "wb"))
      self.model.save(self.name)
    except Exception:
      err = traceback.format_exc()
      #print (err)
      return False, err
    else:
      return True, self.name
  
  def load(self):
    data = pickle.load(open(f"{self.name}_data.pkl", "rb"))
    self.x_names = data["x_names"]
    self.y_names = data["y_names"]
    self.scaler_x = data["x_scaler"]
    self.scaler_y = data["y_scaler"]
    #model = load_model(self.name)
    return "Data loaded"

  def predict(self):
    x0 = 1
    x_transf = scale_X.transform([[x0]])
    print (scale_y.inverse_transform(model.predict(x_transf)))
    
  def check_overfit(self):
    eval_train = self.model.evaluate(self.x_train, self.y_train)
    #print('Training: {}'.format(eval_train))
    eval_test = self.model.evaluate(self.x_test, self.y_test)
    #print('Test: {}'.format(eval_test))
    
  def fit(self):
    if self.model is None:
      return
    self.model.reset_states()
    history = self.model.fit(self.x_train, self.y_train,
                             batch_size = self.batch_size, epochs = self.epochs,
                             callbacks = [self.callback],
                             validation_data=(self.x_test, self.y_test),
                             verbose=0)
    //self.check_overfit()

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
