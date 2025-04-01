from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
import shutil
import numpy as np
import json

from functionsGA1 import *
from functionsGA2 import *
from functionsGA3 import *
from functionsGA4 import *
from functionsGA5 import *

from openai_embed import find_embed

with open("All_Ques_Embedded.json", "r") as f:
    file_data = json.load(f)

embedd = [json.loads(key) for entry in file_data for key in entry.keys()]  # Ensure correct loading


def get_q_id(question):
    ques_emb = find_embed(question)  # Get embedding for input question
    
    # Ensure embeddings are numpy arrays
    ques_emb = np.array(ques_emb).reshape(1, -1)
    embedd_np = np.array(embedd)  

    # Compute cosine similarity
    similarities = cosine_similarity(ques_emb, embedd_np)[0]  

    # Print similarity scores for debugging
    print("🔹 Cosine Similarities:", similarities)

    most_similar_idx = np.argmax(similarities)  # Get best match
    print("🔹 Most Similar Index:", most_similar_idx)
    
    # Convert to JSON string
    map_key = json.dumps(embedd[most_similar_idx])

    # Find the corresponding question ID in file_data
    mapped_question_id = None
    for entry in file_data:
        if map_key in entry:
            mapped_question_id = entry[map_key]
            break
    
    return mapped_question_id  # Fetch corresponding question ID

def save_file(file):
    # Define the upload directory (change this path if needed)
    UPLOAD_DIR = Path("/tmp/uploads")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists

    # Create the file path
    file_path = UPLOAD_DIR / file.filename

    # Save the file properly
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)  # Copy file data without additional read

    return file_path  # Return the saved file path

async def get_solution(q_id, ques, file):

    # ------------------------ GA 1 ------------------------------ #

    if q_id == "GA_1_1":
        return handle_VScode()
    elif q_id == "GA_1_2":
        return get_json_output(ques)
    elif q_id == "GA_1_3":    
        file_path = save_file(file)
        return run_npx_prettier(file_path)
    elif q_id == "GA_1_4":
        return parse_formula_GA14(ques)
    elif q_id == "GA_1_5":
        return parse_formula_GA15(ques)
    elif q_id == "GA_1_6":
        file_bytes = await file.read()
        return find_hidden_value(file_bytes)
    elif q_id == "GA_1_7":
        return count_days(ques)
    elif q_id == "GA_1_8":
        file_bytes = await file.read()
        return find_csv_val(ques, file_bytes)
    elif q_id == "GA_1_9":
        return sort_json_data(ques)
    elif q_id == "GA_1_10":
        file_bytes = await file.read()
        return hash_file_sha256(file_bytes)
    elif q_id == "GA_1_11":
        file_bytes = await file.read()
        return find_total_tag(ques, file_bytes)
    elif q_id == "GA_1_12":
        file_path = save_file(file)
        return extract_symbol_count(ques, file_path)
    # elif q_id == "GA_1_13":
        # return get_json_output(ques)
    elif q_id == "GA_1_14":
        file_path = save_file(file)
        return replace_word_and_extract_hash(ques, file_path)
    elif q_id == "GA_1_15":
        file_path = save_file(file)
        return get_matching_files_size(ques, file_path)
    elif q_id == "GA_1_16":
        file_path = save_file(file)
        return get_rename_hash(ques, file_path)
    elif q_id == "GA_1_17":
        file_path = save_file(file)
        return find_file_diff(ques, file_path)
    elif q_id == "GA_1_18":
        return gen_sql_query(ques)
    
    # ------------------------ GA 2 ------------------------------ #

    elif q_id == "GA_2_1":
        return generete_markdown()
    # elif q_id == "GA_2_2":
        # return gendown2()
    elif q_id == "GA_2_3":
        return git_static_hosting()
    elif q_id == "GA_2_4":
        return google_auth()
    elif q_id == "GA_2_5":
        file_bytes = await file.read()
        return count_light_pixels(file_bytes)
    # elif q_id == "GA_2_6":
        # return getepo_info(ques)
    elif q_id == "GA_2_7":
        return github_action()
    elif q_id == "GA_2_8":
        return podman_docker()
    # elif q_id == "GA_2_9":
        # return get__info(ques)

    # ------------------------ GA 3 ------------------------------ #

    elif q_id == "GA_3_1":
        return sentiment_analysis(ques)
    elif q_id == "GA_3_2":
        return find_token_count(ques)
    elif q_id == "GA_3_3":
        return generate_openai_request(ques)
    elif q_id == "GA_3_4":
        file_bytes = await file.read()
        return image_encodeing(file_bytes)
    elif q_id == "GA_3_5":
        return generate_embedding_request(ques)
    elif q_id == "GA_3_6":
        return embedding_similarity()
    elif q_id == "GA_3_7":
        return get_similarity_endpoint()
    elif q_id == "GA_3_8":
        return get_execute_endpoint()
    
    # ------------------------ GA 4 ------------------------------ #

    elif q_id == "GA_4_1":
        return find_no_of_ducks(ques)
    elif q_id == "GA_4_2":
        return IMDB_seacrching(ques)
    elif q_id == "GA_4_3":
        return wikipedia_search()
    elif q_id == "GA_4_4":
        return bbc_weather_fetching(ques)
    elif q_id == "GA_4_5":
        return find_bounding_box(ques)
    elif q_id == "GA_4_6":
        return get_latest_hn_post_with_keywords_and_points(ques)
    elif q_id == "GA_4_7":
        return get_user_details(ques)
    elif q_id == "GA_4_8":
        return scriping_with_github_action()
    elif q_id == "GA_4_9":
        file_path = save_file(file)
        return extract_table_from_pdf(ques, file_path)
    elif q_id == "GA_4_10":
        return extract_markdown_pdf()

    # ------------------------ GA 5 ------------------------------ #

    elif q_id == "GA_5_1":
        file_bytes = await file.read()
        return process_excel_file(ques, file_bytes)
    elif q_id == "GA_5_2":
        file_bytes = await file.read()
        return extract_student_ids(file_bytes)
    elif q_id == "GA_5_3":
        file_path = save_file(file)
        return process_logs_GA53(ques, file_path)
    elif q_id == "GA_5_4":
        file_path = save_file(file)
        return process_logs_GA54(ques, file_path)
    elif q_id == "GA_5_5":
        file_bytes = await file.read()
        return process_sales_data(ques, file_bytes)
    elif q_id == "GA_5_6":
        file_path = save_file(file)
        return process_jsonl_file(file_path)
    elif q_id == "GA_5_7":
        file_bytes = await file.read()
        return find_key_occurrences(ques, file_bytes)
    elif q_id == "GA_5_8":
        return find_posts(ques)
    elif q_id == "GA_5_9":
        file_path = save_file(file)
        return transcribe_segment(ques, file_path)
    elif q_id == "GA_5_10":
        file_bytes = await file.read()
        return unscramble_image(ques, file_bytes)
    else:
        return "Invalid question ID"

    # ------------------------- END ------------------------------- #



    

    

