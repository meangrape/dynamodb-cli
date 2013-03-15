dynamo-cli
==========
<pre>
usage: dynamo-cli [-h] [-c COLUMNS] [-C] [-cf CREDFILE] [-f FILE] [-i ID]
                  [-k KEY] [-H HASH] -t TABLE [-T] [-R READ] [-W WRITE]

optional arguments:
  -h, --help            show this help message and exit
  -c COLUMNS, --columns COLUMNS
                        An unquoted, comma-delimited list of dynamo column
                        headers (personid, first_name)
  -C, --header          Indicates that the first line of the tab-delimnited
                        file contains column names. --columns will override
                        this flag
  -cf CREDFILE, --credfile CREDFILE
                        File containing AWS credentials. Contains 2 lines like
                        AWSAccessKeyId=ABCDE AWSSecretKey=12345
  -f FILE, --file FILE  The input filename; the first line is discarded; the
                        remainder is expected to be tab-delimited
  -i ID, --id ID        AWS Access Key ID
  -k KEY, --key KEY     AWS Secret Key
  -H HASH, --hash HASH  DynamoDB hash key
  -t TABLE, --table TABLE
                        DynamoDB table name
  -T, --throttle        Alter table capcaity. See --read and --write. All
                        other actions ignored!
  -R READ, --read READ  How many read capacity units if in --throttle mode.
                        The default value of 0 means "leave unchanged"
  -W WRITE, --write WRITE
                        How many write capacity units if in --throttle mode.
                        The default value of 0 means "leave unchanged"
</pre>
dynamo-cli does two things right now. It uploads files (tab-delimited, first line discarded) to a dynamodb table.
It also will change read and write capacity for an existing dynamo table.

1. File uploads are -- at the moment -- highly specific to the way Jay does work. You can uload either an LZO compressed file or a plain text file.
If you do not supply the -c/--columns argument or the -C/--header flag, the script defaults to the columns in the people-match table.

You supply columns like this:
```./dynamo-cli -c "name, age, id" -f ./people.txt -t people -H id```

You may also supply column names in the first line of the data file:
```./dynamo-cli --headers -f ./people.txt -t people -H id```

The dynamo table must already exist.

2. The following example will alter read capacity to 200 and write capacity to 8000 for the people-match table.
```./dynamo-cli -t people-match -cf ~/.aws/credentials -T -R 200 -W 8000```

AWS credentials may be specified on the command-line, may be in a file, or may be environment variables.
<pre>
    """Command line flags have priority, followed by credentials in a file,
    followed by environment variables.

    --id abcde --key 12345

    ~/.aws_credentials
    AWSAccessKeyId=abcde
    AWSSecretKey=12345

    export AWSAccessKeyId=abcde
    export AWSSecretKey=12345
    """
</pre>
