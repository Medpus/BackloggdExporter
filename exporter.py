import csv
import requests
from bs4 import BeautifulSoup
import argparse


def fetch_profile_page(profile_url, page):
    try:
        paginated_url = f"{profile_url}?page={page}"
        response = requests.get(paginated_url)
        response.raise_for_status()  # Raise an error for HTTP errors

        soup = BeautifulSoup(response.content, "html.parser")
        game_entries = soup.select(
            ".rating-hover"
        )  # Adjust selector based on your analysis

        if not game_entries:
            return []

        return game_entries
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {page}: {e}")
        return []


def extract_game_data(game_entries):
    game_data = []
    for game_entry in game_entries:
        title_element = game_entry.select_one(".game-text-centered")
        title = title_element.get_text(strip=True) if title_element else "Unknown Title"

        stars_top_element = game_entry.select_one(".stars-top")
        if stars_top_element:
            style = stars_top_element.get("style", "")
            width = (
                style.split("width:")[1].split("%")[0].strip()
                if "width:" in style
                else "0"
            )
            try:
                rating = float(width) / 20
            except ValueError:
                rating = 0.0
        else:
            rating = 0.0

        game_data.append((title, rating))
    return game_data


def fetch_all_game_data(profile_url):
    all_game_data = []
    page = 1
    previous_page_data_hash = None

    while True:
        print(f"Fetching page {page}...")
        game_entries = fetch_profile_page(profile_url, page)

        current_page_data_hash = hash(tuple(game_entries)) if game_entries else None
        if not game_entries or current_page_data_hash == previous_page_data_hash:
            if not game_entries:
                print("No more game entries found. Stopping scraping.")
            elif current_page_data_hash == previous_page_data_hash:
                print("Duplicate page data found. Stopping scraping.")
            break

        game_data = extract_game_data(game_entries)
        all_game_data.extend(game_data)
        previous_page_data_hash = current_page_data_hash
        page += 1

    return all_game_data


def save_to_csv(username, game_data):
    filename = f"{username}_games.csv"
    print(f"Saving data to {filename}...")
    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Title", "Rating"])
            writer.writerows(game_data)
        print(f"Data saved to {filename}")
    except IOError as e:
        print(f"Error saving data to {filename}: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Scrape game data from a Backloggd profile and save to a CSV file."
    )
    parser.add_argument(
        "profile_url_or_username",
        type=str,
        help="Backloggd profile URL or username (e.g., https://backloggd.com/u/username/games/ or simply 'username')",
    )
    args = parser.parse_args()

    # Handle both URL and username input
    if args.profile_url_or_username.startswith("http"):
        profile_url = args.profile_url_or_username
        username = profile_url.split("/u/")[1].split("/")[0]
    else:
        username = args.profile_url_or_username
        profile_url = f"https://backloggd.com/u/{username}/games/"

    print(f"Scraping data for username: {username}")
    all_game_data = fetch_all_game_data(profile_url)
    save_to_csv(username, all_game_data)
