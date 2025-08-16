import askpandas as ap
import pandas as pd
from faker import Faker
import random

# Generate sample data for multiple dataframes
fake = Faker()

# Create employees dataframe
employees_data = []
for i in range(50):
    employees_data.append({
        'employee_id': i + 1,
        'name': fake.name(),
        'department': random.choice(['Engineering', 'Sales', 'Marketing', 'HR', 'Finance']),
        'hire_date': fake.date_this_decade().isoformat(),
        'salary': random.randint(40000, 120000),
        'location': fake.city()
    })

employees_df = pd.DataFrame(employees_data)
employees_df.to_csv("employees.csv", index=False)

# Create sales dataframe
sales_data = []
for i in range(100):
    sales_data.append({
        'sale_id': i + 1,
        'employee_id': random.randint(1, 50),
        'product': random.choice(['Product A', 'Product B', 'Product C', 'Product D']),
        'amount': random.randint(1000, 50000),
        'date': fake.date_this_decade().isoformat(),
        'region': random.choice(['North', 'South', 'East', 'West'])
    })

sales_df = pd.DataFrame(sales_data)
sales_df.to_csv("sales.csv", index=False)

# Create products dataframe
products_data = [
    {'product_id': 1, 'name': 'Product A', 'category': 'Electronics', 'price': 500},
    {'product_id': 2, 'name': 'Product B', 'category': 'Clothing', 'price': 100},
    {'product_id': 3, 'name': 'Product C', 'category': 'Home', 'price': 200},
    {'product_id': 4, 'name': 'Product D', 'category': 'Electronics', 'price': 800}
]

products_df = pd.DataFrame(products_data)
products_df.to_csv("products.csv", index=False)

print("Sample data created:")
print(f"Employees: {employees_df.shape}")
print(f"Sales: {sales_df.shape}")
print(f"Products: {products_df.shape}")

# Set up Ollama LLM (requires Ollama running locally and 'mistral' model pulled)
try:
    llm = ap.OllamaLLM(model_name="mistral")
    ap.set_llm(llm)
    print("✓ Ollama LLM configured successfully")
except Exception as e:
    print(f"✗ Failed to configure Ollama LLM: {e}")
    print("Please ensure Ollama is running and the 'mistral' model is available")
    exit(1)

# Load dataframes
employees = ap.DataFrame("employees.csv")
sales = ap.DataFrame("sales.csv")
products = ap.DataFrame("products.csv")

print("\n" + "="*60)
print("MULTI-DATAFRAME ANALYSIS EXAMPLES")
print("="*60)

# Example 1: Basic multi-dataframe query
print("\n1. Who are the top 5 employees by total sales amount?")
result = ap.chat("Who are the top 5 employees by total sales amount?", employees, sales)
print(result)

# Example 2: Complex aggregation with joins
print("\n2. What is the total revenue by department and region?")
result = ap.chat("What is the total revenue by department and region?", employees, sales)
print(result)

# Example 3: Product performance analysis
print("\n3. Which products perform best in each region?")
result = ap.chat("Which products perform best in each region?", sales, products)
print(result)

# Example 4: Employee performance visualization
print("\n4. Create a bar chart showing average sales by department")
result = ap.chat("Create a bar chart showing average sales by department", employees, sales)
print(result)

# Example 5: Time-based analysis
print("\n5. Show sales trends over time by region")
result = ap.chat("Show sales trends over time by region", sales)
print(result)

# Example 6: Data quality check
print("\n6. Check for any missing or inconsistent data")
result = ap.chat("Check for any missing or inconsistent data", employees, sales, products)
print(result)

# Example 7: Advanced filtering
print("\n7. Show employees in Engineering department with salary > 80000")
result = ap.chat("Show employees in Engineering department with salary > 80000", employees)
print(result)

# Example 8: Statistical analysis
print("\n8. What is the correlation between salary and sales performance?")
result = ap.chat("What is the correlation between salary and sales performance?", employees, sales)
print(result)

print("\n" + "="*60)
print("QUERY ANALYSIS AND VALIDATION")
print("="*60)

# Analyze a query
query = "Show top 10 employees by sales performance"
analysis = ap.analyze_query(query)
print(f"\nQuery: {query}")
print(f"Categories: {list(analysis['categories'].keys())}")
print(f"Primary category: {analysis['primary_category']}")

# Validate a query
validation = ap.validate_query(query, employees.columns)
print(f"\nQuery validation: {'✓ Valid' if validation['is_valid'] else '✗ Invalid'}")
if validation['warnings']:
    print("Warnings:", validation['warnings'])
if validation['suggestions']:
    print("Suggestions:", validation['suggestions'])

# Get query examples
print("\nExample queries for visualization:")
examples = ap.get_query_examples('visualization')
for i, example in enumerate(examples[:3], 1):
    print(f"{i}. {example}")

print("\n" + "="*60)
print("ENGINE STATISTICS")
print("="*60)

# Get engine statistics
engine = ap.AskPandasEngine(llm)
stats = engine.get_engine_stats()
print(f"Total queries executed: {stats['total_queries']}")
print(f"Successful queries: {stats['successful_queries']}")
print(f"Failed queries: {stats['failed_queries']}")

print("\n" + "="*60)
print("CONFIGURATION")
print("="*60)

# Show current configuration
config = ap.get_config()
print("Current configuration:")
for key, value in config.items():
    print(f"  {key}: {value}")

print("\n" + "="*60)
print("AVAILABLE MODELS")
print("="*60)

# Show available models
models = ap.get_available_models()
print("Ollama models:", models['ollama'])
print("HuggingFace models:", models['huggingface'])

print("\n" + "="*60)
print("EXAMPLE COMPLETED SUCCESSFULLY!")
print("="*60)
