import requests


def get_or_create_gitlab_project(gitlab_url, token, username, group, name):
    api_url = f"{gitlab_url}/api/v4"
    headers = {"PRIVATE-TOKEN": token}


    if group != '':
        if not check_groups(gitlab_url, token, group):
            print(f"Group '{group}' does not exist on Gitlab. Please create it first.")
            exit()

    try:
        search_url = f"{api_url}/groups/{group}/projects?search={name}" if group != '' else f"{api_url}/projects?search={name}"
        r = requests.get(search_url, headers=headers)
        r.raise_for_status()

        if r.json() != []:
            print("Project already exist on Gitlab:", r.json()[0]["web_url"])
            return r.json()[0]

        url = f"{api_url}/projects"
        url = url.replace("https://", f"https://{username}:{token}@")
        data = {"name": name}
        if group:
            group_url = f"{api_url}/groups/{group}"
            group_resp = requests.get(group_url, headers=headers)
            group_resp.raise_for_status()
            data["namespace_id"] = group_resp.json()["id"]

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print("Gitlab project created :", response.json()["web_url"])
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error during the communication to Gitlab: {e}")
        print("Verify your connection, URL, tokens and permissions.")
        raise

def check_groups(gitlab_url, token, group):
    api_url = f"{gitlab_url}/api/v4"
    headers = {"PRIVATE-TOKEN": token}

    url = f"{api_url}/groups/{group}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return False
    return True
