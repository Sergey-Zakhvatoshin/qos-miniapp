import { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [telegram, setTelegram] = useState(null);
  const [themeParams, setThemeParams] = useState({});

  useEffect(() => {
    // Initialize Telegram WebApp
    const tg = window.Telegram.WebApp;
    setTelegram(tg);

    // Get theme parameters
    const params = tg.themeParams || {};
    setThemeParams(params);

    // Tell Telegram the app is ready
    tg.ready();
    tg.expand();

    // Adjust colors to Telegram theme
    document.body.style.backgroundColor = params.bg_color || '#ffffff';
    document.body.style.color = params.text_color || '#000000';

    return () => {
      tg.close();
    };
  }, []);

  // Salon address
  const salonAddress = 'Moscow, ul. Primernaya, d. 15';
  const salonPhone = '+7 (999) 123-45-67';

  // Map links
  const yandexMapsUrl = `https://yandex.ru/maps/?text=${encodeURIComponent(salonAddress)}`;
  const googleMapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(salonAddress)}`;

  return (
    <div className="app">
      <header className="header">
        <h1>Quality of Style</h1>
        <p className="subtitle">Your Beauty Salon</p>
      </header>

      <main className="main-content">
        <section className="address-section">
          <h2>📍 Our Address</h2>
          <p className="address">{salonAddress}</p>
          <p className="phone">📞 {salonPhone}</p>
        </section>

        <section className="map-section">
          <h2>🗺️ Location Map</h2>

          {/* Static map diagram */}
          <div className="map-container">
            <div className="map-placeholder">
              <svg
                viewBox="0 0 400 300"
                className="map-svg"
              >
                {/* Background */}
                <rect
                  width="400"
                  height="300"
                  fill={themeParams.bg_color || '#f0f0f0'}
                />

                {/* Main street */}
                <rect
                  x="0"
                  y="130"
                  width="400"
                  height="40"
                  fill="#cccccc"
                />
                <text
                  x="200"
                  y="155"
                  textAnchor="middle"
                  fontSize="12"
                  fill="#666"
                >
                  ul. Primernaya
                </text>

                {/* Side street */}
                <rect
                  x="180"
                  y="0"
                  width="40"
                  height="300"
                  fill="#dddddd"
                />

                {/* Salon building */}
                <rect
                  x="230"
                  y="100"
                  width="60"
                  height="50"
                  fill="#ff6b6b"
                  rx="5"
                />
                <text
                  x="260"
                  y="125"
                  textAnchor="middle"
                  fontSize="10"
                  fill="white"
                >
                  Salon
                </text>
                <text
                  x="260"
                  y="140"
                  textAnchor="middle"
                  fontSize="10"
                  fill="white"
                >
                  QoS
                </text>

                {/* Location marker */}
                <circle
                  cx="260"
                  cy="85"
                  r="15"
                  fill="#4CAF50"
                />
                <text
                  x="260"
                  y="90"
                  textAnchor="middle"
                  fontSize="16"
                  fill="white"
                >
                  📍
                </text>

                {/* Landmarks */}
                <rect
                  x="50"
                  y="50"
                  width="50"
                  height="40"
                  fill="#a8d5ba"
                  rx="3"
                />
                <text
                  x="75"
                  y="75"
                  textAnchor="middle"
                  fontSize="9"
                  fill="#333"
                >
                  Park
                </text>

                <rect
                  x="300"
                  y="200"
                  width="70"
                  height="50"
                  fill="#b8c5e8"
                  rx="3"
                />
                <text
                  x="335"
                  y="230"
                  textAnchor="middle"
                  fontSize="9"
                  fill="#333"
                >
                  Shopping Center
                </text>

                {/* Direction arrow */}
                <path
                  d="M 150 180 L 170 180 L 165 175 M 170 180 L 165 185"
                  stroke="#4CAF50"
                  strokeWidth="2"
                  fill="none"
                />
                <text
                  x="145"
                  y="175"
                  fontSize="10"
                  fill="#4CAF50"
                >
                  Entrance
                </text>
              </svg>
            </div>
          </div>

          <div className="directions">
            <h3>How to get there:</h3>
            <ol>
              <li>Go along ul. Primernaya to building №15</li>
              <li>Landmark: green building with "Quality of Style" sign</li>
              <li>Entrance from the main street side</li>
              <li>Near "Primer" Shopping Center</li>
            </ol>
          </div>
        </section>

        <section className="navigation-section">
          <h2>🚗 Open in Navigator</h2>
          <div className="buttons">
            <a
              href={yandexMapsUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="nav-button yandex"
            >
              Yandex.Maps
            </a>
            <a
              href={googleMapsUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="nav-button google"
            >
              Google Maps
            </a>
          </div>
        </section>
      </main>

      <footer className="footer">
        <p>We are waiting for you! ✨</p>
      </footer>
    </div>
  );
}

export default App;
