import { useEffect } from 'react';
import './PriceList.css';

const priceData = {
  manicure: {
    title: 'Manicure Services',
    items: [
      {
        name: 'Classic Manicure',
        description: 'Basic nail shaping, cuticle care, and polish',
        price: '1 200 ₽',
      },
      {
        name: 'Gel Polish Manicure',
        description: 'Long-lasting gel polish with perfect shine',
        price: '1 800 ₽',
      },
      {
        name: 'Russian Manicure',
        description: 'Deep cuticle cleaning with e-file technique',
        price: '2 200 ₽',
      },
      {
        name: 'Spa Manicure',
        description: 'Manicure with scrub, mask, and hand massage',
        price: '2 500 ₽',
      },
      {
        name: 'Nail Art Design',
        description: 'Custom nail design (per set)',
        price: '1 000 ₽',
      },
    ],
  },
  pedicure: {
    title: 'Pedicure Services',
    items: [
      {
        name: 'Classic Pedicure',
        description: 'Foot care, nail shaping, and polish',
        price: '1 800 ₽',
      },
      {
        name: 'Gel Pedicure',
        description: 'Pedicure with long-lasting gel polish',
        price: '2 400 ₽',
      },
      {
        name: 'Spa Pedicure',
        description: 'Full treatment with scrub, mask, and massage',
        price: '2 800 ₽',
      },
      {
        name: 'Medical Pedicure',
        description: 'Treatment for calluses and foot issues',
        price: '3 000 ₽',
      },
      {
        name: 'Express Pedicure',
        description: 'Quick nail care and polish refresh',
        price: '1 200 ₽',
      },
    ],
  },
  lashes: {
    title: 'Lash Extensions',
    items: [
      {
        name: 'Classic Lash Extensions',
        description: 'Natural 1:1 lash extension technique',
        price: '2 500 ₽',
      },
      {
        name: 'Volume Lash Extensions (2D-3D)',
        description: 'Fuller look with multiple lashes per natural lash',
        price: '3 200 ₽',
      },
      {
        name: 'Mega Volume Lashes',
        description: 'Dramatic, dense lash effect',
        price: '4 000 ₽',
      },
      {
        name: 'Lash Lift & Tint',
        description: 'Natural lash curl with color enhancement',
        price: '2 000 ₽',
      },
      {
        name: 'Lash Removal',
        description: 'Safe and gentle lash extension removal',
        price: '800 ₽',
      },
    ],
  },
};

function PriceList() {
  useEffect(() => {
    const tg = window.Telegram.WebApp;
    tg.ready();
    tg.expand();

    // Устанавливаем цвета вручную на случай, если CSS переменные не работают
    document.body.style.backgroundColor = tg.themeParams.bg_color || '#ffffff';
    document.documentElement.style.setProperty(
      '--tg-text-color',
      tg.themeParams.text_color || '#000000',
    );
    document.documentElement.style.setProperty(
      '--tg-hint-color',
      tg.themeParams.hint_color || '#999999',
    );
    document.documentElement.style.setProperty(
      '--tg-button-color',
      tg.themeParams.button_color || '#3390ec',
    );
    document.documentElement.style.setProperty(
      '--tg-button-text-color',
      tg.themeParams.button_text_color || '#ffffff',
    );
    document.documentElement.style.setProperty(
      '--tg-secondary-bg-color',
      tg.themeParams.secondary_bg_color || '#f0f0f0',
    );
  }, []);

  return (
    <div className="price-list">
      <h1 className="price-list__title">Our Price List</h1>

      {Object.entries(priceData).map(([category, data]) => (
        <section
          key={category}
          className="price-list__category"
          id={category}
        >
          <h2 className="price-list__category-title">{data.title}</h2>
          <div className="price-list__items">
            {data.items.map((item, index) => (
              <div
                key={index}
                className="price-list__item"
              >
                <div className="price-list__item-header">
                  <h3 className="price-list__item-name">{item.name}</h3>
                  <span className="price-list__item-price">{item.price}</span>
                </div>
                <p className="price-list__item-description">{item.description}</p>
              </div>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}

export default PriceList;
