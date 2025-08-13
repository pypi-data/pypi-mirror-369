"""MLB Odds Scraper package for retrieving odds data from OddsPortal."""

from .scraper import (
    scrape_oddsportal_mlb,
    scrape_oddsportal_mlb_years,
    process_game_data,
    clean_game_data
)

__version__ = "0.1.18"

__all__ = [
    "scrape_oddsportal_mlb",
    "scrape_oddsportal_mlb_years",
    "process_game_data",
    "clean_game_data"
] 