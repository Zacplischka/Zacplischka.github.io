-- Create SuperCoach Prices Table
CREATE TABLE supercoach_prices (
    full_name VARCHAR(100) NULL,
    abbreviated_name VARCHAR(50) NULL,
    team VARCHAR(50) NULL,
    current_price VARCHAR(20) NULL,              -- Stored as text with $ formatting
    total_change VARCHAR(20) NULL,               -- Stored as text with +/- and $ formatting
    change_percentage VARCHAR(10) NULL,          -- Stored as text with % formatting
    last_change VARCHAR(20) NULL,                -- Stored as text with +/- and $ formatting
    expected_price VARCHAR(20) NULL,             -- Stored as text with $ formatting
    expected_change VARCHAR(20) NULL,            -- Stored as text with +/- and $ formatting
    expected_price_2 VARCHAR(20) NULL,           -- Stored as text with $ formatting
    expected_change_2 VARCHAR(20) NULL,          -- Stored as text with +/- and $ formatting
    expected_price_3 VARCHAR(20) NULL,           -- Stored as text with $ formatting
    expected_change_3 VARCHAR(20) NULL,          -- Stored as text with +/- and $ formatting
    scraped_date DATE NULL                       -- When the data was scraped
);


CREATE TABLE supercoach_prices (
    player_id INTEGER NULL,                      -- References player_details.id
    full_name VARCHAR(100) NULL,
    abbreviated_name VARCHAR(50) NULL,
    team VARCHAR(50) NULL,
    current_price DECIMAL(8,0) NULL,             -- Numerical price value (e.g., 731200)
    total_change DECIMAL(8,0) NULL,              -- Numerical change value (can be negative)
    change_percentage DECIMAL(5,2) NULL,         -- Percentage as decimal (e.g., 6.00, -63.00)
    last_change DECIMAL(8,0) NULL,               -- Numerical last change value (can be negative)
    expected_price DECIMAL(8,0) NULL,            -- Numerical expected price
    expected_change DECIMAL(8,0) NULL,           -- Numerical expected change (can be negative)
    expected_price_2 DECIMAL(8,0) NULL,          -- Numerical expected price 2
    expected_change_2 DECIMAL(8,0) NULL,         -- Numerical expected change 2 (can be negative)
    expected_price_3 DECIMAL(8,0) NULL,          -- Numerical expected price 3
    expected_change_3 DECIMAL(8,0) NULL,         -- Numerical expected change 3 (can be negative)
    scraped_date DATE NULL                       -- When the data was scraped
);DROP TABLE IF EXISTS supercoach_prices;select * from supercoach_prices
ORDER BY expected_change ASC;select * from supercoach_prices
ORDER BY expected_change ASC;