import pickle
import os

def load(filename):
  if os.path.exists(filename):
    with open(filename, 'rb') as f:
      obj = pickle.load(f)
    
    return obj

def dump(obj, filename):
  with open(filename, 'wb') as f:
    pickle.dump(obj, f)