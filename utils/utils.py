import datetime
import os
import random
import sys
import time

import argparse
import boto.dynamodb


def __acceptable_capacity(current, goal):
    # If we're increasing capacity
    if current < goal:
        if current > (goal * 0.5):
            return goal
        else:
            return current * 2

    # Decreasing capacity
    if goal < current:
        return goal

    # No change
    if current == goal:
        return current


def __update_capacity(dynamo, table, readcapacity, writecapacity):
    """ XXX There are bound to be DynamoDB/Boto errors that I haven't seen
    yet"""
    dynamo.update_throughput(table, readcapacity, writecapacity)
    return readcapacity, writecapacity


def alter_capacity(table, readcap, writecap, AWSAccessKeyId, AWSSecretKey):
    """ XXX Ugly ahead.
    """
    # Get a table object
    myconn, mytable = get_table(table, AWSAccessKeyId, AWSSecretKey)

    # Check current ReadCapacityUnits and WriteCapacityUnits
    dynamo = boto.dynamodb.layer2.Layer2(aws_access_key_id=AWSAccessKeyId, aws_secret_access_key=AWSSecretKey)
    table_description = dynamo.describe_table(table)
    current_readcap = table_description['Table']['ProvisionedThroughput']['ReadCapacityUnits']
    current_writecap = table_description['Table']['ProvisionedThroughput']['WriteCapacityUnits']
    # If table status is ACTIVE, we can update. If UPDATING, we need to wait. If
    # it's something else, I dunno so we bail out.
    table_status = table_description['Table']['TableStatus']
    if table_status == 'UPDATING':
        duration = random.randint(10, 60)
        print >> sys.stdout, "%s Table is still updating. Sleeping for %s seconds." % (datetime.datetime.now(), duration)
        time.sleep(duration)
        del(myconn, mytable, dynamo)
        return alter_capacity(table, readcap, writecap, AWSAccessKeyId, AWSSecretKey)

    if table_status != "ACTIVE":
        print >> sys.stderr, "Table in unknown state -- %s" % table_status
        sys.exit(1)

    # XXX This doesn't work
    # If we're not going to change read or write capacity, set our goal to equal
    # the current value
    if readcap == 0:
        readcap == current_readcap
    if writecap == 0:
        writecap == current_writecap

    # If both read and write capacity equals our goals, return
    if readcap == current_readcap and writecap == current_writecap:
        del(myconn, mytable, dynamo)
        return True

    # We can only change up by a max of doubling.
    # Once per 24 hours we can change down any amount.
    tgtreadcap = __acceptable_capacity(current_readcap, readcap)
    tgtwritecap = __acceptable_capacity(current_writecap, writecap)

    current_readcap, current_writecap = __update_capacity(dynamo, mytable, tgtreadcap, tgtwritecap)
    print >> sys.stdout, "Updated %s to RCU %d and WCU %d" % (table, current_readcap, current_writecap)
    del(myconn, mytable, dynamo)

    # Checking before & after updating so we can exit as quickly as possible
    # If both read and write capacity equals our goals, return
    if readcap == current_readcap and writecap == current_writecap:
        return True

    return alter_capacity(table, readcap, writecap, AWSAccessKeyId, AWSSecretKey)


def aws_authentication(args):
    """Command line flags have priority, followed by credentials in a file,
    followed by environment variables.

    --id abcde --key 12345

    ~/.aws_credentials
    AWSAccessKeyId=abcde
    AWSSecretKey=12345

    export AWS_ACCESS_KEY_ID=ABCDEFG
    export AWS_SECRET_ACCESS_KEY=123456789
    """

    # --id and --key require each other
    if (args.id and not args.key) or (args.key and not args.id):
        msg = "--id and --key must both be set"
        print >> sys.stdout, msg
        sys.exit(1)

    if args.id and args.key:
        AWSAccessKeyId = args.id
        AWSSecretKey = args.key
        return (AWSAccessKeyId, AWSSecretKey)

    if args.credfile:
        creds = open(args.credfile, 'r').readlines()
        for line in creds:
            if line[0:14] == 'AWSAccessKeyId':
                AWSAccessKeyId = line.split('=')[1].strip()
            if line[0:12] == 'AWSSecretKey':
                AWSSecretKey = line.split('=')[1].strip()
        if AWSAccessKeyId and AWSSecretKey:
            return (AWSAccessKeyId, AWSSecretKey)
        else:
            print >> sys.stderr, "Couldn't parse AWS credential file: %s" % args.credfile

    try:
        AWSAccessKeyId = os.environ['AWS_ACCESS_KEY_ID']
        AWSSecretKey = os.environ['AWS_SECRET_ACCESS_KEY']
        return (AWSAccessKeyId, AWSSecretKey)
    except KeyError, e:
        print >> sys.stderr, "Unable to locate AWS credentials"
        sys.exit(1)


def get_table(table, AWSAccessKeyId, AWSSecretKey):
    """Open a connection to DynamoDB & get a handle to a table; keep trying
    until we get it."""
    try:
        dynconn = boto.connect_dynamodb(aws_access_key_id=AWSAccessKeyId, aws_secret_access_key=AWSSecretKey)
        dyntable = dynconn.get_table(table)
        return dynconn, dyntable
    except:
        duration = random.randint(1, 1800)
        print >> sys.stdout, "Failed to connect for %s; sleeping %d seconds" % (table, int(duration / 60))
        time.sleep(duration)
        return get_table(table, AWSAccessKeyId, AWSSecretKey)
