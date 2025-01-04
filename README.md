# Backloggd Scraper

This Python script scrapes titles and game ratings from a [Backloggd](https://backloggd.com/) user’s profile and saves them into a CSV file.  
It uses [requests](https://pypi.org/project/requests/) to fetch the HTML pages, [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) to parse the HTML, and writes the output to a CSV file.

## Prerequisites

- Python 3.6 or higher
- The following Python libraries:
  - `requests`
  - `beautifulsoup4`

You can install them via:

```bash
pip install requests beautifulsoup4
```

## Usage

1. Clone or download this repository:

```bash
git clone https://github.com/<medhus>/backloggd-exporter.git
```

2. Open a terminal in the project directory
3. Run the script with one of the following inputs:

- Backloggd profile URL (full)
- Username only

### Examples

- Using a full profile URL:
  ```bash
  python exporter.py https://backloggd.com/u/username/games/
  ```
- Using username:
  ```bash
  python exporter.py username
  ```

## Output

A CSV file named <username>\_games.csv will be created in the current directory.
The file will have the following strucure:
| Title | Rating |
| -------------- | ------ |
| Game Title #1 | 4.0 |
| Game Title #2 | 3.5 |
| ... | ... |

## License

This project is licensed under the MIT License.

Disclaimer: This tool is not affiliated with or endorsed by Backloggd. Use it responsibly and respect the website's terms of use.
