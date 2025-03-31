from io import BytesIO
import pandas as pd
import numpy as np
import subprocess
import datetime
import requests
import hashlib
import zipfile
import shutil
import json
import re
import os


# ---------------------------------- GA 1.1 --------------------------------------- #
def handle_VScode():
  output = r"""
Version:          Code 1.98.2 (ddc367ed5c8936efe395cffeec279b04ffd7db78, 2025-03-12T13:32:45.399Z)
OS Version:       Windows_NT x64 10.0.26100
CPUs:             12th Gen Intel(R) Core(TM) i3-1220P (12 x 1997)
Memory (System):  7.70GB (0.74GB free)
VM:               0%
  """
  return output

# ---------------------------------- GA 1.2 --------------------------------------- #
def extract_question_GA12(question_text):
  # Extract URL using regex
  url_pattern = r"https://[^\s]+"
  url_match = re.search(url_pattern, question_text)
  url = url_match.group(0) if url_match else None

  # Extract parameter name using regex
  param_name_pattern = r"parameter (\w+) set to"
  param_name_match = re.search(param_name_pattern, question_text)
  param_name = param_name_match.group(1) if param_name_match else None

  # Extract parameter value using regex
  param_value_pattern = r"set to ([\w.@]+)"
  param_value_match = re.search(param_value_pattern, question_text)
  param_value = param_value_match.group(1) if param_value_match else None

  return url, param_name, param_value

def get_json_output(question_text):
  url, param_name, param_value = extract_question_GA12(question_text)
  if not url:
    url = 'https://httpbin.org/get'
  if not param_name:
    param_name = 'email'
  if not param_value:
    param_value = '23f3001458@ds.study.iitm.ac.in'
  params = {param_name: param_value}

  response = requests.get(url, params=params)
  ans = response.json()
  print(ans)
  return json.dumps(ans)

# ---------------------------------- GA 1.3 --------------------------------------- #
def run_npx_prettier(file_path):
    # Run the npx prettier command and get the sha256sum
    cmd = f"npx -y prettier@3.4.2 {file_path} | sha256sum"
    process = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    # return the output
    return str(process.stdout.strip())

# ---------------------------------- GA 1.4 --------------------------------------- #
def extract_ques_GA14(question_text):
  # Extract formula using regex
  formula_pattern = r"=(?:[A-Z]+\([^\n]+\))"
  formula_match = re.search(formula_pattern, question_text, re.DOTALL)
  formula = formula_match.group(0) if formula_match else None

  return formula


def parse_formula_GA14(question_text: str):
    """
    Parses and evaluates a Google Sheets formula in Python.
    """

    formula = extract_ques_GA14(question_text)
    # Extract SEQUENCE parameters: SEQUENCE(rows, cols, start, step)
    seq_match = re.search(r"SEQUENCE\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", formula)
    if not seq_match:
        raise ValueError("SEQUENCE function not found or incorrect format.")

    rows, cols, start, step = map(int, seq_match.groups())

    # Corrected SEQUENCE generation: Row-wise traversal (Google Sheets style)
    sequence = np.arange(start, start + (rows * cols) * step, step).reshape(rows, cols)

    # Extract ARRAY_CONSTRAIN parameters: ARRAY_CONSTRAIN(array, num_rows, num_cols)
    # arr_match = re.search(r"ARRAY_CONSTRAIN\([^)]*,\s*(\d+)\s*,\s*(\d+)\s*\)", formula)
    arr_match = re.search(r"ARRAY_CONSTRAIN\(.*?\)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", formula)
    if not arr_match:
        raise ValueError("ARRAY_CONSTRAIN function not found or incorrect format.")

    num_rows, num_cols = map(int, arr_match.groups())
    print(num_rows, num_cols)

    # Apply ARRAY_CONSTRAIN: extract top-left submatrix
    constrained_array = sequence[:num_rows, :num_cols]

    # Compute SUM
    if "SUM(" in formula:
        result = np.sum(constrained_array)
    else:
        raise ValueError("SUM function not found in formula.")

    return str(result)

