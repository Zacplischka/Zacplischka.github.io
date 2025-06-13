# AFL Data Analysis - Main Script
# This script fetches recent AFL data using the FitzRoy API

# Load required libraries
library(fitzRoy)
library(dplyr)
library(ggplot2)
library(lubridate)

# Source helper functions
source("data_scripts/data_retrieval/functions.R")

# Get current season
current_year <- year(Sys.Date())

# fetch player details
tryCatch({
  player_details <- fetch_player_details(season = 2015:2025, current = FALSE)
  cat("\nPlayer Details:\n")
  print(head(player_details, 10))  # Print first 10 players
    write.csv(player_details, file = "data_scripts/data/player_details_afl_2015_2025.csv", row.names = FALSE)
}, error = function(e) {
  cat("Error fetching player details:", e$message, "\n")
})


# fetch player statistics for last 10 years
tryCatch({
  player_stats <- fetch_player_stats(source="fryzigg",
  comp = "AFLM"
    , season = 2015:2025,
  )
  cat("\nPlayer Statistics for Last 25 Years:\n")
  print(head(player_stats, 100))  # Print first 10 players
  write.csv(player_stats, file = "data_scripts/data/player_stats_afl_2015_2025.csv", row.names = FALSE)
}, error = function(e) {
  cat("Error fetching player statistics:", e$message, "\n")
})




