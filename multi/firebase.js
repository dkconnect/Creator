
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.9.0/firebase-app.js";
import {
  getDatabase,
  ref,
  set,
  get,
  update,
  onValue,
  remove
} from "https://www.gstatic.com/firebasejs/12.9.0/firebase-database.js";

const firebaseConfig = {
  apiKey: "AIzaSyDd5KnFP9s0OJeO6NKenVbfd6__FNUYq9o",
  authDomain: "thecreator-game.firebaseapp.com",
  databaseURL: "https://thecreator-game-default-rtdb.firebaseio.com",
  projectId: "thecreator-game",
  storageBucket: "thecreator-game.firebasestorage.app",
  messagingSenderId: "867218271238",
  appId: "1:867218271238:web:6a7d349894015ad0696787"
};


export const app = initializeApp(firebaseConfig);

// Realtime Database
export const db = getDatabase(app);

export { ref, set, get, update, onValue, remove };
