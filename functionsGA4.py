from bs4 import BeautifulSoup
import requests
import json
import re
from urllib.parse import urlencode
import pandas as pd
from datetime import datetime
from geopy.geocoders import Nominatim
from xml.etree import ElementTree as ET
import datetime
import os
import tabula

# Your GitHub personal access token (Replace with a valid token)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

# ---------------------------------- GA 4.1 --------------------------------------- #

def extract_page_name(question):
    """Extracts the page name from the given question using regex."""

    # Match the page number after "page number"
    page_number_match = re.search(r"page number (\d+)", question, re.IGNORECASE)
    page_number = page_number_match.group(1) if page_number_match else None

    return page_number

def fetch_page_content_GA41(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch page content: {response.status_code}")

def parse_ducks_from_table(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find_all('table', class_='engineTable')[2]
    if not table:
        raise Exception("Could not find the statistics table on the page.")
    # print(table[2])
    ducks_column_index = None
    headers = table.find_all('th')
    for index, header in enumerate(headers):
        if header.text.strip() == '0':
            ducks_column_index = index
            break

    if ducks_column_index is None:
        raise Exception("Could not find the '0' (ducks) column in the table.")

    total_ducks = 0
    rows = table.find_all('tr', class_='data1')
    for row in rows:
        columns = row.find_all('td')
        if len(columns) > ducks_column_index:
            ducks_value = columns[ducks_column_index].text.strip()
            try:
                total_ducks += int(ducks_value)
            except ValueError:
                continue

    return total_ducks

def find_no_of_ducks(question_text):
    page_no = extract_page_name(question_text)
    url = f"https://stats.espncricinfo.com/stats/engine/stats/index.html?class=2;page={page_no};template=results;type=batting"
    html_content = fetch_page_content_GA41(url)
    total_ducks = parse_ducks_from_table(html_content)
    return str(total_ducks)

# ---------------------------------- GA 4.2 --------------------------------------- #

def extract_ques_GA42(question):
    # Extract rating range
    rating_match = re.search(r"rating between (\d+) and (\d+)", question)
    min_rating, max_rating = rating_match.groups() if rating_match else (None, None)

    # Extract number of movies
    movies_match = re.search(r"up to the first (\d+) titles", question)
    num_movies = movies_match.group(1) if movies_match else None

    return int(min_rating), int(max_rating), int(num_movies)

def fetch_page_content_GA42(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch page content: {response.status_code}")

def extract_movie_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    movie_list = []
    for movie in soup.find_all('li', class_='ipc-metadata-list-summary-item'):
        title_element = movie.find('h3', class_='ipc-title__text')
        if title_element:
            title = title_element.text
            year = movie.find('span', class_='dli-title-metadata-item').text.strip()

            rating_element = movie.find('span', class_='ipc-rating-star--rating')
            if rating_element:
                rating = rating_element.text

                href_element = movie.a.get('href')
                if href_element:
                    movie_id = href_element.split('/')[2]
                    movie_data = {
                        "id": movie_id,
                        "title": title,
                        "year": year,
                        "rating": rating
                    }
                    movie_list.append(movie_data)
    return movie_list

def IMDB_seacrching(question):
    min_rating, max_rating, num_movies = extract_ques_GA42(question)
    base_url = f"https://www.imdb.com/search/title/?user_rating={min_rating},{max_rating}"
    html_content = fetch_page_content_GA42(base_url)
    movie_list = extract_movie_data(html_content)
    # extract_movie_data(html_content)

    filtered_movies = []
    for movie in movie_list:
        try:
            rating = float(movie['rating'])
            if min_rating <= rating <= max_rating:
                filtered_movies.append(movie)
        except ValueError:
            pass

    return json.dumps(filtered_movies[:num_movies], indent=4)
    
# ---------------------------------- GA 4.3 --------------------------------------- #

def wikipedia_search():
    return "https://sample-ct67.onrender.com/api/outline"

# ---------------------------------- GA 4.4 --------------------------------------- #

def extract_city_name(question):
    """Extracts the city name from the given question using regex."""

    # Match city name after "for"
    city_match = re.search(r"description for (\w+)", question, re.IGNORECASE)
    city_name = city_match.group(1) if city_match else None

    return city_name

def fetch_weather_data(location_url):
    # Fetch location data
    result = requests.get(location_url).json()
    weather_url = 'https://www.bbc.com/weather/' + result['response']['results']['results'][0]['id']

    # Fetch weather data
    response = requests.get(weather_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    daily_summary = soup.find('div', attrs={'class': 'wr-day-summary'})
    daily_summary_list = re.findall('[a-zA-Z][^A-Z]*', daily_summary.text)


    # Generate date list
    datelist = pd.date_range(datetime.today(), periods=len(daily_summary_list)).tolist()
    datelist = [date.date().strftime('%Y-%m-%d') for date in datelist]


    # Map dates to descriptions
    weather_data = {date: desc for date, desc in zip(datelist, daily_summary_list)}

    # Convert to JSON
    weather_json = json.dumps(weather_data, indent=4)
    return weather_json

def bbc_weather_fetching(question_text):
    required_city = extract_city_name(question_text)
    location_url = 'https://locator-service.api.bbci.co.uk/locations?' + urlencode({
        'api_key': 'AGbFAKx58hyjQScCXIYrxuEwJh2W2cmv',
        's': required_city,
        'stack': 'aws',
        'locale': 'en',
        'filter': 'international',
        'place-types': 'settlement,airport,district',
        'order': 'importance',
        'a': 'true',
        'format': 'json'
    })
    weather_json = fetch_weather_data(location_url)
    return json.dumps(weather_json)

# ---------------------------------- GA 4.5 --------------------------------------- #

def extract_city_country(question):
    # Extract city name
    city_match = re.search(r"the city (\w+)", question)
    city_name = city_match.group(1) if city_match else None

    # Extract country name
    country_match = re.search(r"the country (\w+)", question)
    country_name = country_match.group(1) if country_match else None
    return city_name, country_name

def find_bounding_box(question):
    city, country = extract_city_country(question)
    location = f"{city}, {country}"
    # Activate the Nominatim geocoder
    locator = Nominatim(user_agent="myGeocoder")

    # Geocode the city Mexico City in Mexico
    location = locator.geocode(location)

    # Check if the location was found
    if location:
        # Retrieve the bounding box
        bounding_box = location.raw.get('boundingbox', [])

        # Check if the bounding box is available
        if len(bounding_box) > 1:
            # Extract the minimum latitude from the bounding box (the first value in the list)
            min_latitude = bounding_box[0]
            return min_latitude
        else:
            print("Bounding box information not available.")
    else:
        print("Location not found.")

# ---------------------------------- GA 4.6 --------------------------------------- #

def extract_params_GA46(question):
    # Extract topic
    topic_match = re.search(r'mentioning (.*?) and', question)
    topic = topic_match.group(1) if topic_match else None

    # Extract minimum points
    points_match = re.search(r'minimum of (\d+) points', question)
    min_points = int(points_match.group(1)) if points_match else None

    # Extract relevant tag
    tags_match = re.findall(r'<(.*?)>', question)
    tags = tags_match if tags_match else None

    return topic, min_points, tags

def get_latest_hn_post_with_keywords_and_points(question):
    keywords, min_points, tags = extract_params_GA46(question)
    print(keywords, min_points, tags)
    keywords = keywords.split()
    if not tags:
        tags = ['item', 'link']
    # Fetches the latest Hacker News post mentioning specific keywords and having a minimum number of points.
    url = "https://hnrss.org/newest?q=" + '+'.join(keywords) + "&points=" + str(min_points)
    response = requests.get(url)

    if response.status_code == 200:
      root = ET.fromstring(response.content)
      # items = root.findall(".//item")
      items = root.findall(f".//{tags[0]}")
      # print(items)
      if items:
        latest_item = items[0]
        link = latest_item.find(tags[1]).text
        return str(link)
    return None

# ---------------------------------- GA 4.7 --------------------------------------- #

def extract_parameters_GA47(question):
    """Extracts the city name and number of followers from the given question using regex."""

    # Match city name after "in the city"
    city_match = re.search(r"in the city (\w+)", question, re.IGNORECASE)
    city_name = city_match.group(1) if city_match else None

    # Match follower count after "over"
    followers_match = re.search(r"over (\d+)", question)
    followers_count = int(followers_match.group(1)) if followers_match else None

    return city_name, followers_count

def search_users(location, followers):
    url = f"https://api.github.com/search/users?q=location:{location}+followers:>{followers}&sort=joined&order=desc"
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get('items', [])
    else:
        print(f"Error: {response.status_code} - {response.json().get('message')}")
        return []

def get_user_details(question_text):
    city, followers = extract_parameters_GA47(question_text)
    users = search_users(city, followers)

    # Get the current local date and time
    current_local_datetime = datetime.datetime.now()

    # Subtract 5 minutes to set the cutoff time
    cutoff_datetime = current_local_datetime - datetime.timedelta(minutes=5)

    # Process the first valid user who is not ultra-new
    for user in users:
        user_url = user['url']  # Get the profile API URL
        headers = {'Authorization': f'token {GITHUB_TOKEN}'}
        user_response = requests.get(user_url, headers=headers)

        if user_response.status_code == 200:
            user_data = user_response.json()
            created_at = user_data['created_at']  # ISO 8601 format
            created_at_date = datetime.datetime.fromisoformat(created_at[:-1])  # Convert to datetime

            # Check if the user is NOT ultra-new (joined more than 5 minutes ago)
            if created_at_date < cutoff_datetime:
                return str(created_at)
        else:
            print(f"Error fetching user details: {user_response.status_code}")
            return str(user_response.status_code)

# ---------------------------------- GA 4.8 --------------------------------------- #

def scriping_with_github_action():
    return "https://github.com/abhijit1458/Sheduled-Scraping"

# ---------------------------------- GA 4.9 --------------------------------------- #

def extract_parameters_GA49(question):
    """Extracts the required parameters from the given question using regex."""

    # Extract asked subject name (Physics)
    asked_subject_match = re.search(r"total\s+(\w+)\s+marks", question, re.IGNORECASE)
    asked_subject = asked_subject_match.group(1) if asked_subject_match else None

    # Extract condition subject name (Biology)
    condition_subject_match = re.search(r"scored\s+\d+\s+or\s+more\s+marks\s+in\s+(\w+)", question, re.IGNORECASE)
    condition_subject = condition_subject_match.group(1) if condition_subject_match else None

    # Extract score criteria (18 or more marks)
    score_criteria_match = re.search(r"scored\s+(\d+\s+or\s+more\s+marks)", question, re.IGNORECASE)
    score_criteria = score_criteria_match.group(1) if score_criteria_match else None

    # Extract group range (1-34)
    group_match = re.search(r"groups\s+(\d+-\d+)", question, re.IGNORECASE)
    group_range = group_match.group(1) if group_match else None

    params = {
        "Asked Subject": asked_subject,
        "Condition Subject": condition_subject,
        "Score Criteria": score_criteria,
        "Group Range": group_range
    }
    return params

def extract_table_from_pdf(question_text, pdf_path):
    params = extract_parameters_GA49(question_text)
    asked_subject = params["Asked Subject"]
    condition_subject = params["Condition Subject"]
    score_criteria = params["Score Criteria"]
    group_range = params["Group Range"].split("-")
    check_score = int(score_criteria.split()[0])

    # Extract tables from the PDF, specifying pages and multiple_tables=True
    tables = tabula.read_pdf(pdf_path, pages="all", multiple_tables=True)

    # Initialize an empty list to store all DataFrames
    all_dfs = []

    # Iterate through each table and add a "Group" column based on the page number
    for i, table in enumerate(tables):
        # Add a "Group" column to the table
        table["Group"] = i + 1  # Group 1 for Page 1, Group 2 for Page 2, etc.
        # Append the table to the list
        all_dfs.append(table)

    # Combine all DataFrames into a single DataFrame
    df = pd.concat(all_dfs, ignore_index=True)

    # Rename columns for easier access (if necessary)
    df.columns = ["Maths", "Physics", "English", "Economics", "Biology", "Group"]

    # Convert marks to numerical data types
    df["Maths"] = pd.to_numeric(df["Maths"], errors="coerce")
    df["Physics"] = pd.to_numeric(df["Physics"], errors="coerce")
    df["English"] = pd.to_numeric(df["English"], errors="coerce")
    df["Economics"] = pd.to_numeric(df["Economics"], errors="coerce")
    df["Biology"] = pd.to_numeric(df["Biology"], errors="coerce")
    df["Group"] = pd.to_numeric(df["Group"], errors="coerce")

    # Drop rows with missing values (if any)
    df.dropna(inplace=True)

    if "more marks" not in score_criteria:
        filtered_df = df[(df[condition_subject] <= check_score) & (df["Group"].between(int(group_range[0]), int(group_range[1])))]
    else:
        filtered_df = df[(df[condition_subject] >= check_score) & (df["Group"].between(int(group_range[0]), int(group_range[1])))]

    total_asked_marks = filtered_df[asked_subject].sum()
    return str(total_asked_marks)

# ---------------------------------- GA 4.10 --------------------------------------- #

def extract_markdown_pdf():
    return """
# Deludo tactus

[volutabrum cicuta](https://rubbery-lay.net)

#### Ver conatus velociter sint compello

[argumentum vilitas](https://eminent-bowler.biz)

> Synagoga adulatio cultellus adhuc arguo addo vilis vitiosus aptus.

[assumenda infit](https://heavy-opera.net)

```javascript
Decumbo damno adaugeo abeo corrumpo adipisci coerceo.
Sperno capio demum vobis verto.
Reiciendis attonbitus amet hic alioqui.
Totam uter summopere itaque ustilo.


- cedo tenetur adversus stillicidium ademptio
- subvenio convoco tamquam terebro
- virgo corporis ultra totus
- stultus volutabrum

> Cometes peccatus uredo verto agnitio.

- amplitudo vigor vomer vado
- demitto aro depopulo calamitas ulciscor
- demonstro ocer annus tergiversatio
- adiuvo absconditus tergiversatio tergeo ex
- auctor nesciunt currus aeger arcesso

##### Vaco correptius vito corroboro caput itaque

Ocer consuasor thymum cognomen. Adiuvo stella tutis calco dens. Vere similique comminor congregatio appono cetera creo aegre.

> Capillus stipes careo perferendis totam patria.

| demoror | venustas | defluo       | ipsam    |
| :--------- | :--------- | :---------- | :------- |
| ut            | nesciunt  | dolor        | tracto   |
| vapulus   | excepturi | succurro     | sono     |
| spargo    | speculum  | desparatus   | combibo  |
| copiose  | cohibeo   | voluptatibus | abundans |

> Pariatur auctus stillicidium astrum virga nobis curo cupiditas.

- quae amplus maiores expedita crebro
- volutabrum corona vallum
- patrocinor vestrum suscipit
- audax votum
- audentia decimus tonsor ubi sophismata

[tubineus vindico](https://exotic-coast.net/)

#### Depereo vindico defaeco

> Autus volubilis altus minima temporibus deinde considero antea valeo color.

[voluptatem creator](https://subtle-event.net/)

Sit tracto careo. Uterque vomer vindico autus spargo. Tantum depono alienus stipes campana ut autus.

Caste tero ara. Tersus coaegresco dolore pectus crinis tenus. Tubineus antiquus decerno coniecto correptius adhaero verumtamen cohors amissio.

Voro terra thema deputo cunctatio tenus illo. Harum terminatio sulum. Eius peccatus veniam audentia approbo aeneus alius torrens cognomen.

Vobis voluntarius uterque pecto corpus expedita decimus. Compono clibanus creo coepi contabesco. Cruciamentum anser triduana stella.

```javascript
Commodi tametsi subiungo aureus cotidie sumptus.
Creber vilicus vetus.
Bos adficio clam vestigium certe conculco.
Cur degero vigilo ulciscor atrocitas conitor acidus illum ager.
```

```bash
Nemo tondeo architecto comparo curatio abbas.
Volaticus aiunt ipsa.
Congregatio vesica sumptus degusto suspendo tametsi solus.
```

## Illo campana bis decerno

| Elementum | Descriptio |
|-----------|------------|
| Aqua      | Fluida vitalis necessaria |
| Ignis     | Energia et calor generans |
| Terra     | Fundamentum stabilitatis |
| Aer       | Motus et respiratio |

### Additional Lists

- Caelum serenum est
- Mare tranquillum manet
- Arboribus virentibus decoratur
- Avium cantus delectat

1. Initium novum
2. Processus iterabilis
3. Finis certus
4. Reditus ad originem
    """

# ------------------------------------ END ----------------------------------------- #