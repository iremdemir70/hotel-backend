# Project Demo Video

Watch the demo video here: [Hotel Booking Web App Demo](https://drive.google.com/file/d/1kPilOSCl2f2xOojf9Qg1DSrWoEoz-BUV/view?usp=sharing)

---

# Hotel Booking Web App  
Deployed at: [Vercel](https://hotel-frontend-lemon.vercel.app)

This project is a hotel listing and search web application where users can search hotels based on city, dates, and number of guests. The project consists of a **Flask-based backend** and an **Angular frontend**, both deployed online for public access.

---
## Data Model
The application uses a PostgreSQL database hosted on Supabase. Here is a brief overview of the data model:
- **User**: Stores personal info and login method (Google/email).
- **Hotel**: Includes name, price, location, coordinates, rating, image.
- **Amenity / HotelAmenity**: Many-to-many relation between hotels and features.
- **Comment / Rating**: Each comment has a detailed rating (5 aspects).
- **HotelAvailability**: Used for filtering hotels by available dates.

---

## Assumptions

- Only hotel **searching and viewing** is implemented, not booking.
- Users log in via **Google OAuth or email-password**.
- Hotel locations are shown on **Google Maps** with price markers.
- Supabase is used privately through env vars.

---
## Backend - Flask API

### Features

- Built with Flask (Python)
- PostgreSQL database hosted on **Supabase**
- JWT authentication with Google OAuth login support
- RESTful endpoints for hotel listing and search
- Deployed on **Render**
- Kept awake using periodic pings via **Uptime Robot**

### Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables in a .env file
FLASK_ENV=development
DATABASE_URL=supabase_connection_url
JWT_SECRET_KEY=secret_key

# Run database migrations
flask db init
flask db migrate
flask db upgrade

# Run the app
flask run
```

### Project Structure

```
backend/
│
├── app/
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── hotel_routes.py
│   ├── utils/
│   │   └── auth.py
│   ├── models.py
│   ├── extensions.py
│   └── __init__.py
│
├── migrations/
├── .env
├── requirements.txt
├── app.py
├── wsgi.py
└── Procfile //For Render
```

### Deployment

- Hosted on **Render**: https://hotel-backend-minh.onrender.com
- **Uptime Robot** is used to send periodic bot requests to keep the backend awake.

---

##  Frontend - Angular

### Features

- Built with **Angular**
- Allows users to search hotels based on city, dates, and guests
- Google OAuth login support
- Interactive hotel cards showing ratings, pricing, and location
- Hotels are displayed on **Google Maps** with price markers
- Deployed on **Vercel**

### Local Setup

```bash
# Install dependencies
npm install

# Start the Angular development server
ng serve
```

### Project Structure

```
frontend/
└── src/
    ├── app/
    │   ├── pages/
    │   │   ├── home-page/
    │   │   ├── hotel-detail/
    │   │   ├── login-page/
    │   │   └── register/
    │   ├── app.component.ts / html / scss
    │   ├── app.routes.ts
    │   └── app.module.ts
    ├── environments/
    │   ├── environment.ts
    │   └── environment.prod.ts
    └── index.html
```

### Deployment

- Hosted on **Vercel**: https://hotel-frontend-lemon.vercel.app/login
- Environment-specific configurations are handled through `environment.prod.ts`

---

