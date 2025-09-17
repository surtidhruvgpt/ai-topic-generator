"""
This script automates the generation of new essay topics using the Google Gemini API
and creates a new issue in a GitHub repository with the generated topics.

This script is designed to be run as part of a GitHub Actions workflow.
It requires the following environment variables to be set:
    - GEMINI_API_KEY: The API key for the Google Gemini service.
    - GITHUB_TOKEN: A GitHub token with permissions to create issues.
    - DOMAIN: The academic domain for which to generate topics.
    - NUM_TOPICS: The number of new topics to generate.
    - REPO_NAME: The name of the GitHub repository (e.g., 'owner/repo').
"""

import os
import re
import sys
from pathlib import Path

import google.generativeai as genai
import requests
from google.api_core import exceptions as google_exceptions

# --- Constants ---
MODEL_NAME = "gemini-1.5-flash"
DATASET_FILE_PATH = Path("golden_dataset.md")
GITHUB_API_BASE_URL = "https://api.github.com"

PROMPT_TEMPLATE = """
You are an expert curriculum designer for university-level courses in the {domain} domain.

Generate exactly {num_topics} new and unique essay topics suitable for undergraduate students.
The topics must be different from the following existing topics:

--- EXISTING TOPICS ---
{existing_topics}
---------------------

Provide the output ONLY as a numbered list with each topic on a new line.
Do not include any other text, title, or preamble.
"""


def get_existing_topics(domain: str) -> list[str]:
    """
    Parses the markdown dataset file to find existing topics for a specific domain.

    Args:
        domain: The academic domain to search for (e.g., 'Psychology').

    Returns:
        A list of existing topic strings. Returns an empty list if the file or
        domain section is not found.
    """
    print(f"🔍 Reading existing topics for '{domain}' from {DATASET_FILE_PATH}...")
    try:
        content = DATASET_FILE_PATH.read_text(encoding="utf-8")
        # Regex to find a ### Domain header and capture the following table
        pattern = rf"### {domain}\s*?\n(.*?)(?=\n###|\Z)"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

        if not match:
            print(f" No section found for domain '{domain}'.")
            return []

        table_content = match.group(1)
        # Regex to extract the prompt text from the second column of a markdown table
        prompt_pattern = re.compile(r"\|\s*rub_\w+_\d+\s*\|\s*(.*?)\s*\|", re.DOTALL)
        topics = prompt_pattern.findall(table_content)
        print(f" Found {len(topics)} existing topics.")
        return [topic.strip() for topic in topics]
    except FileNotFoundError:
        print(f" Dataset file not found at '{DATASET_FILE_PATH}'.")
        return []


def generate_new_topics(domain: str, num_topics: str, existing_topics: list[str]) -> str:
    """
    Generates new topics using the Google Gemini API.

    Args:
        domain: The academic domain for the new topics.
        num_topics: The number of topics to generate.
        existing_topics: A list of topics to avoid duplicating.

    Returns:
        A string containing the newly generated topics, formatted as a list.
    """
    print(f" Calling LLM to generate {num_topics} new topics...")
    model = genai.GenerativeModel(MODEL_NAME)
    
    existing_topics_str = "\n".join(f"- {topic}" for topic in existing_topics)
    prompt = PROMPT_TEMPLATE.format(
        domain=domain,
        num_topics=num_topics,
        existing_topics=existing_topics_str,
    )

    try:
        response = model.generate_content(prompt)
        print(" LLM response received.")
        return response.text.strip()
    except google_exceptions.GoogleAPICallError as e:
        print(f" An error occurred with the Google API: {e}")
        raise
    except Exception as e:
        print(f" An unexpected error occurred during topic generation: {e}")
        raise


def create_github_issue(repo_name: str, token: str, domain: str, num_topics: str, new_topics: str):
    """
    Creates a new issue in the specified GitHub repository.

    Args:
        repo_name: The name of the repository (e.g., 'owner/repo').
        token: The GitHub token for authentication.
        domain: The academic domain of the topics.
        num_topics: The number of topics generated.
        new_topics: The text content of the new topics.
    """
    print(f" Creating GitHub issue in repository '{repo_name}'...")
    url = f"{GITHUB_API_BASE_URL}/repos/{repo_name}/issues"
    
    issue_title = f" New Topics Generated for: {domain}"
    issue_body = (
        f"Hi team,\n\n"
        f"The topic generation workflow has created **{num_topics}** new topic(s) "
        f"for the **{domain}** domain.\n\n"
        "--- \n\n"
        f"{new_topics}"
    )
    
    payload = {
        "title": issue_title,
        "body": issue_body,
        "labels": ["new-topics", f"domain:{domain.lower()}"],
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        issue_url = response.json()['html_url']
        print(f" Successfully created issue: {issue_url}")
    except requests.exceptions.HTTPError as e:
        print(f" HTTP Error creating GitHub issue: {e.response.status_code} {e.response.text}")
        raise
    except requests.exceptions.RequestException as e:
        print(f" A network error occurred while creating the GitHub issue: {e}")
        raise


def main():
    """Main function to orchestrate the topic generation workflow."""
    # --- Load Configuration from Environment Variables ---
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    github_token = os.getenv("GITHUB_TOKEN")
    domain = os.getenv("DOMAIN")
    num_topics = os.getenv("NUM_TOPICS")
    repo_name = os.getenv("REPO_NAME")

    if not all([gemini_api_key, github_token, domain, num_topics, repo_name]):
        sys.exit(" Error: Missing one or more required environment variables.")

    try:
        genai.configure(api_key=gemini_api_key)
    except Exception as e:
        sys.exit(f" Error configuring Google AI SDK: {e}")

    # --- Run Workflow ---
    try:
        existing = get_existing_topics(domain)
        generated_text = generate_new_topics(domain, num_topics, existing)
        create_github_issue(repo_name, github_token, domain, num_topics, generated_text)
        print("\n Workflow completed successfully!")
    except Exception as e:
        sys.exit(f" A top-level error occurred during workflow execution: {e}")


if __name__ == "__main__":
    main()