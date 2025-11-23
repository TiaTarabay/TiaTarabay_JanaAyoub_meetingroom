-- Bookings table (used by Bookings service)
CREATE TABLE IF NOT EXISTS bookings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'CONFIRMED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reviews table (used by Reviews service)
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment VARCHAR(500),
    status VARCHAR(20) DEFAULT 'ACTIVE',   -- ACTIVE / DELETED
    is_flagged BOOLEAN DEFAULT FALSE,      -- moderation flag
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- (Optional for later, when you and Tia are ready)
-- CREATE TABLE IF NOT EXISTS users (...);
-- CREATE TABLE IF NOT EXISTS rooms (...);
