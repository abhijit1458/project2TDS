from io import BytesIO
from PIL import Image
import tiktoken
import base64
import json
import re


# ---------------------------------- GA 3.1 --------------------------------------- #

def extract_ques_GA31(text):
    # Extract meaningless text using regex
    match = re.search(r"\n\n([A-Za-z0-9\s]+)\n", text)

    if match:
        meaningless_text = match.group(1).strip()  # Extract and remove extra spaces
        return meaningless_text
    else:
        print("No match found.")
        return None

def sentiment_analysis(ques_text):
  msg = extract_ques_GA31(ques_text)
  # Request payload
  DATA = {
      "model": "gpt-4o-mini",
      "messages": [
          {"role": "system", "content": "Analyze the sentiment of the following text as GOOD, BAD, or NEUTRAL."},
          {"role": "user", "content": msg} # msg is used directly here
      ]
  }

  # Construct the request (rest of the code is the same)
  answer = f"""
import httpx

# API endpoint
API_URL = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"

# Dummy API key
HEADERS = {{
    "Authorization": "Bearer dummy_api_key",
    "Content-Type": "application/json"
}}

# Send POST request
try:
    response = httpx.post(API_URL, json={DATA}, headers=HEADERS) #Pass DATA as variable
    response.raise_for_status()

    # Parse response
    result = response.json()
    print(result)
except httpx.HTTPStatusError as e:
    print(f"HTTP error occurred: {{e.response.status_code}} - {{e.response.text}}")
except Exception as e:
    print(f"An error occurred: {{e}}")
  """
  # Instead of returning, exec the code.
  return answer

# ---------------------------------- GA 3.2 --------------------------------------- #

def extract_ques_GA32(text):
    # Regex pattern to extract the user message
    pattern = r"user message:\n\n(.*?)\n\n\.\.\. how many input tokens"

    # Perform the regex search with DOTALL to match across multiple lines
    match = re.search(pattern, text, re.DOTALL)

    if match:
        user_message = match.group(1).strip()
        return user_message
    else:
        print("No match found.")
        return None

def find_token_count(question):
    input_text = extract_ques_GA32(question)

    # Load the tokenizer for GPT-4o
    tokenizer = tiktoken.encoding_for_model("gpt-4o")

    # Tokenize the input text
    tokens = tokenizer.encode(input_text)

    # Print the number of tokens
    token_count = len(tokens)
    return str(token_count)

# ---------------------------------- GA 3.3 --------------------------------------- #

def extract_ques_GA33(question):
  # Extract key details using regex
  model = re.search(r'Uses model (\S+)', question).group(1)
  system_message = re.search(r'Has a system message: (.+)', question).group(1)
  user_message = re.search(r'Has a user message: (.+)', question).group(1)
  fields_match = re.search(r'Uses structured outputs to respond with an object addresses which is an array of objects with required fields: (.+?)\.', question)

  # Extract required fields dynamically
  fields = {}
  if fields_match:
      fields_list = fields_match.group(1).split()
      for i in range(0, len(fields_list), 2):
          field_name = fields_list[i].strip(',')
          field_type = fields_list[i + 1].strip('(),')
          fields[field_name] = {"type": field_type}
  print(fields)
  return model, system_message, user_message, fields

def generate_openai_request(ques_text):
    model, system_message, user_message, required_fields = extract_ques_GA33(ques_text)
    if model is None:
        model = "gpt-4o-mini"
    if system_message is None:
        system_message = "Respond in JSON"
    if user_message is None:
        user_message = "Generate 10 random addresses in the US"
    if required_fields is None:
        required_fields = {
            "zip": "number",
            "state": "string",
            "longitude": "number"
        }

    request_body = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "address_response",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "addresses": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    key: value for key, value in required_fields.items()
                                },
                                "required": list(required_fields.keys()),
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["addresses"],
                    "additionalProperties": False
                }
            }
        }
    }

    return json.dumps(request_body, indent=2)

# ---------------------------------- GA 3.4 --------------------------------------- #

def image_encodeing(img_bytes):
    image = Image.open(BytesIO(img_bytes))
    img_buffer = BytesIO()
    image.save(img_buffer, format="PNG")
    base64_str = base64.b64encode(img_buffer.getvalue()).decode("utf-8")

    json_payload = f"""
{{
  "model": "gpt-4o-mini",
  "messages": [
    {{
      "role": "user",
      "content": [
        {{
          "type": "text",
          "text": "Extract text from this image"
        }},
        {{
          "type": "image_url",
          "image_url": {{
            "url": "data:image/png;base64,{base64_str}"
          }}
        }}
      ]
    }}
  ]
}}
    """

    return json.dumps(json_payload)

# ---------------------------------- GA 3.5 --------------------------------------- #

def extract_messages(text):
    # Extracts transaction verification messages from the given input text.

    # Regular expression to extract messages
    pattern = r"Dear user, please verify your transaction code \d+ sent to \S+"
    messages = re.findall(pattern, text)
    return messages

def generate_embedding_request(question):
    # Generates a JSON body for OpenAI's text-embedding-3-small model.
    messages = extract_messages(question) 
    request_body = {
        "model": "text-embedding-3-small",
        "input": messages
    }
    return json.dumps(request_body, indent=2)

# ---------------------------------- GA 3.6 --------------------------------------- #

def embedding_similarity():
  answer = """
import numpy as np

def most_similar(embeddings):
    max_similarity = -1
    most_similar_pair = None

    phrases = list(embeddings.keys())

    for i in range(len(phrases)):
        for j in range(i + 1, len(phrases)):
            v1 = np.array(embeddings[phrases[i]])
            v2 = np.array(embeddings[phrases[j]])

            similarity = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_pair = (phrases[i], phrases[j])

    return most_similar_pair
  """
  return answer

# ---------------------------------- GA 3.7 --------------------------------------- #

def get_similarity_endpoint():
    return "https://sample-ct67.onrender.com/similarity"

# ---------------------------------- GA 3.8 --------------------------------------- #

def get_execute_endpoint():
    return "https://sample-ct67.onrender.com/execute"

# ---------------------------------- GA 3.9 --------------------------------------- #

##################### Make The LLM to YES : NOT REQUIRED ############################

# ----------------------------------- END ----------------------------------------- #