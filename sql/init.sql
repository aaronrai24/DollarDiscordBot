CREATE TABLE IF NOT EXISTS cash.users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255),
    home_address VARCHAR(255),
    work_address VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS cash.games (
    game_id INT AUTO_INCREMENT PRIMARY KEY,
    game_name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS cash.game_subscriptions (
    subscription_id INT AUTO_INCREMENT  PRIMARY KEY,
    user_id INT,
    game_id INT,
    FOREIGN KEY (user_id) REFERENCES cash.users(user_id),
    FOREIGN KEY (game_id) REFERENCES cash.games(game_id)
);

CREATE TABLE IF NOT EXISTS cash.guilds (
    guild_id INT AUTO_INCREMENT PRIMARY KEY,
    guild_name VARCHAR(255),
    owner_id INT,
    FOREIGN KEY (owner_id) REFERENCES cash.users(user_id)
);

CREATE TABLE IF NOT EXISTS cash.guild_preferences (
    preference_id INT AUTO_INCREMENT PRIMARY KEY,
    guild_id INT,
    text_channel VARCHAR(255),
    voice_channel VARCHAR(255),
    shows_channel_name VARCHAR(255),
    FOREIGN KEY (guild_id) REFERENCES cash.guilds(guild_id)
);