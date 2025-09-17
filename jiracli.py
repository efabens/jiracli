#!/usr/bin/env python3

from jira import JIRA
import json
import os
import getpass, argparse
from sys import stdout


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def custom_color(r, g, b):
        return '\033[38;2;' + str(r) + ";" + str(g) + ";" + str(b) + 'm'


class Password(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        if values is None:
            values = os.getenv('JIRA_PASSWORD', 'foo')
            if values == 'foo':
                values = getpass.getpass()

        setattr(namespace, self.dest, values)


def do_issues(sprint, issues):
    # concatName = sprint.name + ' | ' + str(sprint.id) + ' | ' + sprint.state
    # print(bcolors.HEADER + concatName + bcolors.ENDC)
    for i in issues:
        status = i.fields.status.name
        key = "[" + i.key + "] " + status + " "
        summary = i.fields.summary
        end = bcolors.ENDC
        if status in ["Resolved", "Ready to Test"]:
            color = bcolors.custom_color(46, 139, 87)
        elif status in ["To Do", "Selected for Development", "Open"]:
            color = bcolors.custom_color(255, 140, 0)
        elif status == "Done":
            color = bcolors.custom_color(30, 144, 255)
        elif status == "In Progress":
            color = bcolors.custom_color(186, 85, 211)
        elif status in ["Backlog", "FRONTLOG"]:
            color = bcolors.custom_color(30, 144, 255)
        elif status in ["New"]:
            color = bcolors.custom_color(255, 31, 143)
        else:
            color = ''
            end = ''
        if stdout.isatty():
            print(color + key + end + summary)
        else:
            print(key + summary)
    
def get_appropriate_sprint(which_types):
    # Use the get boards method to determine which board you want sprint info
    # for
    boards = config['board']
    print(boards)
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


def retrieve_issues(jira, assignee, which_types):
    sprints = get_appropriate_sprint(which_types)
    for sprint in sprints:
        issues = jira.search_issues(
            'assignee=' + assignee + ' and sprint=' + str(sprint.id))
        if issues:
            do_issues(sprint, issues)


def get_all_issues(jira, which_types):
    # sprints = getAppropriateSprint(which_types)
    # for sprint in sprints:
    issues = jira.search_issues(
        'assignee = currentUser() and statusCategory != Done order BY status ASC, updatedDate DESC')
    do_issues("", issues)


def get_ticket_for_llm(jira, ticket_id):
    try:
        issue = jira.issue(ticket_id, expand='changelog,renderedFields')
        
        # Format the output for LLM processing
        output = []
        output.append(f"# JIRA Ticket: {issue.key}")
        output.append(f"**URL:** https://{config['subdomain']}.{config['domain']}/browse/{issue.key}")
        output.append("")
        
        # Basic information
        output.append("## Basic Information")
        output.append(f"**Summary:** {issue.fields.summary}")
        output.append(f"**Status:** {issue.fields.status.name}")
        output.append(f"**Type:** {issue.fields.issuetype.name}")
        
        if hasattr(issue.fields, 'priority') and issue.fields.priority:
            output.append(f"**Priority:** {issue.fields.priority.name}")
        
        output.append("")
        
        # People
        output.append("## People")
        if issue.fields.assignee:
            output.append(f"**Assignee:** {issue.fields.assignee.displayName}")
        else:
            output.append("**Assignee:** Unassigned")
            
        if issue.fields.reporter:
            output.append(f"**Reporter:** {issue.fields.reporter.displayName}")
            
        if issue.fields.creator:
            output.append(f"**Creator:** {issue.fields.creator.displayName}")
        
        output.append("")
        
        # Dates
        output.append("## Dates")
        if issue.fields.created:
            output.append(f"**Created:** {issue.fields.created}")
        if issue.fields.updated:
            output.append(f"**Updated:** {issue.fields.updated}")
        if hasattr(issue.fields, 'resolutiondate') and issue.fields.resolutiondate:
            output.append(f"**Resolved:** {issue.fields.resolutiondate}")
        if hasattr(issue.fields, 'duedate') and issue.fields.duedate:
            output.append(f"**Due Date:** {issue.fields.duedate}")
        
        output.append("")
        
        # Description
        if issue.fields.description:
            output.append("## Description")
            output.append(issue.fields.description)
            output.append("")
        
        # Components
        if issue.fields.components:
            output.append("## Components")
            for component in issue.fields.components:
                output.append(f"- {component.name}")
            output.append("")
        
        # Labels
        if issue.fields.labels:
            output.append("## Labels")
            output.append(f"{', '.join(issue.fields.labels)}")
            output.append("")
        
        # Fix versions
        if hasattr(issue.fields, 'fixVersions') and issue.fields.fixVersions:
            output.append("## Fix Versions")
            for version in issue.fields.fixVersions:
                output.append(f"- {version.name}")
            output.append("")
        
        # Parent/Epic
        if hasattr(issue.fields, 'parent') and issue.fields.parent:
            output.append("## Parent Issue")
            output.append(f"**{issue.fields.parent.key}:** {issue.fields.parent.fields.summary}")
            output.append("")
        
        # Subtasks
        if hasattr(issue.fields, 'subtasks') and issue.fields.subtasks:
            output.append("## Subtasks")
            for subtask in issue.fields.subtasks:
                output.append(f"- **{subtask.key}** ({subtask.fields.status.name}): {subtask.fields.summary}")
            output.append("")
        
        # Issue links
        if hasattr(issue.fields, 'issuelinks') and issue.fields.issuelinks:
            output.append("## Linked Issues")
            for link in issue.fields.issuelinks:
                if hasattr(link, 'outwardIssue') and link.outwardIssue:
                    output.append(f"- **{link.type.outward}** {link.outwardIssue.key}: {link.outwardIssue.fields.summary}")
                elif hasattr(link, 'inwardIssue') and link.inwardIssue:
                    output.append(f"- **{link.type.inward}** {link.inwardIssue.key}: {link.inwardIssue.fields.summary}")
            output.append("")
        
        # Comments
        if issue.fields.comment.comments:
            output.append("## Comments")
            for comment in issue.fields.comment.comments:
                output.append(f"### Comment by {comment.author.displayName} on {comment.created}")
                output.append(comment.body)
                output.append("")
        
        # Attachments
        if hasattr(issue.fields, 'attachment') and issue.fields.attachment:
            output.append("## Attachments")
            for attachment in issue.fields.attachment:
                output.append(f"- **{attachment.filename}** ({attachment.size} bytes) - {attachment.created}")
            output.append("")
        
        return "\n".join(output)
        
    except Exception as e:
        return f"Error retrieving ticket {ticket_id}: {str(e)}"


def get_config():
    with open(os.path.dirname(__file__) + "/jira.conf", 'r') as conf:
        return json.load(conf)


def getJira(user, password):
    options = {
        'server': 'https://' + config['subdomain'] + '.' + config['domain'],
        'agile_rest_path': "agile",
        'rest_api_version': '3'
    }

    return JIRA(options, basic_auth=(user, password))


def get_boards(jira):
    boards = sorted(jira.boards(), key=lambda x: x.name)
    for i in boards:
        print(bcolors.HEADER + str(i.id) + bcolors.ENDC, i.name)


def man_page():
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
    parser.add_argument(
        '-t', '--ticket', dest='ticket_id',
        help='Retrieve a specific ticket by ID and display it in LLM-friendly format')
    args = parser.parse_args()

    config = get_config()
    jira = getJira(args.user, args.password)

    if args.ticket_id:
        print(get_ticket_for_llm(jira, args.ticket_id))
    elif args.show_unassigned:
        retrieve_issues(jira, 'null', [])
    elif args.board:
        get_boards(jira)
    else:
        get_all_issues(jira, args.board_type)
    # else:
    #     retrieve_issues(jira, args.t_user, args.board_type)
