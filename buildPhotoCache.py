#!/usr/bin/env python

# Builds photo cache from Facebook

import urllib, urllib2
import argparse, random

import requests

# AJAX Zone
# =========
SELECT_FBIDS_URL = 'http://www.thefacesoffacebook.com/php/select_many_fbid.php'

def getFBIDs(offset, count):
    userStr = []
    for i in xrange(offset, offset + count):
        userStr.append(str(i) + " fbusers1 " + str(i))
    data = ",".join(userStr)

    r = requests.post(SELECT_FBIDS_URL, data=data)
    responseBody = r.text
    print responseBody
    return [int(s.split(',')[1]) for s in responseBody.split(" ")]
    

# Download Coordination
# =====================

def downloadProfilePictures(offset, count = 40):
    print "Obtaining Facebook IDs..."
    fbids = getFBIDs(offset, count)
    print fbids

def main():
    parser = argparse.ArgumentParser(description='Builds photo cache from Facebook/Faces of Facebook')
    parser.add_argument('--count', dest='count', metavar='N', type=int, default=40, help="Number of profiles to add to the cache (default: 40)")
    parser.add_argument('--offset', dest='offset', metavar='OFFSET', type=int, help="Offset to start the download from up to 1000000 (default: randomly selected)")
    args = parser.parse_args()

    if args.offset is None:
        args.offset = random.randint(1, 1000000)

    print "Starting at offset " + str(args.offset) + " (count: " + str(args.count) + ")...\n"
    # get random sampling of profiles
    downloadProfilePictures(args.offset, args.count)

if __name__ == '__main__':
    main()
