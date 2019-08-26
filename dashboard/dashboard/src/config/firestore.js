import Firebase from 'firebase';

const config = {
  apiKey: 'AIzaSyBFaAMofqAcv039UnDmmRNz_U3oDpayrTc',
  authDomain: 'jinjirome-test.firebaseapp.com',
  databaseURL: 'https://jinjirome-test.firebaseio.com',
  projectId: 'jinjirome-test',
  storageBucket: 'jinjirome-test.appspot.com',
  messagingSenderId: '212019270274',
  appId: '1:212019270274:web:9dfcf77b5d4a95a5',
};

const firebaseInstance = Firebase.initializeApp(config)

export const db = firebaseInstance.firestore()
export const storage = firebaseInstance.storage()