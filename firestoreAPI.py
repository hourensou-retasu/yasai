import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

class FireStoreDB:
  def __init__(self):
    cred = credentials.Certificate('conf/firebase.json')
    firebase_admin.initialize_app(cred)
    
    self.db = firestore.client()
