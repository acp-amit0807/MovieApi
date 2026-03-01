import os
import requests
import json

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

REPO = os.getenv("GITHUB_REPOSITORY")
PR_NUMBER = os.getenv("GITHUB_REF").split("/")[-1]

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_changed_files():
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}/files"
    response = requests.get(url, headers=headers)
    return response.json()

def call_llm(code):
    prompt = open("review_prompt.txt").read()

    payload = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": code}
        ]
    }

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        data=json.dumps(payload)
    )

    return response.json()["choices"][0]["message"]["content"]

def post_comment(review):
    url = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
    data = {"body": review}
    requests.post(url, headers=headers, json=data)

def main():
    try:
        files = get_changed_files()
        code_content = ""

        for file in files:
            if file["filename"].endswith(".cs"):
                code_content += f"\n\nFile: {file['filename']}\n"
                code_content += file.get("patch", "")

        if not code_content:
            print("No C# files changed.")
            return

        review = call_llm(code_content)
        post_comment(review)

    except Exception as e:
        print("LLM failed but not breaking CI:", str(e))

if __name__ == "__main__":
    main()