import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { marked } from 'marked';
import { auth } from './firebaseConfig';
import { createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut } from "firebase/auth";
import './App.css';
import logo from './indonesia-skyline-silhouette-vector.png'; // Import the logo

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const chatContainerRef = useRef(null);
  const [user, setUser] = useState(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false); // Add loading state
  const [authError, setAuthError] = useState(''); // Add error state

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }

    const unsubscribe = auth.onAuthStateChanged((authUser) => {
      if (authUser) {
        setUser(authUser);
      } else {
        setUser(null);
      }
    });

    return () => unsubscribe();
  }, [messages]);

  const handleSignUp = async () => {
    try {
      setAuthError(''); // Clear previous errors
      await createUserWithEmailAndPassword(auth, email, password);
    } catch (error) {
      switch (error.code) {
        case 'auth/email-already-in-use':
          setAuthError('This email address is already in use. Please sign in or use a different email.');
          break;
        case 'auth/weak-password':
          setAuthError('Password should be at least 6 characters.');
          break;
        default:
          setAuthError('An unexpected error occurred. Please try again.');
          break;
      }
    }
  };

  const handleSignIn = async () => { // Add event parameter
  //  if (event && event.key !== 'Enter') return; // Check for Enter key
    try {
      setAuthError(''); // Clear previous errors
      await signInWithEmailAndPassword(auth, email, password);
    } catch (error) {
      switch (error.code) {
        case 'auth/user-not-found':
          setAuthError('Incorrect email or password. Please try again.');
          break;
        case 'auth/invalid-credential':
          setAuthError('Incorrect email or password. Please try again.');
          break;
          case 'auth/invalid-email':
            setAuthError('Incorrect email or password. Please try again.');
            break;          
        default:
          setAuthError('An unexpected error occurred. Please try again.');
          break;
      }
    }
  };

  const handleSignOut = async () => {
    try {
      await signOut(auth);
      setMessages([]); // Clear chat messages
    } catch (error) {
      alert(error.message);
    }
  };

  const sendMessage = async () => {
    if (input.trim() === '') return;

    const newMessage = { text: input, sender: 'user' };
    setMessages((prevMessages) => [...prevMessages, newMessage]);
    setInput('');
    setIsLoading(true); // Set loading to true

    try {
      const token = await user.getIdToken();
      const response = await axios.post('/chat', { message: input }, {
        headers: {
          Authorization: token,
        },
      });
      const botMessage = {
        text: marked(response.data.response),
        sender: 'chatbot',
      };
      setMessages((prevMessages) => [...prevMessages, botMessage]);
      setIsLoading(false); // Set loading to false
    } catch (error) {
      const errorMessage = { text: `Error: ${error.message}`, sender: 'error' };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
      setIsLoading(false); // Set loading to false
    }
  };

  if (!user) {
    return (
      <div className="auth-container">
        <input 
        type="email" 
        placeholder="Email" 
        value={email} 
        onChange={(e) => setEmail(e.target.value)} />
        <input 
        type="password" 
        placeholder="Password" 
        value={password} 
        onChange={(e) => setPassword(e.target.value)}
        onKeyPress={(event) => { // Added the enter key check here.
          if (event.key === 'Enter') {
            handleSignIn();
          }
        }} 
        />
        {authError && <div className="auth-error">{authError}</div>}
        <button onClick={handleSignIn}>Sign In</button>
        <button onClick={handleSignUp}>Sign Up</button>
      </div>
    );
  }

  return (
    <div className="App">
      <div className="logo-container">
        <img
          src={logo} 
          alt="Indonesia Skyline Logo"
          className="logo"
        />
      </div>    
      <div className="chat-app">
        <div className="chat-container" ref={chatContainerRef}>
          {messages.length === 0 && !isLoading ? ( // Check for empty messages and no loading
            <div className="welcome-message">
              Wisata Indo? Gas, tanya aja!.
            </div>
          ) : (
            <>
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.sender}`}>
              {message.sender === 'chatbot' ? (
                <div dangerouslySetInnerHTML={{ __html: message.text }} />
              ) : (
                message.text
              )}
            </div>
          ))}
          {isLoading && (
            <div className="loading">
              <div className="spinner"></div>
              Lagi mikir jawaban nih...
            </div>
          )}
          </>
          )}
        </div>
        <div className="input-area">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          />
          <button onClick={sendMessage}>Send</button>
          <button onClick={handleSignOut}>Sign Out</button>
        </div>
      </div>
    </div>
  );
}

export default App;