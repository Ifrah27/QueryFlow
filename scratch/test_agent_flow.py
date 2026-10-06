from langchain_core.messages import HumanMessage
from agents.data_agent import data_agent
from utils.dataset_manager import DatasetManager
import pandas as pd

# 1. Create a test table in Postgres
dm = DatasetManager()
df = pd.DataFrame({
    'customer_name': ['Alice', 'Bob', 'Charlie'],
    'total_sales': [100.5, 250.0, 75.25],
    'city': ['Mumbai', 'Delhi', 'Indore']
})
with open('scratch/test_sales.csv', 'rb') as f:
    success, msg, ds_info = dm.process_and_upload_csv(f, 'test_sales.csv')

table_name = ds_info['table_name']
print("Created table:", table_name)

# 2. Invoke Data Agent with Context
prompt = f"[CONTEXT: The user has selected uploaded dataset 'test_sales.csv'. Target PostgreSQL table name is '{table_name}'. Columns and types: {ds_info['schema']}]. How many rows are in the dataset '{table_name}'?"

response = data_agent.invoke({'messages': [HumanMessage(content=prompt)], 'route_response': ''})
print('Route:', response.get('route_response'))
for m in response.get('messages', []):
    if isinstance(m, dict):
        print('Generated SQL:', m.get('generated_sql_query'))
        print('Query Result:', m.get('sql_query_execution_result'))
        print('Final Answer:', m.get('final_answer'))

# 3. Cleanup
dm.drop_dataset_table(table_name)
print("Dropped table:", table_name)
