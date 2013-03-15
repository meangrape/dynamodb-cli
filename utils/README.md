A handful of dynamo utilities that might be useful outside of the cli tool.

I've just extracted them with the initial commit so they're not as easy to use as I'd like.
In particular, there's a lot of passing around of AWS creds.


<pre>
def alter_capacity(table, readcap, writecap, AWSAccessKeyId, AWSSecretKey):


def aws_authentication(args):
    """Command line flags have priority, followed by credentials in a file,
    followed by environment variables.

    --id abcde --key 12345

    ~/.aws_credentials
    AWSAccessKeyId=abcde
    AWSSecretKey=12345

    export AWSAccessKeyId=abcde
    export AWSSecretKey=12345
    """

def get_table(table, AWSAccessKeyId, AWSSecretKey):
    """Open a connection to DynamoDB & get a handle to a table; keep trying
    until we get it."""
</pre>