# ---------------------------------- GA 1.5 --------------------------------------- #
def extract_ques_GA15(question_text):
  formula_pattern = r"=SUM\(.*\))"

  # Extract formula using regex
  formula_pattern = r"=(?:[A-Z]+\([^\n]+\))"
  formula_match = re.search(formula_pattern, question_text, re.DOTALL)
  formula = formula_match.group(0) if formula_match else None
  return formula


def parse_formula_GA15(question_text: str):
    """
    Parses and evaluates a Google Sheets formula in Python.
    """
    # Extract formula using regex
    formula = extract_ques_GA15(question_text)

    values_match = re.search(r"SORTBY\(\{([\d,]+)\}", formula)
    values = list(map(int, values_match.group(1).split(',')))

    sort_match = re.search(r"SORTBY\(\{[\d,]+\},\s*\{([\d,]+)\}", formula)
    sort_order = list(map(int, sort_match.group(1).split(',')))

    take_match = re.search(r"TAKE\(.*?\)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", formula)
    take_rows, take_cols = map(int, take_match.groups())

    # Convert lists to numpy arrays
    values = np.array(values)
    sort_order = np.array(sort_order)

    # Step 1: Sort values based on sort_order
    sorted_indices = np.argsort(sort_order)
    sorted_values = values[sorted_indices]

    # Step 2: Take the first row and first 'take_cols' columns
    taken_values = sorted_values[:take_cols]

    # Step 3: Compute sum
    result = np.sum(taken_values)
    return str(result)

# ---------------------------------- GA 1.6 --------------------------------------- #

# ------------------------------------NOT DONE------------------------------------- #

# ---------------------------------- GA 1.7 --------------------------------------- #
def extract_ques_GA17(question_text):
  # Given text
  if question_text == "":
    question_text = "How many wednesdays are there in the date range 1990-02-15 to 2009-04-28?"

  # Regex pattern to extract the day name and dates (YYYY-MM-DD format)
  pattern = r"How many (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)s? .*? (\d{4}-\d{2}-\d{2}) to (\d{4}-\d{2}-\d{2})"
  # Find match
  match = re.search(pattern, question_text, re.IGNORECASE)

  if match:
      day_name = match.group(1)  # Extracted day name
      start_date = match.group(2)  # Extracted start date
      end_date = match.group(3)  # Extracted end date

      days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
      day_num = days.index(day_name.lower()) 
      
      return day_num, start_date, end_date
  else:
      print("No match found!")
      return None, None, None

def count_days(question_text):
    """Counts the number of days in a date range."""
    day_num, start_date, end_date = extract_ques_GA17(question_text)
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

    current_date = start_date
    day_count = 0

    while current_date <= end_date:
        if current_date.weekday() == day_num:
            day_count += 1
            current_date += datetime.timedelta(days=1)

    return str(day_count)

# ---------------------------------- GA 1.8 --------------------------------------- #
def extract_ques_GA18(question):
    column_match = re.search(r"value in the ['\"]?([\w]+)['\"]? column", question)

    if column_match:
        column_name = column_match.group(1)  # Extracted column name
    else:
        column_name = "answer"
    return column_name

def find_csv_val(question_text, file_bytes):
    column_name = extract_ques_GA18(question_text)
    
    # Unzip and extract the CSV file
    with zipfile.ZipFile(BytesIO(file_bytes), "r") as zip_ref:
        csv_filename = zip_ref.namelist()[0]  # Assuming single CSV file
        with zip_ref.open(csv_filename) as csv_file:
            df = pd.read_csv(csv_file)  # Read CSV into DataFrame

    # Extract the value from the "answer" column
    if column_name in df.columns:
        answer_value = df[column_name].iloc[0]  # Assuming first row's value
        return str(answer_value)
    else:
        print(f"Column '{column_name}' not found in the CSV file.")
        return None

