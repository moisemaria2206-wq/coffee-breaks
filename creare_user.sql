CREATE DATABASE coffee_breaks ENCODING 'UTF8';
CREATE USER coffee_user WITH ENCRYPTED PASSWORD 'parola_aici';
GRANT ALL ON DATABASE coffee_breaks TO coffee_user;

-- se rulează conectat la baza coffee_breaks
CREATE SCHEMA django AUTHORIZATION coffee_user;
ALTER ROLE coffee_user SET search_path = django, public;
GRANT ALL ON SCHEMA django TO coffee_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA django TO coffee_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA django TO coffee_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA django TO coffee_user;