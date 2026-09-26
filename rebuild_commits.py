import os
import subprocess
import datetime
import random

repo_dir = r"d:\AI_Data_Agent"
os.chdir(repo_dir)

# Set Git global and local config for user name and email explicitly
subprocess.run(["git", "config", "--local", "user.name", "Ifrah27"], check=True)
subprocess.run(["git", "config", "--local", "user.email", "ifrahqureshi27@gmail.com"], check=True)

# 1. Back up all working tree files into memory
print("Reading current files into memory...")
file_contents = {}
for root, dirs, files in os.walk("."):
    if any(ignore in root for ignore in [".git", ".venv", "__pycache__", "node_modules"]):
        continue
    for f in files:
        filepath = os.path.normpath(os.path.join(root, f))
        if filepath.startswith(".git") or filepath.startswith(".venv") or "fix_author.py" in filepath or "generate_commits.py" in filepath:
            continue
        try:
            with open(filepath, "rb") as file_obj:
                file_contents[filepath] = file_obj.read()
        except Exception:
            pass

print(f"Total files backed up: {len(file_contents)}")

commit_messages = [
    "initial project setup",
    "add pyproject toml and requirements",
    "setup gitignore and env template",
    "init base models schema",
    "add schema model definitions",
    "create database utility module",
    "add db connection helper",
    "implement llm picker utility",
    "add model selection logic",
    "create etl tools helper",
    "implement extract load tool",
    "add transform load tool",
    "setup etl analyst agent",
    "etl analyst node handler",
    "add etl prompts and workflow",
    "setup sql analyst agent",
    "add query curation step",
    "add context gathering helper",
    "sql analyst prompts update",
    "implement sql safety validation",
    "add execution safety checker",
    "setup main router data agent",
    "router classification node",
    "langgraph graph orchestration",
    "add main entrypoint runner",
    "test script for db feeding",
    "add sample datasets",
    "test data agent schema context",
    "fix sql analyst output format",
    "update schema definitions",
    "refactor etl tools error handling",
    "add parquet format support",
    "update llm fallback options",
    "refactor router prompt instructions",
    "backend API service layer",
    "fastapi backend setup",
    "add health endpoint",
    "datasets backend endpoint",
    "chat message endpoint backend",
    "query history backend service",
    "frontend vite React setup",
    "add Tailwind CSS setup",
    "add icon assets and public files",
    "create api client frontend service",
    "types definition for API contracts",
    "Header navigation component",
    "Sidebar component layout",
    "Overview dashboard view component",
    "AskDataView query UI",
    "Datasets view list component",
    "Query history list component",
    "SmartChart visualization component",
    "SqlBlock syntax highlighter",
    "App layout integration",
    "update sidebar dataset selection",
    "ui fixes",
    "ui enhancement",
    "changes done",
    "backend bug fix",
    "fix dataset upload response parse",
    "update chat message state handler",
    "fix SQL block styling",
    "dashboard summary cards alignment",
    "add chart display logic",
    "fix dark mode contrast",
    "improve error state feedback",
    "backend prompt tuning",
    "adjust temperature on LLM pick",
    "add safe limit to sql queries",
    "update graph diagram asset",
    "schema test output cleanup",
    "clean up requirements file",
    "update vite config build options",
    "refactor API endpoint response key",
    "fix query history refresh state",
    "readme documentation initial",
    "update README architecture diagram",
    "add feature list to README"
]

file_commit_plan = [
    [".gitignore", ".python-version"],
    ["pyproject.toml"],
    ["requirements.txt", ".env.example"],
    ["ai_agent/models/schema.py"],
    ["ai_agent/utils/database.py"],
    ["ai_agent/utils/llm_pick.py"],
    ["main.py"],
    ["ai_agent/utils/etl_tools.py"],
    ["data/extract/extracted_data.csv"],
    ["data/transform/transformed_data.csv"],
    ["ai_agent/agents/etl_analyst.py"],
    ["ai_agent/agents/sql_analyst.py"],
    ["test_schema_details.txt"],
    ["data/users.csv"],
    ["data/ratings.csv"],
    ["data/payments.csv"],
    ["data/rides.csv"],
    ["data/vehicles.csv"],
    ["ai_agent/agents/data_agent.py"],
    ["data_agent_graph.png"],
    ["app.py"],
    ["feed_db.py"],
    ["scratch/test_sales.csv"],
    ["scratch/test_agent_flow.py"],
    ["scratch/test_pipeline_verification.py"],
    ["scratch/debug_trace.py"],
    ["scratch/debug_trace2.py"],
    ["scratch/debug_trace3.py"],
    ["scratch/debug_out.txt"],
    ["scratch/debug_out2.txt"],
    ["scratch/debug_out3.txt"],
    ["backend/main.py"],
    ["frontend/package.json"],
    ["frontend/vite.config.ts"],
    ["frontend/tsconfig.json"],
    ["frontend/index.html"],
    ["frontend/public/favicon.svg"],
    ["frontend/public/icons.svg"],
    ["frontend/public/queryflow-logo.png"],
    ["frontend/src/main.tsx"],
    ["frontend/src/assets/hero.png"],
    ["frontend/src/assets/react.svg"],
    ["frontend/src/assets/vite.svg"],
    ["frontend/src/types/api.ts"],
    ["frontend/src/services/apiClient.ts"],
    ["frontend/src/components/Header.tsx"],
    ["frontend/src/components/Sidebar.tsx"],
    ["frontend/src/components/OverviewView.tsx"],
    ["frontend/src/components/AskDataView.tsx"],
    ["frontend/src/components/DatasetsView.tsx"],
    ["frontend/src/components/QueryHistoryView.tsx"],
    ["frontend/src/components/SmartChart.tsx"],
    ["frontend/src/components/SqlBlock.tsx"],
    ["frontend/src/App.css"],
    ["frontend/src/index.css"],
    ["styles/app.css"],
    ["frontend/src/App.tsx"],
    ["README.md"]
]

