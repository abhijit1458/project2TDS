from io import BytesIO
from PIL import Image
import numpy as np
import colorsys
import json




# ---------------------------------- GA 2.1 --------------------------------------- #

def generete_markdown():
    answer = r"""
# Weekly Step Analysis

This report analyzes the **number** of steps walked each day for a week, comparing personal trends over time and with friends. The goal is to identify areas for improvement and maintain a consistent exercise routine.

---

## Methodology

The analysis follows these steps:

1. *Data Collection*:
   - Step counts were recorded using a fitness tracker.
   - Friends' step data was collected via a shared fitness app.

2. *Data Analysis*:
   - Daily step counts were compared with the personal goal of 10,000 steps.
   - Weekly trends were visualized and summarized.

3. *Comparison*:
   - Trends were compared with friends' weekly averages.

Note: This analysis assumes all data points are accurate and complete. If not, a preprocessing step is applied using the function `clean_data(dataset)`.

---

## Results

### Step Counts Table
The table below compares personal step counts with friends' averages:

| Day       | My Steps | Friends' Avg Steps |
|-----------|----------|--------------------|
| Monday    | 8,500    | 9,800              |
| Tuesday   | 9,200    | 10,100             |
| Wednesday | 7,500    | 8,900              |
| Thursday  | 10,300   | 10,500             |
| Friday    | 12,000   | 9,700              |
| Saturday  | 14,000   | 11,200             |
| Sunday    | 13,500   | 12,000             |

---
###Hyperlink

[stepcount](https://stepcount.com)

###Image
![Step Count Image](https://www.dreamstime.com/illustration/step-counter.html)

###Blockquote
>Number of steps you walked in a week is presented.

## Observations

- *Weekend Success*: Step counts were significantly higher on Saturday and Sunday.
- *Midweek Dip*: Wednesday had the lowest step count.
- *Goal Achievement*: The 10,000-step goal was achieved on four out of seven days.

---

### Visualizing Weekly Steps
The following Python code was used to create a bar chart showing step counts:

```python
import matplotlib.pyplot as plt

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
my_steps = [8500, 9200, 7500, 10300, 12000, 14000, 13500]

plt.bar(days, my_steps, color='skyblue')
plt.title("My Daily Step Counts")
plt.xlabel("Days")
plt.ylabel("Steps")
plt.axhline(y=10000, color='red', linestyle='--', label='Goal')
plt.legend()
plt.show()
    """
    return json.dumps(answer)

# ---------------------------------- GA 2.2 --------------------------------------- #

# --------------------------------- NOT DONE -------------------------------------- #

# ---------------------------------- GA 2.3 --------------------------------------- #

def git_static_hosting():
    return "https://abhijit1458.github.io/Sample-Static-Hosing/"

# ---------------------------------- GA 2.4 --------------------------------------- #

def google_auth():
    return "38bff"

# ---------------------------------- GA 2.5 --------------------------------------- #

def count_light_pixels(image_bytes):
    image = Image.open(BytesIO(image_bytes))

    rgb = np.array(image) / 255.0
    lightness = np.apply_along_axis(lambda x: colorsys.rgb_to_hls(*x)[1], 2, rgb)
    light_pixels = np.sum(lightness > 0.489)
    print(f'Number of pixels with lightness > 0.489: {light_pixels}')
    return str(light_pixels)

# ---------------------------------- GA 2.6 --------------------------------------- #

# --------------------------------- NOT DONE -------------------------------------- #

# ---------------------------------- GA 2.7 --------------------------------------- #

def github_action():
    return "https://github.com/abhijit1458/GitAction"

# ---------------------------------- GA 2.8 --------------------------------------- #

def podman_docker():
    return "https://hub.docker.com/repository/docker/abhijit1458/pdmgolang/general"

# ---------------------------------- GA 2.9 --------------------------------------- #

# --------------------------------- NOT DONE -------------------------------------- #

# ---------------------------------- GA 2.10 -------------------------------------- #
'''
██╗     ██╗      █████╗ ███╗   ███╗ █████╗ ███████╗██╗██╗     ███████╗
██║     ██║     ██╔══██╗████╗ ████║██╔══██╗██╔════╝██║██║     ██╔════╝
██║     ██║     ███████║██╔████╔██║███████║█████╗  ██║██║     █████╗
██║     ██║     ██╔══██║██║╚██╔╝██║██╔══██║██╔══╝  ██║██║     ██╔══╝
███████╗███████╗██║  ██║██║ ╚═╝ ██║██║  ██║██║     ██║███████╗███████╗
╚══════╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚══════╝'
'''                 
# ----------------------------- NEED NOT TO ANSWER ---------------------------------- #

# ----------------------------------- END ------------------------------------------- #