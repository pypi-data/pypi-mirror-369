import askpandas as ap
import pandas as pd
from faker import Faker
import random

# Generate a fake CSV file for testing
fake = Faker()
rows = []
for _ in range(20):
    rows.append(
        {
            "name": fake.name(),
            "country": fake.country(),
            "revenue": random.randint(1000, 10000),
            "date": fake.date_this_decade().isoformat(),
        }
    )
df_fake = pd.DataFrame(rows)
df_fake.to_csv("fake_sample.csv", index=False)

# Set up Ollama LLM (requires Ollama running locally and 'mistral' model pulled)
llm = ap.OllamaLLM(model_name="mistral")
ap.set_llm(llm)

# Load and query
fake_df = ap.DataFrame("fake_sample.csv")
result = fake_df.chat("Which are the top 5 countries by total revenue?")
print(result)

# Create a visualization
fake_df.chat("Create a bar chart showing total revenue by country")
