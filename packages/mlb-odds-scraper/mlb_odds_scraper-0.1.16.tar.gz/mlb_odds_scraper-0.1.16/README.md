# MLB Odds Scraper

A Python package for scraping MLB odds data from OddsPortal. This package provides tools to easily retrieve and analyze betting odds for MLB games.

## Installation

```bash
pip install mlb_odds_scraper
```

## Features

- Scrape historical MLB betting odds from OddsPortal
- Support for concurrent page scraping
- Clean and structured data output with team ID mapping
- Timezone handling (converts game times to UTC)
- Filters out All-Star games automatically
- Adaptive selectors to handle website structure changes
- Enhanced stealth mode to avoid detection

## Requirements

- Python >= 3.8
- Chrome/Chromium browser installed

## Dependencies

- pandas >= 1.0.0
- selenium >= 4.0.0
- stealthenium >= 0.1.0
- MLB-StatsAPI >= 1.0.0

## Usage

```python
from mlb_odds_scraper import scrape_oddsportal_mlb, scrape_oddsportal_mlb_years, process_game_data

# Scrape a single year
games = scrape_oddsportal_mlb(2024)  # Scrapes all pages for 2024
games = scrape_oddsportal_mlb(2024, max_pages=5)  # Scrape first 5 pages only

# Scrape multiple years
df = scrape_oddsportal_mlb_years(2020, 2024)  # Scrapes 2020-2023
df = scrape_oddsportal_mlb_years()  # Scrapes 2006-2024 (default)

# Process the scraped data
processed_df = process_game_data(df)
# Returns DataFrame with:
# - Parsed dates and times (UTC)
# - Team IDs from MLB-StatsAPI
# - Cleaned odds and scores
# - Removed All-Star games
```

## Changelog

### v0.1.2
- Added multiple selectors to handle website structure changes
- Improved error handling and robustness
- Enhanced stealth mode to avoid detection
- Added better date and time parsing
- Fixed issues with future year scraping

### v0.1.1
- Initial release

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 