# ---------------------------------- GA 1.9 --------------------------------------- #
def extract_ques_GA19(text):
  # Extract the first and second field names (keys in JSON)
  field_pattern = r'"(\w+)"\s*:\s*'
  fields = re.findall(field_pattern, text)
  first_field, sec_field = fields[0], fields[1]

  # Extract JSON data
  json_pattern = r"(\[.*\])"
  json_match = re.search(json_pattern, text, re.DOTALL).group(1)

  return json_match, first_field, sec_field


def sort_json_data(question_text):
    json_str, first_field, second_field = extract_ques_GA19(question_text)

    # Convert JSON string to list of dictionaries
    data_array = json.loads(json_str)

    # Ensure the sorting field values are of the correct type
    sorted_data = sorted(data_array, key=lambda x: (x[second_field], x[first_field]))

    # Convert back to compact JSON string
    return json.dumps(sorted_data, separators=(',', ':'))

# ---------------------------------- GA 1.10 -------------------------------------- #
def hash_sha256(text: str) -> str:
    encoded_text = text.encode("utf-8")  # Ensure UTF-8 encoding
    return hashlib.sha256(encoded_text).hexdigest()

def hash_file_sha256(file_bytes) -> str:
    data = BytesIO(file_bytes).read().decode("utf-8")

    # Split the data into key-value pairs
    data_dict = {}
    for line in data.strip().split("\n"):
        key, value = line.split("=")
        data_dict[key] = value

    hashed_json = hash_sha256(json.dumps(data_dict, separators=(",", ":")))  # Match JS JSON.stringify()
    return str(hashed_json)

# ---------------------------------- GA 1.11 -------------------------------------- #

# ---------------------------------- NOT DONE ------------------------------------- #

# ----------------------------------- GA 1.12 ------------------------------------- #
def extract_ques_GA112(text):
    # Extract the required symbols from the text
    match = re.search(r"([^\w\s]+(?:\s+OR\s+[^\w\s]+)+)", text).group(1)
    symbols = re.findall(r'[^\w\s]', match)
    return symbols

def extract_symbol_count(question_text, zip_file_path):
    symbols = extract_ques_GA112(question_text)

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall('12extracted_files')
    tot = 0
    extracted_files = os.listdir('12extracted_files')
    for file in extracted_files:
        if file == 'data1.csv':
            data1 = pd.read_csv(os.path.join('12extracted_files', file), encoding='cp1252')
        if file == 'data2.csv':
            data2 = pd.read_csv(os.path.join('12extracted_files', file), encoding='utf-8')
        if file == 'data3.txt':
            data3 = pd.read_csv(os.path.join('12extracted_files', file), encoding='utf-16', sep='\t')
    all_data = pd.concat([data1, data2, data3])
    filtered_data = all_data[all_data['symbol'].isin(symbols)]
    tot = filtered_data['value'].sum()
    return str(tot)

# ---------------------------------- GA 1.13 -------------------------------------- #
# ---------------------------------- NOT DONE ------------------------------------- #
# ---------------------------------- GA 1.14 -------------------------------------- #
def extract_ques_GA114(text):
  # Extract words to be replaced
  match = re.search(r'"(\w+)" \(.*?\) with "([^"]+)"', text)

  if match:
      old_word = match.group(1)  # Word to be replaced
      new_word = match.group(2)  # Replacement word
      print(f'"{old_word}" will be converted into "{new_word}"')
      return old_word, new_word
  else:
      print("No match found")
      return None, None

def extract_zip_GA114(zip_path, extract_path):
  os.makedirs(extract_path, exist_ok=True)
  with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

