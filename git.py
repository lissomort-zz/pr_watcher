import ConfigParser
import datetime
import json
import requests

config = ConfigParser.RawConfigParser()
config.read("./config.yml")

API_URL = "https://api.github.com/repos/"
PULL_QUERY = "pulls"

QUERY_PARAMS = "?per_page=100&state=open"

PAGE_SAMPLE = "&page={}"

PAGES = 3

def get_all_prs():
    """
    return all open PRs of given repo
    """

    headers = {'authorization': 'token %s' % config.get('github', 'api_token')}
    url = "{api_url}{company}/{repo}/{query}{params}".format(
        api_url=API_URL,
        company=config.get('github', 'company'),
        repo=config.get('github', 'repo'),
        query=PULL_QUERY,
        params=QUERY_PARAMS)

    all_prs = []
    for page in range(1, PAGES+1):
        req = requests.get(
            url + PAGE_SAMPLE.format(str(page)), 
            headers=headers)
        if req.status_code == 200:
            all_prs += json.loads(req.content)

    return all_prs


def filter_by_team(pr_list):
    """
    filter the PRs list by authors from config
    """

    def create_date_update_line(datetime_str):
        """
        Return datetime in string <Update at <date> <time> ({} hours ago)>
        """
        dt_obj = datetime.datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%SZ')
        date_upd = dt_obj.date()
        time_upd = dt_obj.time()
        time_delta = datetime.datetime.now() - dt_obj
        return "Last updated: {date} at {time} ({delta} ago)".format(
            date=str(date_upd),
            time=str(time_upd),
            delta=str(time_delta)
        )

    def create_pr_line(pr_dict):
        """
        create a description line from PR info
        """

        return "PR#{number} {title} {tags} {updated}".format(
            number=pr['number'],
            title=pr['title'][:30] + "...",
            tags=''.join(['['+tag['name']+']' for tag in pr['labels']]),
            updated=create_date_update_line(pr['updated_at'])
        )


    author_list = config.get('github', 'authors').split(',')
    teams_pr = [pr for pr in pr_list if pr['user']['login'] in author_list]

    return_dict = dict()
    for pr in teams_pr:
        author = pr['user']['login']
        if author in return_dict.keys():
            return_dict[author].append(create_pr_line(pr))
        else:
            return_dict[author] = [create_pr_line(pr)]
    return return_dict

def get_pr_list():
    all_prs =  get_all_prs()
    return filter_by_team(all_prs)


if __name__ == "__main__":
    for author in get_pr_list():
        print(author)
        for pr in get_pr_list()[author]:
            print(pr)

