import os
import re
import sys
import requests
from pathlib import Path

# --- Configuration ---
# Get inputs from environment variables set by the GitHub Action
API_KEY = os.getenv("GEMINI_API_KEY")
DOMAIN = os.getenv("DOMAIN")
NUM_TOPICS = os.getenv("NUM_TOPICS")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("REPO_NAME")
DATASET_FILE = Path("golden_dataset.md")

# --- Helper Functions ---
def get_existing_topics(domain: str) -> list[str]:
    """Parses the markdown file to find existing topics for a specific domain."""
    print(f"🔍 Reading existing topics for '{domain}' from {DATASET_FILE}...")
    try:
        content = DATASET_FILE.read_text()
        # Find the markdown table for the specific domain
        # This regex looks for a ### Domain header, then captures the table content until the next ### header or end of file
        domain_section_pattern = re.compile(rf"### {domain}\s*?\n(.*?)(?=\n###|\Z)", re.DOTALL | re.IGNORECASE)
        match = domain_section_pattern.search(content)

        if not match:
            print(f"⚠️ No section found for domain '{domain}'.")
            return []

        table_content = match.group(1)
        # Extract prompt text from the second column of each table row
        prompt_pattern = re.compile(r"\|\s*rub_\w+_\d+\s*\|\s*(.*?)\s*\|", re.DOTALL)
        topics = prompt_pattern.findall(table_content)
        print(f"✅ Found {len(topics)} existing topics.")
        return [topic.strip() for topic in topics]
    except FileNotFoundError:
        print(f"⚠️ Dataset file not found at '{DATASET_FILE}'.")
        return []

def generate_new_topics(existing_topics: list[str]) -> str:
    """Calls the Gemini API to generate new, unique topics."""
    print(f"🤖 Calling LLM to generate {NUM_TOPICS} new topics...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.0-pro:generateContent?key={API_KEY}"    
    # Create a numbered list of existing topics to include in the prompt
    existing_topics_str = "\n".join(f"- {topic}" for topic in existing_topics)

    prompt = (
        f"You are an expert curriculum designer for university-level courses in the {DOMAIN} domain.\n\n"
        f"Generate exactly {NUM_TOPICS} new and unique essay topics suitable for undergraduate students. "
        "The topics must be different from the following existing topics:\n\n"
        f"--- EXISTING TOPICS ---\n{existing_topics_str}\n---------------------\n\n"
        "Provide the output ONLY as a numbered list with each topic on a new line. Do not include any other text, title, or preamble."
    )

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status() # Raise an exception for bad status codes
    
    # Extract the text content from the response
    result = response.json()
    new_topics_text = result['candidates'][0]['content']['parts'][0]['text']
    print("✅ LLM response received.")
    return new_topics_text.strip()

def create_github_issue(new_topics: str):
    """Creates a new issue in the GitHub repository with the generated topics."""
    print(f"📝 Creating GitHub issue in repository '{REPO_NAME}'...")
    url = f"https://api.github.com/repos/{REPO_NAME}/issues"
    
    issue_title = f"✅ New Topics Generated for: {DOMAIN}"
    issue_body = (
        f"Hi team,\n\n"
        f"The topic generation workflow has created **{NUM_TOPICS}** new topic(s) for the **{DOMAIN}** domain. "
        "Please review and use them to create new dataset entries.\n\n"
        "--- \n\n"
        f"{new_topics}"
    )
    
    payload = {
        "title": issue_title,
        "body": issue_body,
        "labels": ["new-topics", f"domain:{DOMAIN.lower()}"]
    }
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    issue_url = response.json()['html_url']
    print(f"✅ Successfully created issue: {issue_url}")

# --- Main Execution ---
if __name__ == "__main__":
    if not all([API_KEY, DOMAIN, NUM_TOPICS, GITHUB_TOKEN, REPO_NAME]):
        sys.exit("❌ Error: Missing one or more required environment variables.")
    
    try:
        existing = get_existing_topics(DOMAIN)
        generated_text = generate_new_topics(existing)
        create_github_issue(generated_text)
        print("\n🎉 Workflow completed successfully!")
    except Exception as e:
        sys.exit(f"❌ An error occurred: {e}")