import requests
import subprocess
import enum
import sys


if len(sys.argv) <= 1:
    raise Exception("Pass company name(github/gitlab username) as an argument")

company_name = sys.argv[1]
    

class GIT_PROVIDER(enum.Enum):
    GITHUB = "GITHUB"
    GITLAB = "GITLAB"
    BITBUCKET = "BITBUCKET"


# from which providers to search from
scan_repos: list[GIT_PROVIDER] = [
    GIT_PROVIDER.GITHUB,
    GIT_PROVIDER.GITLAB
    ]
if len(scan_repos) == 0:
    raise Exception("scan_repos not defined")
    

repos: dict[GIT_PROVIDER, list[str]] = {
   GIT_PROVIDER.GITHUB: [],
   GIT_PROVIDER.GITLAB: [],
   GIT_PROVIDER.BITBUCKET: []
}

results: dict[GIT_PROVIDER, list[str]] = {
   GIT_PROVIDER.GITHUB: [],
   GIT_PROVIDER.GITLAB: [],
   GIT_PROVIDER.BITBUCKET: []
}



# ---------- Generic ----------
def get_public_repo_url(repo_name, type):
    if type == GIT_PROVIDER.GITHUB:
      return f"https://github.com/{company_name}/{repo_name}"
    elif type == GIT_PROVIDER.GITLAB:
      return f"https://gitlab.com/{company_name}/{repo_name}.git"
    elif type == GIT_PROVIDER.BITBUCKET:
      return "" # TODO
    
def get_public_repo_list_url(type):
    if type == GIT_PROVIDER.GITHUB:
      return f"https://api.github.com/users/{company_name}/repos"
    elif type == GIT_PROVIDER.GITLAB:
      return f"https://gitlab.com/api/v4/users/{company_name}/projects"
    elif type == GIT_PROVIDER.BITBUCKET:
      return "" # TODO

def run_script(repo_name, git_provider: GIT_PROVIDER): 
    url = get_public_repo_url(repo_name, git_provider)
            
    result = subprocess.run(["sh", "./git-scanner.sh", url, repo_name, company_name, git_provider.value.lower()], stdout=subprocess.PIPE)
            
    decoded = result.stdout.decode('utf-8')
    return decoded

        

# ---------- Github ----------
def get_github_public_repos():
    url = get_public_repo_list_url(GIT_PROVIDER.GITHUB)
    response = requests.get(url)

    if response.status_code == 200:
        repositories = response.json()

        for repository in repositories:
            if repository['fork'] == False:
                repos[GIT_PROVIDER.GITHUB].append(repository['name'])
    else:
        print(f"No GitHub user found for {company_name}, response: {response.status_code}")

def check_github_repos():
    get_github_public_repos()
    
    if len(repos[GIT_PROVIDER.GITHUB]) != 0:
        print(f"Checking ${GIT_PROVIDER.GITHUB} repos") 
        for repo_name in repos[GIT_PROVIDER.GITHUB]:
            data = run_script(repo_name, GIT_PROVIDER.GITHUB)
            results[GIT_PROVIDER.GITHUB].append(data)      



# ---------- Gitlab ----------
def get_gitlab_public_repos():
    url = get_public_repo_list_url(GIT_PROVIDER.GITLAB)
    response = requests.get(url)


    if response.status_code == 200:
        repositories = response.json()

        for repository in repositories:
            repos[GIT_PROVIDER.GITLAB].append(repository['name'])
    else:
       print(f"No GitLab user found for {company_name}, response: {response.status_code}")
        
def check_gitlab_repos():
    get_gitlab_public_repos()
    
    if len(repos[GIT_PROVIDER.GITLAB]) != 0:
        print(f"Checking ${GIT_PROVIDER.GITLAB} repos") 
        for repo_name in repos[GIT_PROVIDER.GITLAB]:
            data = run_script(repo_name, GIT_PROVIDER.GITLAB)
            results[GIT_PROVIDER.GITLAB].append(data)   
    

def generateTldr(): 
     result = subprocess.run(["ls", f"./data/{company_name}/results"], stdout=subprocess.PIPE)
     decodedResults = result.stdout.decode('utf-8')
     
     filenames = decodedResults.splitlines()
     
     lines = [
         f"----- Git leaks for {company_name} -----"
     ]

     if(len(filenames) > 0):
        for fileName in filenames:
            file = open(f"./data/{company_name}/results/{fileName}", "r")
            contents = file.read().splitlines()
            
            fileParts = fileName.split("_")
            
            indexes = [i for i in range(len(contents)) if contents[i].startswith("Secret")]

            
            lines.append(f"Git provider: {fileParts[1]}")
            for index in indexes:
                lines.append(f"Found secret: {contents[index]}" )
            lines.append('\n')
            
     else: 
        lines.append("No leaks found")
        
     with open(f"{company_name}_tldr.txt", "w") as file:
            file.writelines(line + "\n" for line in lines)
     file.close()
     
     subprocess.run(["mv", f"{company_name}_tldr.txt", f"./data/{company_name}"])


def init():
    if GIT_PROVIDER.GITHUB in scan_repos:
        check_github_repos()

    if GIT_PROVIDER.GITLAB in scan_repos:
        check_gitlab_repos()

    if GIT_PROVIDER.BITBUCKET in scan_repos:
        raise Exception("BITBUCKET Not supported yet")
        # TODO: check_gitlab_repos()
        
    generateTldr()
        
init()
