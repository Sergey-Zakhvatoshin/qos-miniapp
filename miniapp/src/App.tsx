import { useEffect, useState } from 'react';
import './App.css';
import PriceList from './components/PriceList.tsx';
import Reviews from './components/Reviews.tsx';
import directionsImg from './assets/images/directions.webp';

type Page = 'map' | 'price-list' | 'reviews';

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('map');

  useEffect(() => {
    const tg = window.Telegram!.WebApp;
    tg.ready();
    tg.expand();

    const getPageFromUrl = (): Page => {
      const urlParams = new URLSearchParams(window.location.search);
      const page = urlParams.get('page');
      if (page === 'price-list') {
        return 'price-list';
      }
      if (page === 'reviews') {
        return 'reviews';
      }
      return 'map';
    };

    setCurrentPage(getPageFromUrl());
  }, []);

  return (
    <div className="app">
      {currentPage === 'price-list' ? (
        <PriceList />
      ) : currentPage === 'reviews' ? (
        <Reviews />
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
