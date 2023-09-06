import os
import json
import openai
import requests


# Set your OpenAI API key
openai.api_key = os.environ.get('OPENAI_API_KEY')



def post_comment(pr_id: int, comment: str) -> None:
    """Post a comment on a GitHub PR."""
    url = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/issues/{pr_id}/comments"
    headers = {
        "Authorization": f"token {os.environ['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"body": comment}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 201:
        print(f"Failed to post comment: {response.text}")

def get_pr_files(pr_id: int) -> list:
    """Get the files from a GitHub PR."""
    url = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/pulls/{pr_id}/files"
    headers = {
        "Authorization": f"token {os.environ['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get PR files: {response.text}")
        return []

def extract_changed_lines(patch_text: str) -> tuple:
    """Extract the added and deleted lines from patch text."""
    lines_added = [line[1:] for line in patch_text.split('\n') if line.startswith('+ ') and not line.startswith('+++ ')]
    lines_deleted = [line[1:] for line in patch_text.split('\n') if line.startswith('- ') and not line.startswith('--- ')]
    return '\n'.join(lines_added), '\n'.join(lines_deleted)

def review_code(pr_id: int) -> tuple:
    """Review the code in a GitHub PR."""
    files = get_pr_files(pr_id)
    num_files_changed = len(files)
    comment_body = f"The PR has {num_files_changed} files changed:\n\n"
    for file in files:
        filename = file['filename']
        status = file['status']
        changes = file['changes']
        additions = file['additions']
        deletions = file['deletions']
        patch_text = file.get('patch', 'No changes available')
        lines_added, lines_deleted = extract_changed_lines(patch_text)
        comment_body += f"File: {filename}\nStatus: {status}\nTotal Changes: {changes}\nLines Added: {additions}\nLines Removed: {deletions}\nCode Added:\n```\n{lines_added}\n```\nCode Removed:\n```\n{lines_deleted}\n```\n\n"
    post_comment(pr_id, comment_body)
    return pr_id, comment_body

def analyze_code_change(pr_id: int, comment: str, language: str = "Python") -> str:
    """Analyze a code change using OpenAI API."""
    prompt = f"The following code change is in {language} language:\n\n{comment}\n\nWhat does this code change do?"
    try:
        response = openai.Completion.create(engine="davinci", prompt=prompt, max_tokens=50)
        description = response.choices[0].text.strip()
        return description
    except Exception as e:
        print(f"Error: {e}")
        return "Error in analyzing the code"

if __name__ == "__main__":
    with open(os.environ["GITHUB_EVENT_PATH"], "r") as f:
        event_data = json.load(f)
        pr_id = event_data["pull_request"]["number"]
        pr_id, comment_body = review_code(pr_id)
        analysis_result = analyze_code_change(pr_id, comment_body)
        post_comment(pr_id, analysis_result)
