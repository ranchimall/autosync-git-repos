import requests 
import json 
import pdb 
import os 
from operator import itemgetter 
import configparser 

config = configparser.ConfigParser()
config.read('config.ini')

GIT_USERNAME = config['DEFAULT']['GIT_USERNAME']
GIT_ORG_NAME = config['DEFAULT']['GIT_ORG_NAME']
GITLAB_GROUP_ID = config['DEFAULT']['GITLAB_GROUP_ID']
GITLAB_API_TOKEN = config['DEFAULT']['GITLAB_API_TOKEN']
CODEBERG_API_TOKEN = config['DEFAULT']['CODEBERG_API_TOKEN']
GITHUB_API_TOKEN = config['DEFAULT']['GITHUB_API_TOKEN']

current_working_dir = os.getcwd()

def repo_cloning():
    directory_data = {}

    GITHUB_HEADERS =  {
        'Authorization': "token " + GITHUB_API_TOKEN,
    }
    response = requests.get(f'https://api.github.com/orgs/{GIT_ORG_NAME}/repos?page=1&per_page=1000&type=all', headers=GITHUB_HEADERS)
    if response.status_code == 200:
        response_data = response.json()
        for i in range(len(response_data)):
            
            #if response_data[i]['name'] in ['app-guides', "electrumx"]:
            name, private, visibility, html_url, description = itemgetter('name', 'private', 'visibility', 'html_url', 'description')(response_data[i])
            directory_data[i] = {
                'name': name,
                'private': private,
                'visibility': visibility,
                'html_url': html_url,
                'description': description
            }
            
            if not os.path.isdir(f"{current_working_dir}/{directory_data[i]['name']}"):
                directory_data[i]['available_locally'] = False
                os.system(f"git clone {directory_data[i]['html_url']}")
            else:
                directory_data[i]['available_locally'] = True
        print('Completed cloning')
    return directory_data
    
def create_repos_gitlab(directory_data):
    for key in directory_data.keys():
        name, private, visibility, html_url, description = itemgetter('name', 'private', 'visibility', 'html_url', 'description')(directory_data[key])
        headers = { 'PRIVATE-TOKEN': GITLAB_API_TOKEN }
        json_data = {
                'name': name,
                'description': description,
                'path': name,
                'initialize_with_readme': 'false',
                'visibility': visibility,
                'namespace_id': GITLAB_GROUP_ID
            }
        response = requests.post('https://gitlab.com/api/v4/projects/', headers=headers, json=json_data)

def setting_remote_repositories(directory_data):
    for key in directory_data.keys():
        if directory_data[key]['available_locally'] == False:
            repo_name = directory_data[key]['name']
            print(f'Setting remote repositores for repo_name')
            os.system(f"cd {current_working_dir}/{repo_name} && git remote set-url origin --add https://codeberg.org/{GIT_ORG_NAME}/{repo_name}.git && git remote set-url origin --add https://gitlab.com/{GIT_ORG_NAME}/{repo_name}.git")

def pull_push_code(directory_data):
    for key in directory_data.keys():
        repo_name = directory_data[key]['name']
        os.system(f"cd {current_working_dir}/{repo_name} && git pull && git push https://{GITHUB_API_TOKEN}@github.com/{GIT_ORG_NAME}/{repo_name}.git && git push https://{GIT_USERNAME}:{GITLAB_API_TOKEN}@gitlab.com/{GIT_ORG_NAME}/{repo_name}.git")
        # Codeberg 
        try:
            os.system(f"cd {current_working_dir}/{repo_name} && git pull && git push https://{CODEBERG_API_TOKEN}@codeberg.org/{GIT_ORG_NAME}/{repo_name}.git")
        except:
            print("Couldn't process Codeberg")


if __name__ == '__main__':
    dir_data = repo_cloning()
    create_repos_gitlab(dir_data)
    setting_remote_repositories(dir_data)
    pull_push_code(dir_data)