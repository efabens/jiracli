#!/usr/bin/env python3

from jira import JIRA
import json
import os
import getpass
import argparse


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
        url = ' https://' + config['subdomain'] + '.' + config['domain'] + "/browse/" + i.key
        end = bcolors.ENDC
        if status in colors:
            color = bcolors.customColor(*colors[status])
        elif "default" in colors:
            if colors['default'] == "debug":
                print(status + " does not yet have a defined color")
                color = ''
                end = ''
            else:
                color = bcolors.customColor(*colors["default"])
        else:
            color = ''
            end = ''
        print(color + key + end + summary + " " + bcolors.OKBLUE + url + end)


def getAppropriateSprint(which_types):
    # Use the get boards method to determine which board you want sprint info
    # for
    boards = config['board']
    # sprints = []
    existing_boards = jira.projects()
    sprints = jira.sprints()
    issue = jira.issue("ops-903")
    print(issue)
    for i in sprints:
        all_sprints = jira.sprints(i.id)
        for s in all_sprints:
            if s.name.lower() == "zigzaggery":
                print("board", i)
                print("sprint". s)

    print("out of loops")
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
        aconfig = json.load(conf)
        return aconfig

def statusColors(conf):
    with open(os.path.dirname(__file__) + "/status-color.conf", 'r') as default_colors:
        d_colors = json.load(default_colors)
    c_colors = {}
    for i,j in d_colors.items():
        c_colors[i] = j
    if "status-colors" in conf:
        if "default" in conf['status-colors']:
            default = conf['status-colors']['default']
            if verify_color(default) or default == "debug":
                c_colors['default'] = default
        if "custom-colors" in conf['status-colors']:
            custom = conf['status-colors']['custom-colors']
            round2 = {}
            for i, j in custom.items():
                if verify_color(j):
                    c_colors[i] = j
                else:
                    if type(j) is str:
                        round2[i] = j
                    else:
                        print("Color for Status " + str(i) + "could not be resolved")
            for i, j in round2.items():
                if j in c_colors:
                    c_colors[i] = c_colors[j]
                else:
                    resolved = resolve_color(j, round2, c_colors)
                    if verify_color(resolved):
                        c_colors[i] = resolved
                    else:
                        print("Color for Status " + str(i) + " could not be resolved")
    return c_colors 

def resolve_color(name, resolving_dict, final_dict):
    if name in resolving_dict:
        name_prime = resolving_dict[name]
    else:

        return None
    while name_prime is not name:
        if name_prime in final_dict:
            return final_dict[name_prime]
        elif name_prime in resolving_dict:
            name_prime = resolving_dict[name_prime]
        else:
            return None
    return None



def verify_color(rgb):
    if type(rgb) is list and len(rgb) == 3:
        return all([i>=0 and i<=255 for i in rgb])
    else:
        return False

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
    colors = statusColors(config)

    jira = getJira(args.user, args.password)

    if args.show_unassigned:
        retrieveIssues(jira, 'null', args.board_type)
    elif args.board:
        getBoards(jira)
    elif args.returnall:
        getAllIssues(jira, args.board_type)
    else:
        retrieveIssues(jira, args.t_user, args.board_type)
