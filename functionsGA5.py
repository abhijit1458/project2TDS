from fuzzywuzzy import fuzz, process
from datetime import datetime
from io import BytesIO
from PIL import Image
import pandas as pd
import subprocess
import whisper
import base64
import json
import gzip
import os
import re



# ---------------------------------- GA 5.1 --------------------------------------- #

def convert_to_datetime(date):
    for fmt in ("%m-%d-%Y", "%Y/%m/%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(date), fmt)
        except ValueError:
            continue
    return pd.NaT

def extract_info_GA51(ques):
    # Regex patterns
    date_pattern = re.search(r"(\w{3} \w{3} \d{1,2} \d{4})", ques)
    time_pattern = re.search(r"(\d{2}:\d{2}:\d{2})", ques)
    country_pattern = re.search(r"sold in\s+([A-Z]{2,3})\b", ques)
    product_pattern = re.search(r"for (\w+) sold", ques)

    # Extracted values
    date = date_pattern.group(1) if date_pattern else None
    time = time_pattern.group(1) if time_pattern else None
    country_code = country_pattern.group(1) if country_pattern else None
    product_code = product_pattern.group(1) if product_pattern else None

    return date, time, country_code, product_code

def process_excel_file(ques_text, file_bytes):
    date_str, time, country_code, pro_code = extract_info_GA51(ques_text)

    # Load the Excel file
    df = pd.read_excel(BytesIO(file_bytes))

    # Standardize Country Names
    country_mapping = {
        "USA": "US", "U.S.A": "US", "UNITED STATES": "US", "US": "US",
        "BRA": "BR", "BRAZIL": "BR", "BR": "BR",
        "U.K": "GB", "UK": "GB", "UNITED KINGDOM": "GB",
        "FR": "FR", "FRA": "FR", "FRANCE": "FR",
        "IND": "IN", "INDIA": "IN",
        "AE": "UAE", "U.A.E": "UAE", "UNITED ARAB EMIRATES": "UAE", "UAE": "UAE"
    }
    df['Country'] = df['Country'].str.strip().str.upper().replace(country_mapping)


    df['Date'] = df['Date'].apply(convert_to_datetime)

    # Extract Product Name before "/"
    df['Product'] = df['Product/Code'].astype(str).str.split('/').str[0].str.strip()

    # Clean and Convert Sales & Cost
    df['Sales'] = df['Sales'].astype(str).str.replace("USD", "").str.strip().astype(float)
    df['Cost'] = df['Cost'].astype(str).str.replace("USD", "").str.strip()

    # Handle missing Cost (50% of Sales if missing)
    df['Cost'] = pd.to_numeric(df['Cost'], errors='coerce')
    df['Cost'] = df['Cost'].fillna(df['Sales'] * 0.5)

    # Filter Data (Before Specified Date, Product = "Eta", Country = "FR")
    date_str = "Sat Nov 25 2023"
    date_obj = datetime.strptime(date_str, "%a %b %d %Y")
    formatted_date = [int(date) for date in date_obj.strftime("%Y-%m-%d").split("-")]
    formatted_time = [int(t) for t in time.split(":")]

    date_filter = datetime(formatted_date[0], formatted_date[1], formatted_date[2], formatted_time[0], formatted_time[1], formatted_time[2])
    df_filtered = df[
        (df['Date'] <= date_filter) &
        (df['Product'].str.lower() == pro_code.lower()) &
        (df['Country'] == country_code)
    ]

    # Calculate Total Margin
    total_sales = df_filtered['Sales'].sum()
    total_cost = df_filtered['Cost'].sum()
    total_margin = (total_sales - total_cost) / total_sales if total_sales > 0 else 0

    # Return results
    return str(round(total_margin, 4))

# ---------------------------------- GA 5.2 --------------------------------------- #

def extract_student_ids(file_bytes):
    # Read file as a text string
    file_content = BytesIO(file_bytes).read().decode("utf-8")
    
    # Ensure file is not empty
    if not file_content.strip():
        raise ValueError("The uploaded text file is empty.")
    
    # Extract student IDs using regex (assuming 10-character alphanumeric IDs)
    student_ids = set(re.findall(r'\b[A-Z0-9]{10}\b', file_content))
    
    # Return count of unique student IDs
    return str(len(student_ids))

# ---------------------------------- GA 5.3 --------------------------------------- #

def extract_info_GA53(text):
    pattern = r'pages under\s+(/[\w\-/_.]+).*?from\s+(\d{1,2}):\d{2}.*?before\s+(\d{1,2}):\d{2}.*?on\s+(\w+)'
    match = re.search(pattern, text, re.IGNORECASE)
    
    if match:
        file_name = match.group(1)  # Extracts the file path (e.g., /tamilmp3/)
        start_time = match.group(2)  # Extracts the start hour (e.g., 10)
        end_time = match.group(3)    # Extracts the end hour (e.g., 15)
        day = match.group(4)         # Extracts the day (e.g., Sunday)

        file_name = file_name.strip("/")
        day = day.rstrip('s')
        return file_name, int(start_time), int(end_time), day
    
    return None

def parse_log_line(line):
    log_pattern = (r'^(\S+) (\S+) (\S+) \[(.*?)\] "(\S+) (.*?) (\S+)" (\d+) (\S+) "(.*?)" "(.*?)" (\S+) (\S+)$')
    match = re.match(log_pattern, line)
    if match:
        return {
            "ip": match.group(1),
            "time": match.group(4),
            "method": match.group(5),
            "url": match.group(6),
            "protocol": match.group(7),
            "status": int(match.group(8)),
            "size": int(match.group(9)) if match.group(9).isdigit() else 0,
            "referer": match.group(10),
            "user_agent": match.group(11),
            "vhost": match.group(12),
            "server": match.group(13)
        }
    return None

def load_logs(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return pd.DataFrame()

    parsed_logs = []
    with gzip.open(file_path, 'rt', encoding='utf-8') as f:
        for line in f:
            parsed_entry = parse_log_line(line)
            if parsed_entry:
                parsed_logs.append(parsed_entry)
    return pd.DataFrame(parsed_logs)

def convert_time(timestamp):
    return datetime.strptime(timestamp, "%d/%b/%Y:%H:%M:%S %z")

def process_logs_GA53(query, file_path):
    file_name, start_time, end_time, day = extract_info_GA53(query)
    df = load_logs(file_path)

    if not df.empty:
        df["datetime"] = df["time"].apply(convert_time)
        df["day_of_week"] = df["datetime"].dt.strftime('%A')
        df["hour"] = df["datetime"].dt.hour

        # Filter conditions
        filtered_df = df[
            (df["method"] == "GET") &
            (df["url"].str.startswith(f"/{file_name}/")) &
            (df["status"] >= 200) & (df["status"] < 300) &
            (df["day_of_week"] == day) &
            (df["hour"] >= start_time) &
            (df["hour"] < end_time)
        ]

        # Output the count and hash
        return str(len(filtered_df))
    else:
        print("No log data available for processing.")

# ---------------------------------- GA 5.4 --------------------------------------- #

def extract_info_GA54(query):
  # Extract URL path (under `/carnatic/`)
  url_pattern = r"under\s+(\w+)(?=/)"
  url_match = re.search(url_pattern, query)
  url = url_match.group(1) if url_match else None

  # Extract date
  date_pattern = r"on\s+(\d{4}-\d{2}-\d{2})"
  date_match = re.search(date_pattern, query)
  date = date_match.group(1) if date_match else None

  return url, date

def process_logs_GA54(query, file_path):
    # Extract URL and date from the query
    url, date = extract_info_GA54(query)
    df = load_logs(file_path)

    if not df.empty:
        df["datetime"] = df["time"].apply(convert_time)
        df["date"] = df["datetime"].dt.strftime('%Y-%m-%d')

        # Filter conditions for /hindimp3/ on 2024-05-16
        filtered_df = df[
            (df["url"].str.startswith(f"/{url}/")) &
            (df["date"] == date)
        ]

        # Aggregate data by IP
        ip_data = filtered_df.groupby("ip")["size"].sum().reset_index()

        # Identify the top data consumer
        top_ip = ip_data.loc[ip_data["size"].idxmax()]
        return str(top_ip['size'])
    else:
        print("No log data available for processing.")

# ---------------------------------- GA 5.5 --------------------------------------- #

known_cities = ["São Paulo", "Jakarta", "Tokyo", "London", "Paris", "Beijing", "Shanghai", "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Karachi", "Lagos", "Kinshasa", "Cairo", "Istanbul", "Mexico City", "Buenos Aires", "Rio de Janeiro"]

def extract_info_GA55(text):
  # Extract product name
  product_pattern = r"units of (\w+)"
  product_match = re.search(product_pattern, text)
  product_name = product_match.group(1) if product_match else None

  # Extract city name
  city_pattern = r"in ([A-Za-zÀ-ÿ\s]+) on"
  city_match = re.search(city_pattern, text)
  city_name = city_match.group(1) if city_match else None

  # Extract number of units
  units_pattern = r"at least (\d+)"
  units_match = re.search(units_pattern, text)
  units_sold = int(units_match.group(1)) if units_match else None

  return product_name, city_name.lower(), units_sold

def cluster_cities(city_series):
    city_series = city_series.fillna('Unknown')

    def get_closest_city(city_name):
        best_match = process.extractOne(city_name, known_cities, scorer=fuzz.token_set_ratio)
        if best_match and best_match[1] > 75:  # Adjusted threshold
            return best_match[0]
        return city_name

    city_series = city_series.apply(get_closest_city)
    return city_series

def process_sales_data(ques_text, file_bytes):
    product_name, city_name, units_sold = extract_info_GA55(ques_text)
    data = json.loads(BytesIO(file_bytes).read().decode("utf-8"))
    df = pd.DataFrame(data)
    # Standardize city names
    df['city'] = cluster_cities(df['city'])

    # Filter sales for Hat with at least 44 units
    df_filtered = df[(df['product'] == product_name) & (df['sales'] >= units_sold)]

    # Aggregate sales by city
    df_grouped = df_filtered.groupby("city")["sales"].sum().reset_index()

    # Find sales for São Paulo
    city_sales = df_grouped[df_grouped["city"].str.lower() == city_name]["sales"].sum()

    return str(city_sales)

# ---------------------------------- GA 5.6 --------------------------------------- #

def process_jsonl_file(file_path):
  # Initialize total sales variable
  total_sales = 0

  # Regex pattern to extract sales values from invalid lines
  sales_pattern = re.compile(r'"sales"\s*:\s*([\d.]+)')

  # Read the JSONL file and sum sales values
  with open(file_path, "r") as file:
      for line in file:
          try:
              # Try parsing the line as JSON
              data = json.loads(line)
              if "sales" in data and isinstance(data["sales"], (int, float)):
                  total_sales += data["sales"]
          except json.JSONDecodeError:
              # If JSON parsing fails, extract sales value using regex
              match = sales_pattern.search(line)
              if match:
                total_sales += int(match.group(1))
  return str(total_sales)

# ---------------------------------- GA 5.7 --------------------------------------- #

def extract_info_GA57(question):

  # Regex pattern to extract the key
  pattern = r"\b([A-Z])\b(?=.* key)"

  # Search for the key
  match = re.search(pattern, question)

  # Extracted key
  key_name = match.group(1) if match else None

  # Print the extracted key
  print(f"Extracted Key: {key_name}")
  return key_name

def count_key_occurrences(data, target_key="S"):
    """Recursively count occurrences of a specific key in a nested JSON structure."""
    count = 0

    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:  # Count only if it's a key
                count += 1
            count += count_key_occurrences(value, target_key)  # Recursive call

    elif isinstance(data, list):
        for item in data:
            count += count_key_occurrences(item, target_key)  # Recursive call for lists

    return count

def find_key_occurrences(question, file_bytes):
    key = extract_info_GA57(question)
    # Read the JSON file
    json_data = json.loads(BytesIO(file_bytes).read().decode("utf-8"))
    
    key_count = count_key_occurrences(json_data, key)
    return str(key_count)

# ---------------------------------- GA 5.8 --------------------------------------- #

def extract_info_GA58(question):
  # Regex patterns
  datetime_pattern = r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)"  # Extracts ISO 8601 datetime
  comments_pattern = r"at least (\d+) comment"  # Extracts minimum number of comments
  stars_pattern = r"(\d+) useful stars"  # Extracts number of useful stars
  column_pattern = r"column called (\w+)"  # Extracts column name

  # Extract values using regex
  datetime_match = re.search(datetime_pattern, question)
  comments_match = re.search(comments_pattern, question)
  stars_match = re.search(stars_pattern, question)
  column_match = re.search(column_pattern, question)

  # Assign extracted values
  datetime_stamp = datetime_match.group(1) if datetime_match else None
  num_comments = int(comments_match.group(1)) if comments_match else None
  num_stars = int(stars_match.group(1)) if stars_match else None
  column_name = column_match.group(1) if column_match else None

  return datetime_stamp, int(num_stars), int(num_comments), column_name

def find_posts(question):
    datetime_stamp, num_stars, num_comments,  column_name = extract_info_GA58(question)
    if num_comments is None:
        num_comments = 1
    if column_name is None:
        column_name = 'post_id'
    # SQL query
    query = f"""
SELECT {column_name}
FROM (
    SELECT {column_name}
    FROM (
        SELECT {column_name},
            json_extract(comments, '$[*].stars.useful') AS useful_stars
        FROM social_media
        WHERE timestamp >= '{datetime_stamp}'
    )
    WHERE EXISTS (
        SELECT {num_comments} FROM UNNEST(useful_stars) AS t(value)
        WHERE CAST(value AS INTEGER) >= {num_stars}
    )
)
ORDER BY {column_name};
    """
    return json.dumps(query)

# ---------------------------------- GA 5.9 --------------------------------------- #

def extract_video_info(text):
    pattern = r"(https?://[^\s]+)\s+between\s+([\d.]+)\s+and\s+([\d.]+)"
    match = re.search(pattern, text)
    
    if match:
        link = match.group(1)
        start_time = (match.group(2).rstrip("."))
        end_time = (match.group(3).rstrip("."))
        return link, start_time, end_time
    else:
        pattern = r"between\s+([\d.]+)\s+and\s+([\d.]+)"
        match = re.search(pattern, text)
        start_time = (match.group(1).rstrip("."))
        end_time = (match.group(2).rstrip("."))
        return None, start_time, end_time

def transcribe_segment(question, file_path=None):
    youtube_url, start_time, end_time = extract_video_info(question)
    if youtube_url != None:
        # Download audio using yt-dlp
        audio_file = "mystery_story.mp3"
        subprocess.run(["yt-dlp", "-x", "--audio-format", "mp3", "-o", audio_file, youtube_url])

        # Trim the audio using FFmpeg (Extract segment 313.6s to 381.7s)
        trimmed_audio = "trimmed_audio.mp3"
        subprocess.run(["ffmpeg", "-i", audio_file, "-ss", start_time, "-to", end_time, "-c:a", "copy", trimmed_audio])
    if file_path != None:
        # Define the local video file path
        video_file = file_path  # Update this with your actual video file name

        # Trim the audio using FFmpeg (Extract segment from 313.6s to 381.7s)
        trimmed_audio = "trimmed_audio.mp3"
        subprocess.run(["ffmpeg", "-i", video_file, "-ss", start_time, "-to", end_time, "-q:a", "0", "-map", "a", trimmed_audio])


    # Load Whisper model for transcription
    model = whisper.load_model("small")

    # Transcribe the trimmed audio
    result = model.transcribe(trimmed_audio)

    return json.dumps(result["text"])

# ---------------------------------- GA 5.10 --------------------------------------- #

def extract_info_GA510(question_text):
  # Extract grid size (cut piece dimension)
  grid_size_pattern = r"cut into (\d+) \(\d+x\d+\) pieces"
  grid_size_match = re.search(grid_size_pattern, question_text)
  grid_size = int(grid_size_match.group(1)) if grid_size_match else 5  # Defaulting to 5x5

  # Extract mapping using regex
  mapping_pattern = r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"
  mapping_matches = re.findall(mapping_pattern, question_text)

  # Convert extracted values into dictionary format
  mapping = { (int(orig_r), int(orig_c)): (int(scram_r), int(scram_c)) for orig_r, orig_c, scram_r, scram_c in mapping_matches }

  return grid_size, mapping

def unscramble_image(question_text, image_bytes):
  grid_size, mapping = extract_info_GA510(question_text)

  # Load the scrambled image
  scrambled_image = Image.open(BytesIO(image_bytes))

  # Image dimensions
  piece_size = scrambled_image.width // grid_size  # Assuming a square image

  # Create a blank image to store the reconstructed output
  reconstructed_image = Image.new("RGB", scrambled_image.size)

  # Rearrange pieces based on mapping
  for (orig_r, orig_c), (scram_r, scram_c) in mapping.items():
      # Define box to crop the piece from scrambled image
      left = scram_c * piece_size
      upper = scram_r * piece_size
      right = left + piece_size
      lower = upper + piece_size

      # Crop the piece
      piece = scrambled_image.crop((left, upper, right, lower))

      # Define position to paste in reconstructed image
      paste_left = orig_c * piece_size
      paste_upper = orig_r * piece_size

      # Paste the piece into the correct position
      reconstructed_image.paste(piece, (paste_left, paste_upper))

  # Save the reconstructed image
  img_buffer = BytesIO()
  reconstructed_image.save(img_buffer, format="PNG")
  base64_str = base64.b64encode(img_buffer.getvalue()).decode("utf-8")

  return json.dumps(base64_str)  # Return Base64-encoded image

# ------------------------------------ END ----------------------------------------- #
