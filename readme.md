This is only python3 compatible, though it would be pretty straightforward to port

### Arguments
1. username
2. password
3. optional flags
4. give -u flag a username


### optional flags:
`-h` see help page


`-u` `--unassigned` see unassigned stories in the current sprint


`-f [username]` `--for-user [username]` returns all issues for the given user


`-a` returns all issues in the given sprint


`-b` see all boards, this is used to determine the board number in the conf file


`-t [ticket_id]` `--ticket [ticket_id]` retrieve a specific ticket by ID and display it in LLM-friendly format

### Configuration
A conf file named jira.conf needs to be in the same directory as the python file. It should be a standard json file with 3 required fields:

`https://{subdomain}.{domain.net}/`

```json
{
"board": [7, 2],
"subdomain": "subdomain",
"domain": "domain.net"
}
```

### Python Package Dependencies
jira (and it's dependencies)

`pip install jira`
