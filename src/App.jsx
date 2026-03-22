import { useEffect, useState } from 'react';
import './App.css';
import PriceList from './components/PriceList';
import directionsImg from './assets/images/directions.webp';

function App() {
  const [currentPage, setCurrentPage] = useState('map');

  useEffect(() => {
    const tg = window.Telegram.WebApp;
    tg.ready();
    tg.expand();

    const handleHashChange = () => {
      const hash = window.location.hash.slice(1);
      if (hash === 'price-list') {
        setCurrentPage('price-list');
      } else {
        setCurrentPage('map');
      }
    };

    handleHashChange();
    window.addEventListener('hashchange', handleHashChange);

    return () => {
      window.removeEventListener('hashchange', handleHashChange);
    };
  }, []);

  return (
    <div className="app">
      {currentPage === 'price-list' ? (
        <PriceList />
      ) : (
        <img
          src={directionsImg}
          alt="Location directions"
          className="directions-image"
        />
      )}
    </div>
  );
}

export default App;
