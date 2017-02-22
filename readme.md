This is only python3 compatible, though it would be pretty straightforward to port

###Arguments
1. username
2. password
3. optional flags
4. give -u flag a username


###optional flags:
`-h` see help page


`-u` see unassigned stories in the current sprint


`-u [username]` returns all issues for the given user


`-a` returns all issues in the given sprint


`-b` see all boards, this is used to determine the board number in the conf file

### Configuration
A conf file named jira.conf needs to be in the same directory as the python file. It should be a standard json file with 3 required fields:

`https://{subdomain}.{domain.net}/`

```json
{
"board": 7,
"subdomain": "subdomain",
"domain": "domain.net"
}
```

###Python Package Dependencies
jira (and it's dependencies)

`pip install jira`