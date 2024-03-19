import requests
import os
import subprocess

GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
FILEPATH = os.getenv("image_path")
THM_USERNAME = os.getenv("username")
COMMITTER_USERNAME = os.getenv("committer_username")
COMMITTER_EMAIL = os.getenv("committer_email")
COMMIT_MESSAGE = os.getenv("commit_message")

def exec_command(cmd, args=[], options={}):
    output_data = ''
    try:
        process = subprocess.Popen([cmd] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        output_data, _ = process.communicate()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd)
    except Exception as e:
        return {"code": 1, "outputData": str(e)}
    return {"code": process.returncode, "outputData": output_data}

def download_image(filepath, username):
    url = f'https://tryhackme-badges.s3.amazonaws.com/{username}.png'
    with requests.get(url, stream=True) as response:
        with open(filepath, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

def update_image(filepath):
    # Check if the image exists in the repository
    if os.path.exists(filepath):
        # If it exists, overwrite it
        exec_command('git', ['checkout', '--', filepath])
    else:
        # If it doesn't exist, add it
        exec_command('git', ['add', filepath])

def commit_and_push(username, commit_message):
    exec_command('git', ['commit', '-m', commit_message])
    exec_command('git', ['push', 'origin', 'HEAD'])

try:
    download_image(FILEPATH, THM_USERNAME)
    update_image(FILEPATH)
    os.environ["GIT_COMMITTER_NAME"] = COMMITTER_USERNAME
    os.environ["GIT_COMMITTER_EMAIL"] = COMMITTER_EMAIL
    os.environ["GIT_AUTHOR_NAME"] = COMMITTER_USERNAME
    os.environ["GIT_AUTHOR_EMAIL"] = COMMITTER_EMAIL
    commit_and_push(THM_USERNAME, COMMIT_MESSAGE)
except Exception as e:
    print('nothing to commit')
