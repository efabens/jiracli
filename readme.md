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

There is also an additional set of custom color fields that are allowed they should be in the format 

```json
"status-colors": {
    "custom-colors": {
      "Verifying": "Pending Review",
      "Ready to Test": "Resolved",
      "Pending Review": [
        253,
        106,
        2
      ]
    },
    "default":"debug" //Default is not required, see notes below for more info
  }
```

These will override values in the status-colors.conf file. The values need to either be a list of three value [R,G,B] or the name of another status that has a color (or a status that references another status that has a color and so on. If there is a loop of references it will be set to the default color, or if the reference status can't be found it is set to default). One debugging note. If in the custom colors section any of the values are set to `None` it will use the standard color scheme of your terminal. There is a field recognized called `"default"` if this is set it will be used instead of the terminal default. If `"default"` is set to `"debug"` it will print the name of any statuses that don't have a configured color but will use the default terminal color as the default.

There is a file called `status-color.conf` this can also be used to configure colors, but all statuses must be defined as `[R, G, B]` additionally this is not in the `.gitignore` file.

### Python Package Dependencies
jira (and it's dependencies)

`pip install jira`
