-- AFL Database Table Creation Script (CORRECTED VERSION)
-- Created for AFL Player Details and Player Stats data (2015-2025)
-- Based on actual CSV data analysis

-- Drop tables if they exist
DROP TABLE IF EXISTS supercoach_prices;
DROP TABLE IF EXISTS player_stats;
DROP TABLE IF EXISTS player_details;

-- Create Player Details Table
CREATE TABLE player_details (
    firstName VARCHAR(100) NULL,
    surname VARCHAR(100) NULL,
    id INTEGER NULL,
    team VARCHAR(100) NULL,
    season INTEGER NULL,
    jumperNumber INTEGER NULL,
    providerId VARCHAR(50) NULL,
    dateOfBirth DATE NULL,
    draftYear VARCHAR(20) NULL,
    heightInCm INTEGER NULL,
    weightInKg INTEGER NULL,
    recruitedFrom TEXT NULL,
    debutYear VARCHAR(20) NULL,
    draftType VARCHAR(50) NULL,
    draftPosition VARCHAR(20) NULL,
    position VARCHAR(50) NULL,
    data_accessed DATE NULL
);

-- Create SuperCoach Prices Table
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
);

-- Create Player Stats Table  
CREATE TABLE player_stats (
    venue_name VARCHAR(150) NULL,                    -- Max length: 30
    match_id INTEGER NULL,                           -- int64 - OK
    match_home_team VARCHAR(100) NULL,               -- Max length: 22  
    match_away_team VARCHAR(100) NULL,               -- Max length: 22
    match_date DATE NULL,                            -- Date string - OK
    match_local_time TIME NULL,                      -- Time string - OK
    match_attendance INTEGER NULL,                   -- int64 - OK
    match_round VARCHAR(20) NULL,                    -- Max length: 18
    match_home_team_goals INTEGER NULL,              -- int64 - OK
    match_home_team_behinds INTEGER NULL,            -- int64 - OK
    match_home_team_score INTEGER NULL,              -- int64 - OK
    match_away_team_goals INTEGER NULL,              -- int64 - OK
    match_away_team_behinds INTEGER NULL,            -- int64 - OK
    match_away_team_score INTEGER NULL,              -- int64 - OK
    match_margin INTEGER NULL,                       -- int64 - OK
    match_winner VARCHAR(100) NULL,                  -- Max length: 22
    match_weather_temp_c INTEGER NULL,               -- int64 - OK
    match_weather_type VARCHAR(50) NULL,             -- Max length: 13
    player_id INTEGER NULL,                          -- int64 - OK
    player_first_name VARCHAR(100) NULL,             -- Max length: 10
    player_last_name VARCHAR(100) NULL,              -- Max length: 19
    player_height_cm DECIMAL(5,1) NULL,              -- CHANGED: float64 with decimals
    player_weight_kg DECIMAL(5,1) NULL,              -- CHANGED: float64 with decimals  
    player_is_retired VARCHAR(10) NULL,              -- CHANGED: object with True/False/NULL
    player_team VARCHAR(100) NULL,                   -- Max length: 22
    guernsey_number INTEGER NULL,                    -- int64 - OK
    kicks INTEGER NULL,                              -- int64 - OK
    marks INTEGER NULL,                              -- int64 - OK
    handballs INTEGER NULL,                          -- int64 - OK
    disposals INTEGER NULL,                          -- int64 - OK
    effective_disposals DECIMAL(5,1) NULL,          -- CHANGED: float64
    disposal_efficiency_percentage INTEGER NULL,     -- int64 - OK
    goals INTEGER NULL,                              -- int64 - OK
    behinds INTEGER NULL,                            -- int64 - OK
    hitouts INTEGER NULL,                            -- int64 - OK
    tackles INTEGER NULL,                            -- int64 - OK
    rebounds INTEGER NULL,                           -- int64 - OK
    inside_fifties INTEGER NULL,                     -- int64 - OK
    clearances INTEGER NULL,                         -- int64 - OK
    clangers INTEGER NULL,                           -- int64 - OK
    free_kicks_for INTEGER NULL,                     -- int64 - OK
    free_kicks_against INTEGER NULL,                 -- int64 - OK
    brownlow_votes INTEGER NULL,                     -- int64 - OK
    contested_possessions INTEGER NULL,              -- int64 - OK
    uncontested_possessions INTEGER NULL,            -- int64 - OK
    contested_marks INTEGER NULL,                    -- int64 - OK
    marks_inside_fifty INTEGER NULL,                 -- int64 - OK
    one_percenters INTEGER NULL,                     -- int64 - OK
    bounces INTEGER NULL,                            -- int64 - OK
    goal_assists INTEGER NULL,                       -- int64 - OK
    time_on_ground_percentage INTEGER NULL,          -- int64 - OK
    afl_fantasy_score DECIMAL(6,1) NULL,            -- CHANGED: float64
    supercoach_score DECIMAL(6,1) NULL,             -- CHANGED: float64
    centre_clearances INTEGER NULL,                  -- int64 - OK
    stoppage_clearances INTEGER NULL,                -- int64 - OK
    score_involvements INTEGER NULL,                 -- int64 - OK
    metres_gained INTEGER NULL,                      -- int64 - OK
    turnovers INTEGER NULL,                          -- int64 - OK
    intercepts INTEGER NULL,                         -- int64 - OK
    tackles_inside_fifty INTEGER NULL,               -- int64 - OK
    contest_def_losses DECIMAL(5,1) NULL,           -- CHANGED: float64
    contest_def_one_on_ones DECIMAL(5,1) NULL,      -- CHANGED: float64
    contest_off_one_on_ones DECIMAL(5,1) NULL,      -- CHANGED: float64
    contest_off_wins DECIMAL(5,1) NULL,             -- CHANGED: float64
    def_half_pressure_acts DECIMAL(5,1) NULL,       -- CHANGED: float64
    effective_kicks DECIMAL(5,1) NULL,              -- CHANGED: float64
    f50_ground_ball_gets DECIMAL(5,1) NULL,         -- CHANGED: float64
    ground_ball_gets DECIMAL(5,1) NULL,             -- CHANGED: float64
    hitouts_to_advantage DECIMAL(5,1) NULL,         -- CHANGED: float64
    hitout_win_percentage DECIMAL(5,2) NULL,        -- CHANGED: float64 with 2 decimals
    intercept_marks DECIMAL(5,1) NULL,              -- CHANGED: float64
    marks_on_lead DECIMAL(5,1) NULL,                -- CHANGED: float64
    pressure_acts DECIMAL(5,1) NULL,                -- CHANGED: float64
    rating_points DECIMAL(6,2) NULL,                -- CHANGED: float64 with 2 decimals
    ruck_contests DECIMAL(6,1) NULL,                -- CHANGED: float64
    score_launches DECIMAL(5,1) NULL,               -- CHANGED: float64
    shots_at_goal INTEGER NULL,                     -- int64 - OK
    spoils DECIMAL(5,1) NULL,                       -- CHANGED: float64
    subbed VARCHAR(15) NULL,                        -- Max length: 10
    player_position VARCHAR(10) NULL,               -- Max length: 4
    date DATE NULL                                   -- Date string - OK
);

