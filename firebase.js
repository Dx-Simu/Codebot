<!-- firebase.js -->
<script type="module">
  import { initializeApp } from "https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js";
  import { getAuth, onAuthStateChanged, signInAnonymously } from "https://www.gstatic.com/firebasejs/10.14.1/firebase-auth.js";
  import { getDatabase, ref, push, set, onValue, remove, update, serverTimestamp, query, orderByChild, limitToLast } from "https://www.gstatic.com/firebasejs/10.14.1/firebase-database.js";
  import { getStorage, ref as sRef, uploadBytes, getDownloadURL } from "https://www.gstatic.com/firebasejs/10.14.1/firebase-storage.js";

  const firebaseConfig = {
    apiKey: "AIzaSyAlPc5ggTLg7NvHispFP4YpwQv7F-CCi68",
    authDomain: "mahi-chat-4dd1b.firebaseapp.com",
    databaseURL: "https://mahi-chat-4dd1b-default-rtdb.firebaseio.com",
    projectId: "mahi-chat-4dd1b",
    storageBucket: "mahi-chat-4dd1b.appspot.com",
    messagingSenderId: "590135005998",
    appId: "1:590135005998:web:your-app-id"
  };

  const app = initializeApp(firebaseConfig);
  const db = getDatabase(app);
  const storage = getStorage(app);
  const auth = getAuth(app);

  // Auto anonymous login constant
  signInAnonymously(auth);

  window.firebaseDB = { db, ref, push, set, onValue, remove, update, serverTimestamp, query, orderByChild, limitToLast };
  window.firebaseStorage = { storage, sRef, uploadBytes, getDownloadURL };
  window.firebaseAuth = auth;
</script>
