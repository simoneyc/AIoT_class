# AIoT_class

老師要求作業必須要使用chatGPT

The teacher requires the homework to be completed using ChatGPT.


# LINE Bot for Travel Recommendations - project
***I am in Taichung***

A project designed to assist users in exploring Taichung's attractions, food, and snacks with LINE Bot integration and data scraping.

## Features

- **Web Scraping**: Extract data from Taichung's travel website and save it as CSV files.
- **LINE Bot Integration**: Interact with users to provide recommendations, weather updates, and more through LINE messages.
- **Database Integration**: Store and manage attraction data in MongoDB for seamless data retrieval.

## Project Structure

```
project
   ├── code
        ├── scrapying.py    # Scrapes data from the travel website and saves it as a CSV file
        ├── app.py          # Implements the LINE Bot server with Flask
        ├── db_csv.py       # Imports CSV data into MongoDB
```

## Requirements

- Python 3.8+
- MongoDB
- Flask
- LINE Bot SDK
- BeautifulSoup (bs4)

## Installation

1. Clone the repository:

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up your environment variables for LINE Bot:

    ```bash
    export CHANNEL_ACCESS_TOKEN=your_channel_access_token
    export CHANNEL_SECRET=your_channel_secret
    ```

4. Configure MongoDB:

    Update the MongoDB connection string in `db_csv.py` and `app.py` to match your setup.

## Usage

### Scrape Data
Run the scraper script to generate CSV files with attraction data:

```bash
python scrapying.py
```

### Import Data into MongoDB
Run the import script to load the scraped data into MongoDB:

```bash
python db_csv.py
```

### Start the LINE Bot Server
Run the Flask server to start the LINE Bot:

```bash
python app.py
```

## Acknowledgements

- Taichung Travel Website: [Source of data](https://travel.taichung.gov.tw/).

