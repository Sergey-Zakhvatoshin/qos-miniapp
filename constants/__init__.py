# Welcome message constants
WELCOME_TITLE = "<b>Welcome to Quality of Style — Your Beauty Experts!</b>"

WELCOME_DESCRIPTION = (
    "We are professional beauty specialists dedicated to making you look and feel amazing.\n"
    "With years of experience and attention to every detail, we guarantee premium quality service."
)

SERVICES_LIST = (
    "Our services:\n"
    "• Manicure\n"
    "• Pedicure\n"
    "• Eyelash Extensions"
)

CALL_TO_ACTION = "Ready to transform your look? Choose a service below!"

# Button texts
USEFUL_INFO_BUTTON = "❕ Useful information"
BACK_TO_SERVICES_BUTTON = "⬅️ Back to services"
MINI_APP_LINK_TEXT = "🗺️ View location map"
PRICE_LIST_BUTTON = "💰 Price list"
REVIEWS_BUTTON = "⭐ Reviews"

# Review request messages
REVIEW_REQUEST_TITLE = "🌟 <b>How was your experience?</b>"
REVIEW_REQUEST_TEXT = (
    "Thank you for choosing Quality of Style!\n\n"
    "We'd love to hear about your visit. Please rate your experience with {service}:"
)
REVIEW_RATING_PROMPT = "Please select your rating (1-5):"
REVIEW_TEXT_PROMPT = (
    "Thank you! Would you like to leave a short review?\n\n"
    "Just type your feedback below (or type <b>skip</b> to skip):"
)
REVIEW_POSITIVE_THANKS = (
    "🎉 <b>Thank you for your wonderful review!</b>\n\n"
    "We're so glad you enjoyed your experience. "
    "It would mean a lot to us if you could share your experience on Yandex Maps too!"
)
REVIEW_POSITIVE_LINK = "📍 Leave a review on Yandex Maps"
REVIEW_NEGATIVE_THANKS = (
    "😔 <b>Thank you for your honest feedback.</b>\n\n"
    "We're sorry your experience didn't meet our standards. "
    "We'll work on improving our service to better meet your expectations.\n\n"
    "Your feedback has been forwarded to our management team. We hope to see you again!"
)

# Admin email notification
ADMIN_REVIEW_SUBJECT = "Negative Review Alert - {service}"
ADMIN_REVIEW_BODY = (
    "A negative review has been received:\n\n"
    "Service: {service}\n"
    "Rating: {rating}/5\n"
    "Customer: {name} (Telegram ID: {telegram_id})\n"
    "Appointment Date: {date}\n"
    "Time Slot: {time_slot}\n"
    "Review: {review_text}"
)

YANDEX_MAPS_LINK = "https://yandex.ru/maps/213/moscow/?ll=37.617700%2C55.755863&z=10"

WELCOME_MESSAGE = f"{WELCOME_TITLE}\n\n{WELCOME_DESCRIPTION}\n\n{SERVICES_LIST}\n\n{CALL_TO_ACTION}"

# Service selection messages
SERVICE_SELECTED_TITLE = "You selected: <b>{service}</b>"
SERVICE_SELECTED_DESCRIPTION = (
    "Great choice! Our specialists will provide the best service for you."
)
CHANGE_SERVICE_HINT = "Use the button below to change your selected service."

# Button texts
BACK_TO_SERVICES_BUTTON = "⬅️ Back to services"

# Client info collection
ASK_NAME_MESSAGE = (
    "Please enter your name so we know how to address you:\n\n"
    "(Just type your name in the chat)"
)

ASK_PHONE_MESSAGE = (
    "Now please enter your phone number in format: <b>8 XXX XXX XX XX</b> or <b>+7 XXX XXX XX XX</b>\n\n"
    "(Example: 8 999 123 45 67 or +7 999 123 45 67)"
)

PHONE_FORMAT_ERROR = (
    "❌ Invalid phone format. Please enter your number as: <b>8 XXX XXX XX XX</b> or <b>+7 XXX XXX XX XX</b>\n\n"
    "Example: 8 999 123 45 67\n\n"
    "Please try again:"
)

# Confirmation with client info
CONFIRMATION_WITH_CLIENT_INFO = (
    "Please confirm your appointment:\n\n"
    "📌 Service: <b>{service}</b>\n"
    "📅 Date: <b>{date}</b>\n"
    "⏰ Time: <b>{time_slot}</b>\n"
    "👤 Name: <b>{name}</b>\n"
    "📞 Phone: <b>{phone}</b>"
)

EDIT_BOOKING_HINT = "Use the button below to edit your booking if needed."

# Message after booking - offer to book another service or view appointments
BOOK_ANOTHER_MESSAGE = (
    "<b>What would you like to do next?</b>\n\n"
    "You can book another service or view your existing appointments."
)

# Booking confirmed message
BOOKING_CONFIRMED_WITH_CLIENT = (
    "☑️ Your appointment has been confirmed!\n\n"
    "📌 Service: <b>{service}</b>\n"
    "📅 Date: <b>{date}</b>\n"
    "⏰ Time: <b>{time_slot}</b>\n"
    "👤 Name: <b>{name}</b>\n"
    "📞 Phone: <b>{phone}</b>\n\n"
    "We look forward to seeing you!"
)
