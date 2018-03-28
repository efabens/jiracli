#!/usr/bin/env python3

from jira import JIRA
import json
import os
import getpass, argparse


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


class Password(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        if values is None:
            values = os.getenv('JIRA_PASSWORD', 'foo')
            if values == 'foo':
                values = getpass.getpass()

        setattr(namespace, self.dest, values)


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


def getAppropriateSprint(which_types):
    # Use the get boards method to determine which board you want sprint info
    # for
    boards = config['board']
    sprints = []
    for i in boards:
        sprints += jira.sprints(i)

    active = [i for i in sprints if i.state == 'active']
    future = [i for i in sprints if i.state == 'future']
    closed = [i for i in sprints if i.state == 'closed']

    return_list = []
    if 'c' in which_types:
        return_list += closed
    if 'a' in which_types:
        return_list += active
    if 'f' in which_types:
        return_list += future
    if not return_list:
        raise RuntimeError("No sprints were found matching specified criteria")
    return return_list


def retrieveIssues(jira, assignee, which_types):
    sprints = getAppropriateSprint(which_types)
    for sprint in sprints:
        issues = jira.search_issues(
            'assignee=' + assignee + ' and sprint=' + str(sprint.id))
        if issues:
            doIssues(sprint, issues)


def getAllIssues(jira, which_types):
    sprints = getAppropriateSprint(which_types)
    for sprint in sprints:
        issues = jira.search_issues(
            ' sprint=' + str(sprint.id))
        doIssues(sprint, issues)


def getConfig():
    with open(os.path.dirname(__file__) + "/jira.conf", 'r') as conf:
        return json.load(conf)


def getJira(user, password):
    options = {
        'server': 'https://' + config['subdomain'] + '.' + config['domain'],
        'agile_rest_path': "agile"
    }

    return JIRA(options, basic_auth=(user, password))


def getBoards(jira):
    boards = sorted(jira.boards(), key=lambda x: x.name)
    for i in boards:
        print(bcolors.HEADER + str(i.id) + bcolors.ENDC, i.name)


def manPage():
    with open(os.path.dirname(__file__) + "/readme.md", 'r') as manpage:
        print(manpage.read())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='List current tickets from jira')

    parser.add_argument('user', help='Username for login')
    parser.add_argument(
        'password', action=Password, nargs='?',
        help='Password. Can be specified as second argument or via prompt ' +
             'if not provided')
    parser.add_argument(
        '--for-user', '-f', dest='t_user', default='currentUser()',
        help='User to retrieve issues related to')
    parser.add_argument(
        '--unassigned', '-u', dest='show_unassigned', action='store_true',
        help='Show unassigned tickets in the current sprint')
    parser.add_argument(
        '-b', dest='board', action='store_true', help='Jira board')
    parser.add_argument(
        '-a', dest='returnall', action='store_true', help='Return all issues ' +
                                                          'in the current sprint')
    parser.add_argument(
        '-w', '--which', dest='board_type', default='a',
        help='Set which types of sprints should be returned, currently supported is "a" : active, "f": future,'
             ' "c": closed. Values are additive. Boards will always be displayed in order Past, Active, Future. Within '
             'sections order is not specified. Using "c" can take a long time')
    args = parser.parse_args()

    config = getConfig()
    jira = getJira(args.user, args.password)

    if args.show_unassigned:
        retrieveIssues(jira, 'null')
    elif args.board:
        getBoards(jira)
    elif args.returnall:
        getAllIssues(jira, args.board_type)
    else:
        retrieveIssues(jira, args.t_user, args.board_type)
