# Install required packages for AFL data analysis

# Set CRAN mirror
options(repos = c(CRAN = "https://cloud.r-project.org/"))

# Check if packages are installed, if not install them
required_packages <- c("fitzRoy", "dplyr", "ggplot2", "lubridate", "readr")

install_if_missing <- function(package) {
  if (!require(package, character.only = TRUE, quietly = TRUE)) {
    cat("Installing", package, "...\n")
    install.packages(package)
    library(package, character.only = TRUE)
    cat(package, "installed successfully!\n")
  } else {
    cat(package, "already installed.\n")
  }
}

cat("Installing required packages...\n")
sapply(required_packages, install_if_missing)
cat("All packages ready!\n")