def replace_word_and_extract_hash(ques_text, zip_path):
    from_word, to_word = extract_ques_GA114(ques_text)
    # Step 1: Extract the ZIP file
    extract_path = "14extracted_files"
    extract_zip_GA114(zip_path, extract_path)

    # Step 2: Collect file paths (match Bash `ls -U` behavior)
    file_list = [os.path.join(extract_path, f) for f in os.listdir(extract_path) if os.path.isfile(os.path.join(extract_path, f))]

    # Step 3: Perform case-insensitive replacement while preserving line endings
    for file_path in file_list:
        with open(file_path, "rb") as f:
            content = f.read()  # Read raw bytes (preserves line endings)

        # Replace IITM (case-insensitive) in a binary-safe way
        old_term_bytes = from_word.encode()  
        new_term_bytes = to_word.encode()  

        # Create a binary regex pattern
        pattern = rb'(?i)\b' + re.escape(old_term_bytes) + rb'\b'  # Escape ensures safety

        # Perform the binary-safe replacement
        new_content = re.sub(pattern, new_term_bytes, content)

        with open(file_path, "wb") as f:
            f.write(new_content)  # Write raw bytes (preserves line endings)

    # Step 4: Compute SHA-256 hash like `cat * | sha256sum`
    sha256_hash = hashlib.sha256()

    # Ensure exact Bash order
    file_list.sort(key=lambda x: os.path.basename(x).casefold())

    for file_path in file_list:
        with open(file_path, "rb") as f:
            sha256_hash.update(f.read())

    # Print the computed hash
    computed_hash = sha256_hash.hexdigest()
    return str(computed_hash)

# ---------------------------------- GA 1.15 -------------------------------------- #
def extract_ques_GA115(text):
  # Extract minimum file size
  size_match = re.search(r"at least (\d+) bytes", text)

  # Extract date-time
  date_match = re.search(r"on or after (.+\d{4}, \d{1,2}:\d{2} (?:am|pm) IST)", text)

  if size_match and date_match:
      min_size = int(size_match.group(1))  # Extracts 5164
      date_time_str = date_match.group(1)  # Extracts "Mon, 7 Oct, 2019, 1:26 pm IST"

      # Convert to "2019-10-07 13:26:00"
      dt_obj = datetime.datetime.strptime(date_time_str, "%a, %d %b, %Y, %I:%M %p IST")
      formatted_dt = dt_obj.strftime("%Y-%m-%d %H:%M:%S")

      return min_size, formatted_dt
  else:
      print("No match found")
      return None, None
  
def extract_zip_GA115(zip_path, extract_to):
    """Extract the ZIP file while preserving timestamps."""
    os.makedirs(extract_to, exist_ok=True)

    if os.name == "nt":  # Windows → Use 7-Zip
        subprocess.run(["7z", "x", zip_path, f"-o{extract_to}", "-mtc=on"], check=True)
    else:  # Linux/macOS → Use unzip
        subprocess.run(["unzip", "-o", zip_path, "-d", extract_to], check=True)

def get_matching_files_size(question_text, file_path):
    """Calculate total size of files meeting the conditions."""
    folder_path = "15extracted_files"
    extract_zip_GA115(file_path, folder_path)
    MIN_SIZE, MIN_DATE_STR = extract_ques_GA115(question_text)
    MIN_DATE = datetime.datetime.strptime(MIN_DATE_STR, "%Y-%m-%d %H:%M:%S")
    total_size = 0

    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_stat = os.stat(file_path)

            file_size = file_stat.st_size
            mod_time = datetime.datetime.fromtimestamp(file_stat.st_mtime)

            # Check if file meets the conditions
            if file_size >= MIN_SIZE and mod_time >= MIN_DATE:
                total_size += file_size

    return str(total_size)

# ---------------------------------- GA 1.16 -------------------------------------- #
def extract_zip_GA116(zip_path, extract_to):
    """Extract the ZIP file while preserving timestamps."""
    os.makedirs(extract_to, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)

def move_all_files(source_folder, target_folder):
    """Move all files from subfolders into a single target folder."""
    os.makedirs(target_folder, exist_ok=True)

    for root, _, files in os.walk(source_folder):
        for file in files:
            src_path = os.path.join(root, file)
            dest_path = os.path.join(target_folder, file)
            shutil.move(src_path, dest_path)