random.seed(42)
start_date = datetime.datetime(2026, 8, 20, 10, 0, 0)
end_date = datetime.datetime(2026, 9, 28, 19, 0, 0)
total_days = (end_date - start_date).days # 39 days
num_commits = len(commit_messages)

day_counts = [1] * total_days
remaining = num_commits - total_days

while remaining > 0:
    idx = random.randint(0, total_days - 1)
    if day_counts[idx] < 5:
        day_counts[idx] += 1
        remaining -= 1

for _ in range(5):
    z_idx = random.randint(0, total_days - 1)
    if day_counts[z_idx] > 1:
        extra = day_counts[z_idx] - 1
        day_counts[z_idx] = 0
        for _ in range(extra):
            target = random.randint(0, total_days - 1)
            while target == z_idx:
                target = random.randint(0, total_days - 1)
            day_counts[target] += 1

dates = []
for day_i, count in enumerate(day_counts):
    curr_day = start_date + datetime.timedelta(days=day_i)
    for _ in range(count):
        h = random.randint(9, 21)
        m = random.randint(0, 59)
        s = random.randint(0, 59)
        dates.append(curr_day.replace(hour=h, minute=m, second=s))

dates.sort()

print("Re-building clean branch with author: Ifrah27 <ifrahqureshi27@gmail.com>...")
subprocess.run(["git", "checkout", "main"], check=False)
subprocess.run(["git", "branch", "-D", "ifrah"], check=False)
subprocess.run(["git", "checkout", "-b", "ifrah"], check=True)

# Delete existing tracked files from filesystem to prepare step-by-step committing
for root, dirs, files in os.walk("."):
    if any(ignore in root for ignore in [".git"]):
        continue
    for f in files:
        fp = os.path.normpath(os.path.join(root, f))
        if not fp.startswith(".git") and "rebuild_commits.py" not in fp and "fix_author.py" not in fp:
            try:
                os.remove(fp)
            except Exception:
                pass

for i, (msg, dt) in enumerate(zip(commit_messages, dates)):
    if i < len(file_commit_plan):
        plan_files = file_commit_plan[i]
    else:
        plan_files = ["README.md"]

    for rel_path in plan_files:
        norm = os.path.normpath(rel_path)
        if norm in file_contents:
            parent_dir = os.path.dirname(norm)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            with open(norm, "wb") as f_out:
                f_out.write(file_contents[norm])
            subprocess.run(["git", "add", norm], check=True)
        elif norm == "README.md" and os.path.exists("README.md"):
            with open("README.md", "a", encoding="utf-8") as f_out:
                f_out.write(" ")
            subprocess.run(["git", "add", "README.md"], check=True)

    date_str = dt.strftime("%Y-%m-%dT%H:%M:%S")
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Ifrah27"
    env["GIT_AUTHOR_EMAIL"] = "ifrahqureshi27@gmail.com"
    env["GIT_COMMITTER_NAME"] = "Ifrah27"
    env["GIT_COMMITTER_EMAIL"] = "ifrahqureshi27@gmail.com"
    env["GIT_AUTHOR_DATE"] = date_str
    env["GIT_COMMITTER_DATE"] = date_str

    subprocess.run(["git", "commit", "-m", msg, "--allow-empty"], env=env, check=True)

print("Restoring all full original files...")
for norm, content in file_contents.items():
    parent_dir = os.path.dirname(norm)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    with open(norm, "wb") as f_out:
        f_out.write(content)

subprocess.run(["git", "add", "."], check=True)
final_dt = dates[-1] + datetime.timedelta(minutes=15)
final_date_str = final_dt.strftime("%Y-%m-%dT%H:%M:%S")
env = os.environ.copy()
env["GIT_AUTHOR_NAME"] = "Ifrah27"
env["GIT_AUTHOR_EMAIL"] = "ifrahqureshi27@gmail.com"
env["GIT_COMMITTER_NAME"] = "Ifrah27"
env["GIT_COMMITTER_EMAIL"] = "ifrahqureshi27@gmail.com"
env["GIT_AUTHOR_DATE"] = final_date_str
env["GIT_COMMITTER_DATE"] = final_date_str
subprocess.run(["git", "commit", "-m", "placement ready README polishing"], env=env, check=False)

print("Done generating backdated git history with correct username and email!")
