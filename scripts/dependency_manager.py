import json
import logging

class DependencyManager:
    def __init__(self, client):
        self.client = client

    def _is_openknx_dependency(self, url):
        # TODO check if the exclusion of external libs here is a clean solution
        return url.startswith("https://github.com/OpenKNX/")

    def fetch_dependencies(self, repo):
        dependencies_url = f"https://raw.githubusercontent.com/OpenKNX/{repo['name']}/{repo['default_branch']}/dependencies.txt"
        response = self.client.get_response(dependencies_url, True)
        if response is None:
            return {}
        dependencies_map = {}
        lines = response.text.splitlines()
        if lines:
            for line in lines[1:]:  # Skip the header
                parts = line.split()
                if len(parts) == 4:
                    commit, branch, path, url = parts
                    dep_name = url.split('/')[-1].replace('.git', '')  # Ableiten des Repo-Namens aus der URL
                    if self._is_openknx_dependency(url):
                        dependencies_map[dep_name] = {
                            "commit": commit,
                            "branch": branch,
                            "path": path,
                            "url": url,
                            # TODO rename to dep_name
                            "depName": dep_name
                        }
                else:
                    logging.warning(f"Invalid dependencies.txt format in {repo['name']} line '{line}'")
        return dependencies_map

    def fetch_all_dependencies(self, repos_data):
        all_dependencies = {}
        for repo in repos_data:
            dependencies = self.fetch_dependencies(repo)
            if dependencies:
                all_dependencies[repo['name']] = dependencies
        with open('dependencies.json', 'w') as outfile:
            json.dump(all_dependencies, outfile, indent=4)
        return all_dependencies