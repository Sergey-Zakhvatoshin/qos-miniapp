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

    const getPageFromUrl = () => {
      const urlParams = new URLSearchParams(window.location.search);
      const page = urlParams.get('page');
      if (page === 'price-list') {
        return 'price-list';
      }
      return 'map';
    };

    setCurrentPage(getPageFromUrl());
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