-- Create indexes for better query performance
CREATE INDEX idx_player_details_team_season ON player_details(team, season);
CREATE INDEX idx_player_details_surname ON player_details(surname);
CREATE INDEX idx_supercoach_prices_player_id ON supercoach_prices(player_id);
CREATE INDEX idx_supercoach_prices_team ON supercoach_prices(team);
CREATE INDEX idx_supercoach_prices_full_name ON supercoach_prices(full_name);
CREATE INDEX idx_supercoach_prices_scraped_date ON supercoach_prices(scraped_date);
CREATE INDEX idx_player_stats_player_id ON player_stats(player_id);
CREATE INDEX idx_player_stats_match_date ON player_stats(match_date);
CREATE INDEX idx_player_stats_team ON player_stats(player_team);
CREATE INDEX idx_player_stats_match_id ON player_stats(match_id);

-- Add comments for documentation
COMMENT ON TABLE player_details IS 'Player biographical and career information from 2015-2025';
COMMENT ON TABLE supercoach_prices IS 'AFL SuperCoach player pricing data scraped from FootyWire';
COMMENT ON TABLE player_stats IS 'Match-by-match player statistics from 2015-2025';
COMMENT ON COLUMN player_details.id IS 'Player identifier';
COMMENT ON COLUMN supercoach_prices.player_id IS 'References player_details.id for player linkage';
COMMENT ON COLUMN supercoach_prices.full_name IS 'Player full name parsed from FootyWire data';
COMMENT ON COLUMN supercoach_prices.team IS 'AFL team abbreviation';
COMMENT ON COLUMN supercoach_prices.scraped_date IS 'Date when the pricing data was scraped';
COMMENT ON COLUMN player_stats.player_id IS 'References player_details.id';
COMMENT ON COLUMN player_stats.match_id IS 'Unique match identifier';
