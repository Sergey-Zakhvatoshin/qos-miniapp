import { useEffect } from 'react';
import './App.css';
import directionsImg from './assets/images/directions.webp';

function App() {
  useEffect(() => {
    const tg = window.Telegram.WebApp;
    tg.ready();
    tg.expand();
  }, []);

  return (
    <div className="app">
      <img
        src={directionsImg}
        alt="Location directions"
        className="directions-image"
      />
    </div>
  );
}

export default App;