def rename_files(folder_path):
    """Rename files by replacing digits (0 → 1, 1 → 2, ..., 9 → 0)."""
    digit_map = str.maketrans("0123456789", "1234567890")

    for file in os.listdir(folder_path):
        old_path = os.path.join(folder_path, file)
        new_name = file.translate(digit_map)  # Apply digit transformation
        new_path = os.path.join(folder_path, new_name)

        if old_path != new_path:  # Only rename if necessary
            os.rename(old_path, new_path)

def compute_sha256(folder_path):
    """Run the Bash command: grep . * | LC_ALL=C sort | sha256sum"""
    command = "grep . * | LC_ALL=C sort | sha256sum"
    result = subprocess.run(command, shell=True, cwd=folder_path, capture_output=True, text=True)
    return result.stdout.strip()

def get_rename_hash(ZIP_FILE):
    # Constants
    EXTRACT_DIR = "16extracted_files"
    FINAL_DIR = "16final_folder"
    # Step 2: Extract ZIP while keeping timestamps
    extract_zip_GA116(ZIP_FILE, EXTRACT_DIR)

    # Step 3: Move all files into a single folder
    move_all_files(EXTRACT_DIR, FINAL_DIR)

    # Step 4: Rename files by replacing digits
    rename_files(FINAL_DIR)

    # Step 5: Compute SHA-256 hash of sorted grep output
    sha256_hash = compute_sha256(FINAL_DIR)

    return str(sha256_hash)

# ---------------------------------- GA 1.17 -------------------------------------- #
def extract_ques_GA117(text):
  # Regex to extract filenames (ending with .txt)
  filenames = re.findall(r"\b\w+\.txt\b", text)
  return filenames

def extract_zip_GA117(zip_path, extract_to):
    """Extract the ZIP file."""
    os.makedirs(extract_to, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)

def count_differences(file1, file2):
    """Count the number of differing lines between two files."""
    with open(file1, "r", encoding="utf-8") as f1, open(file2, "r", encoding="utf-8") as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()

    diff_count = sum(1 for line1, line2 in zip(lines1, lines2) if line1 != line2)
    return diff_count

def find_file_diff(ques_text, ZIP_FILE):
    file1s = extract_ques_GA117(ques_text)
    file1 = file1s[0]
    file2 = file1s[1]
    EXTRACT_DIR = "17extracted_files"
    # Step 1: Extract ZIP
    extract_zip_GA117(ZIP_FILE, EXTRACT_DIR)

    # Step 2: Locate a.txt and b.txt
    a_path = os.path.join(EXTRACT_DIR, file1)
    b_path = os.path.join(EXTRACT_DIR, file2)

    if not os.path.exists(a_path) or not os.path.exists(b_path):
        print("Error: a.txt or b.txt not found in extracted files.")
        return "Error: Files not found"

    # Step 3: Count differing lines
    diff_lines = count_differences(a_path, b_path)
    return str(diff_lines)

# ---------------------------------- GA 1.18 -------------------------------------- #
# SELECT SUM(units * price)
# FROM tickets
# WHERE LOWER(TRIM(type)) = 'gold';

def extract_ques_GA118(text):
  # Regex to extract table name (assumes a word before "table")
  table_name_match = re.search(r"\b(\w+)\s+table\b", text)

  # Regex to extract search item name inside quotes
  search_item_match = re.search(r'"([^"]+)"', text)

  # Extract values if matches found
  table_name = table_name_match.group(1) if table_name_match else None
  search_item = search_item_match.group(1) if search_item_match else None

  print("Table Name:", table_name)
  print("Search Item Name:", search_item)
  return table_name, search_item

def gen_sql_query(question_text):
    # Extract table name and search item
    table_name, search_item = extract_ques_GA118(question_text)
    
    # Generate SQL query
    return f"SELECT SUM(units * price) FROM {table_name} WHERE LOWER(TRIM(type)) = '{search_item}';"

# ---------------------------------- END -------------------------------------- #