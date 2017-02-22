from jira import JIRA
import sys
import json
import os


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def customColor(r, g, b):
        return '\033[38;2;' + str(r) + ";" + str(g) + ";" + str(b) + 'm'


def doIssues(sprint, issues):

    concatName = sprint.name + ' | ' + str(sprint.id) + ' | ' + sprint.state
    print(bcolors.HEADER + concatName + bcolors.ENDC)
    for i in issues:
        status = i.fields.status.name
        key = "[" + i.key + "] " + status + " "
        summary = i.fields.summary
        end = bcolors.ENDC
        if status in ["Resolved", "Ready to Test"]:
            color = bcolors.customColor(46, 139, 87)
        elif status == "To Do":
            color = bcolors.customColor(255, 140, 0)
        elif status == "Done":
            color = bcolors.customColor(30, 144, 255)
        elif status == "In Progress":
            color = bcolors.customColor(186, 85, 211)
        else:
            color = ''
            end = ''
        print(color + key + end + summary)


def getAppropriateSprint():
    # Use the get boards method to determine which board you want sprint info
    # for
    sprints = jira.sprints(config["board"])

    active = [i for i in sprints if i.state == 'active']
    future = [i for i in sprints if i.state == 'future']

    if active:
        return active[0]
    elif future:
        return future[0]
    else:
        raise RuntimeError("No active or future sprints could be found")


def retrieveIssues(jira, assignee):
    sprint = getAppropriateSprint()
    issues = jira.search_issues(
        'assignee=' + assignee + ' and sprint=' + str(sprint.id))
    doIssues(sprint, issues)


def retrievePersonalIssues(jira):
    sprint = getAppropriateSprint()

    issues = jira.search_issues(
        'assignee = currentUser() and' +
        ' sprint=' + str(sprint.id))
    doIssues(sprint, issues)


def getAllIssues(jira):
    sprint = getAppropriateSprint()

    issues = jira.search_issues(
        ' sprint=' + str(sprint.id))
    doIssues(sprint, issues)


def getConfig():
    with open(os.path.dirname(__file__) + "/jira.conf", 'r') as conf:
        return json.load(conf)


def getJira():
    options = {
        'server': 'https://' + config['subdomain'] + '.' + config['domain'],
        'agile_rest_path': "agile"
    }
    return JIRA(options, basic_auth=(sys.argv[1], sys.argv[2]))


def getBoards(jira):
    boards = sorted(jira.boards(), key=lambda x: x.name)
    for i in boards:
        print(bcolors.HEADER + str(i.id) + bcolors.ENDC, i.name)


def manPage():
    with open(os.path.dirname(__file__) + "/readme.md", 'r') as manpage:
        print(manpage.read())


if __name__ == '__main__':
    config = getConfig()
    if ('-h' in sys.argv):
        manPage()
    elif len(sys.argv) <= 3:
        jira = getJira()
        retrieveIssues(jira, "currentUser()")
    elif len(sys.argv) == 4 and sys.argv[3] == '-u':
        jira = getJira()
        retrieveIssues(jira, 'null')
    elif len(sys.argv) == 5 and sys.argv[3] == '-u':
        jira = getJira()
        retrieveIssues(jira, sys.argv[4])
    elif len(sys.argv) == 4 and sys.argv[3] == '-b':
        jira = getJira()
        getBoards(jira)
    elif len(sys.argv) == 4 and sys.argv[3] == '-a':
        jira = getJira()
        getAllIssues(jira)
    else:
        print('Options passed in are not valid')
