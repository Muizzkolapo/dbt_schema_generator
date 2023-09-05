
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

def review_code(pr_id):
    # TODO:  changes from the PR
    code_snippet = "PLACEHOLDER_FOR_CODE_FROM_PR"

    response = openai.Completion.create(
      engine="davinci",
      prompt=f"Review the following code snippet:\n\n{code_snippet}\n",
      max_tokens=150
    )
    
    review = response.choices[0].text.strip()
    post_comment(pr_id, review)

if __name__ == "__main__":
    with open(os.environ["GITHUB_EVENT_PATH"], "r") as f:
        event_data = json.load(f)
        pr_id = event_data["pull_request"]["number"]

    review_code(pr_id)
