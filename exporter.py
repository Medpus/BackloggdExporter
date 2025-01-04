import csv
import requests
from bs4 import BeautifulSoup
import argparse

# Fetch the game entries from a specific profile page
def fetch_profile_page(profile_url, page):
    try:
        paginated_url = f"{profile_url}?page={page}"  # Append the page number to the profile URL
        response = requests.get(paginated_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        soup = BeautifulSoup(response.content, "html.parser")
        game_entries = soup.select(
            ".rating-hover"
        )  # Select all game entries with the "rating-hover" class

        if not game_entries:  # Check if no games are found on the page
            return []

        return game_entries
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {page}: {e}")
        return []

# Extract title and rating data from the fetched game entries
def extract_game_data(game_entries):
    game_data = []
    for game_entry in game_entries:
        # Extract game title
        title_element = game_entry.select_one(".game-text-centered")
        title = title_element.get_text(strip=True) if title_element else "Unknown Title"

        # Extract game rating from the style attribute
        stars_top_element = game_entry.select_one(".stars-top")
        if stars_top_element:
            style = stars_top_element.get("style", "")
            width = (
                style.split("width:")[1].split("%")[0].strip()
                if "width:" in style
                else "0"
            )
            try:
                rating = float(width) / 20  # Convert percentage width to a 5-star rating
            except ValueError:
                rating = 0.0
        else:
            rating = 0.0

        game_data.append((title, rating)) 
    return game_data

# Fetch all game data by iterating through pages until no new data is found
def fetch_all_game_data(profile_url):
    all_game_data = []
    page = 1
    previous_page_data_hash = None

    while True:
        print(f"Fetching page {page}...")
        game_entries = fetch_profile_page(profile_url, page)

        # Detect duplicate or empty pages to stop scraping
        current_page_data_hash = hash(tuple(game_entries)) if game_entries else None
        if not game_entries or current_page_data_hash == previous_page_data_hash:
            if not game_entries:
                print("No more game entries found. Stopping scraping.")
            elif current_page_data_hash == previous_page_data_hash:
                print("Duplicate page data found. Stopping scraping.")
            break

        game_data = extract_game_data(game_entries)
        all_game_data.extend(game_data)  # Add the extracted data to the result list
        previous_page_data_hash = current_page_data_hash
        page += 1

    return all_game_data

# Save the fetched game data to a CSV file
def save_to_csv(username, game_data):
    filename = f"{username}_games.csv"
    print(f"Saving data to {filename}...")
    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Title", "Rating"])  # Write the header row
            writer.writerows(game_data)  # Write the game data
        print(f"Data saved to {filename}")
    except IOError as e:
        print(f"Error saving data to {filename}: {e}")

if __name__ == "__main__":
    import argparse

    # Command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Scrape game data from a Backloggd profile and save to a CSV file."
    )
    parser.add_argument(
        "profile_url_or_username",
        type=str,
        help="Backloggd profile URL or username (e.g., https://backloggd.com/u/username/games/ or simply 'username')",
    )
    args = parser.parse_args()

    # Determine if input is a full URL or just a username
    if args.profile_url_or_username.startswith("http"):
        profile_url = args.profile_url_or_username
        username = profile_url.split("/u/")[1].split("/")[0]  # Extract username from the URL
    else:
        username = args.profile_url_or_username
        profile_url = f"https://backloggd.com/u/{username}/games/"  # Construct URL from the username

    print(f"Scraping data for username: {username}")
    all_game_data = fetch_all_game_data(profile_url) 
    save_to_csv(username, all_game_data)  # Save the data to a CSV file
