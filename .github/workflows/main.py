import subprocess
import requests
import os
import shutil

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

def dl_img(filepath, username):
    url = f'https://tryhackme-badges.s3.amazonaws.com/{username}.png'
    path = filepath

    with requests.get(url, stream=True) as response:
        with open(path, 'wb') as file:
            shutil.copyfileobj(response.raw, file)

    os.environ["GIT_COMMITTER_NAME"] = COMMITTER_USERNAME
    os.environ["GIT_COMMITTER_EMAIL"] = COMMITTER_EMAIL
    os.environ["GIT_AUTHOR_NAME"] = COMMITTER_USERNAME
    os.environ["GIT_AUTHOR_EMAIL"] = COMMITTER_EMAIL

    exec_command('git', ['add', filepath])
    exec_command('git', ['commit', '-m', COMMIT_MESSAGE])
    exec_command('git', ['push', 'origin', 'HEAD'])

try:
    dl_img(FILEPATH, THM_USERNAME)
except Exception as e:
    print('nothing to commit')
