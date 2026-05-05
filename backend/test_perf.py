import time
import pandas as pd
from collections import Counter

start = time.time()
df_real = pd.read_csv("backend/data/datasets/llm_training_data.csv")
print(f"Loaded in {time.time() - start:.2f}s")

start = time.time()
all_skills = []
for skills_str in df_real["matched_skills"]:
    all_skills.extend(str(skills_str).split("|"))

counter = Counter(all_skills)
print(f"Counted {len(all_skills)} skills in {time.time() - start:.2f}s")
print(f"Unique skills: {len(counter)}")
print(counter.most_common(10))
