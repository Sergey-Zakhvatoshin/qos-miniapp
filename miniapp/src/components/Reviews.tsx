import { useEffect } from 'react';
import './Reviews.css';

interface Review {
  id: number;
  service: string;
  rating: number;
  name: string;
  text: string;
}

interface StarRatingProps {
  rating: number;
}

const reviewsData: Review[] = [
  {
    id: 1,
    service: 'Classic Manicure',
    rating: 5,
    name: 'Anna Petrova',
    text: 'Amazing service! My nails have never looked better. The master was very professional and attentive. Highly recommend!',
  },
  {
    id: 2,
    service: 'Gel Pedicure',
    rating: 5,
    name: 'Maria Ivanova',
    text: 'Perfect pedicure! The gel polish lasted for 3 weeks without any chips. Very satisfied with the quality.',
  },
  {
    id: 3,
    service: 'Volume Lash Extensions (2D-3D)',
    rating: 4,
    name: 'Elena Smirnova',
    text: 'Beautiful lash extensions! The only reason for 4 stars is that it took a bit longer than expected. But the result is worth it!',
  },
  {
    id: 4,
    service: 'Spa Manicure',
    rating: 5,
    name: 'Olga Kuznetsova',
    text: 'The spa manicure was incredibly relaxing. My hands feel so soft and smooth. The massage was heavenly!',
  },
  {
    id: 5,
    service: 'Classic Lash Extensions',
    rating: 5,
    name: 'Natalia Volkova',
    text: 'Natural and beautiful lashes! Exactly what I wanted. The master understood my preferences perfectly.',
  },
  {
    id: 6,
    service: 'Russian Manicure',
    rating: 4,
    name: 'Svetlana Morozova',
    text: 'Very thorough and precise manicure. The cuticle work is impeccable. Will definitely come back!',
  },
  {
    id: 7,
    service: 'Lash Lift & Tint',
    rating: 5,
    name: 'Ekaterina Sokolova',
    text: 'My natural lashes look amazing! The lift and tint gave them the perfect curl and color. Love it!',
  },
  {
    id: 8,
    service: 'Mega Volume Lashes',
    rating: 5,
    name: 'Tatiana Lebedeva',
    text: 'Dramatic and gorgeous! Got so many compliments. The master is a true artist.',
  },
];

function StarRating({ rating }: StarRatingProps) {
  return (
    <div className="rating">
      {[1, 2, 3, 4, 5].map((star) => (
        <span
          key={star}
          className={`star ${star <= rating ? 'star--active' : ''}`}
        >
          ★
        </span>
      ))}
    </div>
  );
}

function Reviews() {
  useEffect(() => {
    const tg = window.Telegram!.WebApp;
    tg.ready();
    tg.expand();

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
    <div className="reviews">
      <h1 className="reviews__title">Customer Reviews</h1>
      <div className="reviews__list">
        {reviewsData.map((review) => (
          <div key={review.id} className="review-card">
            <h2 className="review-card__service">{review.service}</h2>
            <StarRating rating={review.rating} />
            <p className="review-card__name">{review.name}</p>
            <p className="review-card__text">{review.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Reviews;
