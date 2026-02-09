import React from 'react';
import './App.css';

function App() {
  return (
    <div style={{ 
      padding: '50px', 
      textAlign: 'center',
      backgroundColor: '#f0f9f0',
      minHeight: '100vh'
    }}>
      <h1 style={{ color: 'green', fontSize: '2.5em', marginBottom: '20px' }}>
        🌾 AgriSmart Farmer's Assistant
      </h1>
      
      <p style={{ fontSize: '1.2em', marginBottom: '30px' }}>
        🎉 FINALLY WORKING! Frontend is ready!
      </p>

      <button 
        style={{
          padding: '12px 24px',
          fontSize: '16px',
          backgroundColor: 'blue',
          color: 'white',
          border: 'none',
          borderRadius: '5px',
          margin: '10px',
          cursor: 'pointer'
        }}
        onClick={() => window.open('http://127.0.0.1:8000', '_blank')}
      >
        Check Backend
      </button>

      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        gap: '20px',
        flexWrap: 'wrap',
        marginTop: '40px'
      }}>
        <div style={{
          padding: '20px',
          border: '2px solid green',
          borderRadius: '10px',
          width: '200px',
          backgroundColor: 'white'
        }}>
          <h3>🌾 Yield Predictor</h3>
          <p>Predict crop yields</p>
        </div>

        <div style={{
          padding: '20px',
          border: '2px solid blue',
          borderRadius: '10px',
          width: '200px',
          backgroundColor: 'white'
        }}>
          <h3>🌱 Crop Recommender</h3>
          <p>Best crops for your land</p>
        </div>

        <div style={{
          padding: '20px',
          border: '2px solid orange',
          borderRadius: '10px',
          width: '200px',
          backgroundColor: 'white'
        }}>
          <h3>🦠 Disease Detector</h3>
          <p>Identify plant diseases</p>
        </div>
      </div>
    </div>
  );
}

export default App;