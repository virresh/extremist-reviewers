# Characterizing extremist reviewers on online reviews

This is the codebase to our paper submitted in the IEEE TCSS journal.

Amazon_Scraper deals with scraping reviews and reviewer profiles from Amazon.in, and some rudimentary visualisations and analysis on the gathered data.
- Categories/ : Contains the product categories and links to their results-pages, from which the scrape.py script begings fetching data.
- scrape.py: Scrapes reviews from categories.
- scrape_profile.py: Scrapes information for the reviewers associated with the reviews collected from the scrape.py script.

Final_Labels.csv contains the annotated data.
