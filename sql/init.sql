CREATE SCHEMA IF NOT EXISTS dollar;

CREATE TABLE IF NOT EXISTS dollar.users (
    user_id SERIAL PRIMARY KEY,
    discord_id VARCHAR(255),
    username VARCHAR(255),
    home_address VARCHAR(255),
    work_address VARCHAR(255),
    time_zone VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS dollar.games (
    game_id SERIAL PRIMARY KEY,
    game_name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS dollar.game_subscriptions (
    subscription_id SERIAL PRIMARY KEY,
    user_id INT,
    game_id INT,
    FOREIGN KEY (user_id) REFERENCES dollar.users(user_id),
    FOREIGN KEY (game_id) REFERENCES dollar.games(game_id)
);

CREATE TABLE IF NOT EXISTS dollar.guilds (
    guild_id SERIAL PRIMARY KEY,
    guild_name VARCHAR(255),
    owner_id INT,
    FOREIGN KEY (owner_id) REFERENCES dollar.users(user_id)
);

CREATE TABLE IF NOT EXISTS dollar.guild_preferences (
    preference_id SERIAL PRIMARY KEY,
    guild_id INT UNIQUE,
    text_channel VARCHAR(255),
    voice_channel VARCHAR(255),
    shows_channel VARCHAR(255),
    FOREIGN KEY (guild_id) REFERENCES dollar.guilds(guild_id)
);