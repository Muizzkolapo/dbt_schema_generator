import os
import json
import openai
import requests

# Initialize OpenAI API
openai.api_key = os.environ.get("GPT3_API_KEY")

def post_comment(pr_id, comment):
    url = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/issues/{pr_id}/comments"
    headers = {
        "Authorization": f"token {os.environ['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "body": comment
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 201:
        print(f"Failed to post comment: {response.text}")

def get_pr_files(pr_id):
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





def extract_changed_lines(patch_text):
    # Extract lines that start with + (indicating additions or modifications)
    changed_lines = [line[1:] for line in patch_text.split('\n') if line.startswith('+ ') and not line.startswith('+++ ')]
    return '\n'.join(changed_lines)
'''
def review_code(pr_id):
    files = get_pr_files(pr_id)
    for file in files:
        patch_text = file.get('patch', 'No changes available')
        
        # Extract changed lines from the patch text
        code_snippet = extract_changed_lines(patch_text)

        # If there are no changed lines (might be a file deletion or renaming), skip to the next file
        if not code_snippet.strip():
            continue

        response = openai.Completion.create(
          engine="davinci",
          prompt=f"Review the following code snippet:\n\n{code_snippet}\n",
          max_tokens=150
        )
        
        review = f"Review for file `{file['filename']}`:\n\n" + response.choices[0].text.strip()
        post_comment(pr_id, review)
'''

def review_code(pr_id):
    files = get_pr_files(pr_id)
    for file in files:
        filename = file['filename']
        status = file['status']  # The status of the file ('added', 'removed', or 'modified')
        changes = file['changes']  # The number of changes made in the file
        additions = file['additions']  # The number of lines added
        deletions = file['deletions']  # The number of lines deleted

        print(f"File: {filename}")
        print(f"Status: {status}")
        print(f"Total Changes: {changes}")
        print(f"Lines Added: {additions}")
        print(f"Lines Removed: {deletions}\n")






if __name__ == "__main__":
    with open(os.environ["GITHUB_EVENT_PATH"], "r") as f:
        event_data = json.load(f)
        pr_id = event_data["pull_request"]["number"]
    review_code(pr_id)
