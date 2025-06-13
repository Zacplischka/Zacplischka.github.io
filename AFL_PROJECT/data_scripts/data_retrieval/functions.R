# Helper functions for AFL data analysis

# Function to print recent matches in a clean format
print_recent_matches <- function(matches, n = 10) {
  if (nrow(matches) == 0) {
    cat("No recent matches found.\n")
    return()
  }
  
  # Check column names and handle different possible date column names
  date_col <- if("utcStartTime" %in% names(matches)) "utcStartTime" else if("date" %in% names(matches)) "date" else "Date"
  
  recent <- matches %>%
    arrange(desc(.data[[date_col]])) %>%
    head(n)
  
  for (i in 1:min(n, nrow(recent))) {
    match <- recent[i, ]
    home_team <- if("home.team.name" %in% names(match)) match$home.team.name else "TBA"
    away_team <- if("away.team.name" %in% names(match)) match$away.team.name else "TBA"
    home_score <- if("home.score.totalScore" %in% names(match)) match$home.score.totalScore else "TBA"
    away_score <- if("away.score.totalScore" %in% names(match)) match$away.score.totalScore else "TBA"
    venue <- if("venue.name" %in% names(match)) match$venue.name else "TBA"
    
    cat(sprintf("%s vs %s (%s - %s) at %s\n", 
                home_team, away_team, home_score, away_score, venue))
  }
}

# Function to get upcoming matches
get_upcoming_matches <- function(fixture, n = 5) {
  if (nrow(fixture) == 0) return(fixture)
  
  date_col <- if("utcStartTime" %in% names(fixture)) "utcStartTime" else if("date" %in% names(fixture)) "date" else "Date"
  
  upcoming <- fixture %>%
    filter(as.Date(.data[[date_col]]) > Sys.Date()) %>%
    arrange(.data[[date_col]]) %>%
    head(n)
  
  return(upcoming)
}

# Function to print upcoming matches
print_upcoming_matches <- function(matches) {
  if (nrow(matches) == 0) {
    cat("No upcoming matches found.\n")
    return()
  }
  
  for (i in 1:nrow(matches)) {
    match <- matches[i, ]
    home_team <- if("home.team.name" %in% names(match)) match$home.team.name else "TBA"
    away_team <- if("away.team.name" %in% names(match)) match$away.team.name else "TBA"
    venue <- if("venue.name" %in% names(match)) match$venue.name else "TBA"
    date_time <- if("utcStartTime" %in% names(match)) {
      format(as.POSIXct(match$utcStartTime), "%Y-%m-%d %H:%M")
    } else "TBA"
    round_name <- if("round.name" %in% names(match)) match$round.name else "TBA"
    
    cat(sprintf("%s: %s vs %s at %s (%s)\n", 
                round_name, home_team, away_team, venue, date_time))
  }
}

# Function to print ladder
print_ladder <- function(ladder, n = 8) {
  if (nrow(ladder) == 0) {
    cat("No ladder data found.\n")
    return()
  }
  
  top_teams <- ladder %>%
    arrange(position) %>%
    head(n)
  
  cat(sprintf("%-3s %-20s %3s %3s %3s %3s %6s %3s\n", 
              "Pos", "Team", "P", "W", "L", "D", "Pct", "Pts"))
  cat(rep("-", 60), "\n", sep = "")
  
  for (i in 1:nrow(top_teams)) {
    team <- top_teams[i, ]
    team_name <- if("team.name" %in% names(team)) team$team.name else "Unknown"
    played <- team$played
    wins <- if("thisSeasonRecord.winLossRecord.wins" %in% names(team)) team$thisSeasonRecord.winLossRecord.wins else 0
    losses <- if("thisSeasonRecord.winLossRecord.losses" %in% names(team)) team$thisSeasonRecord.winLossRecord.losses else 0
    draws <- if("thisSeasonRecord.winLossRecord.draws" %in% names(team)) team$thisSeasonRecord.winLossRecord.draws else 0
    percentage <- if("thisSeasonRecord.percentage" %in% names(team)) team$thisSeasonRecord.percentage else 0
    points <- if("thisSeasonRecord.aggregatePoints" %in% names(team)) team$thisSeasonRecord.aggregatePoints else 0
    
    cat(sprintf("%-3d %-20s %3d %3d %3d %3d %6.1f %3d\n",
                team$position, team_name, played, wins, losses, draws, percentage, points))
  }
}

# Function to create ladder visualization
create_ladder_plot <- function(ladder) {
  if (nrow(ladder) == 0) {
    cat("No ladder data available for plotting.\n")
    return()
  }
  
  # Use the correct column names from FitzRoy API
  if ("team.name" %in% names(ladder) && "thisSeasonRecord.aggregatePoints" %in% names(ladder)) {
    p <- ladder %>%
      arrange(position) %>%
      ggplot(aes(x = reorder(team.name, -position), y = thisSeasonRecord.aggregatePoints)) +
      geom_col(fill = "steelblue", alpha = 0.7) +
      theme_minimal() +
      theme(axis.text.x = element_text(angle = 45, hjust = 1, size = 8)) +
      labs(
        title = paste("AFL Ladder -", year(Sys.Date()), "Season"),
        x = "Team",
        y = "Points",
        caption = "Data from FitzRoy API"
      )
    
    print(p)
    
    # Save plot
    ggsave("afl_ladder.png", plot = p, width = 12, height = 8, dpi = 300)
    cat("\nLadder plot saved as 'afl_ladder.png'\n")
  } else {
    cat("Cannot create plot - required columns not found\n")
  }
}