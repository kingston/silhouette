#!/usr/bin/env python

# Builds photo cache from Facebook

import urllib
import argparse, random, os

from os import path

import requests

# AJAX Zone
# =========
FACEBOOK_GRAPH_URL = 'http://graph.facebook.com/'

def getPhotoURL(fbid):
    url = FACEBOOK_GRAPH_URL + str(fbid) + "/picture"
    payload = {'width':100, 'height':100, 'redirect':'false'}
    r = requests.get(url, params=payload)
    response = r.json()
    if 'data' not in response:
        raise Exception('Invalid response: ' + r.text())

    if response['data']['is_silhouette']:
        return None
    else:
        return response['data']['url']

def downloadPhoto(url, destDir, fbid):
    filepath = path.join(destDir, str(fbid) + ".jpg")
    if url is None:
        # create empty file to represent silhouette
        open(filepath, 'a').close()
    else:
        urllib.urlretrieve(url, filepath)

# Download Coordination
# =====================

def getFBIDs(sourceFile):
    with open(sourceFile, 'r') as f:
        return set([int(s) for s in f.read().split(",")])

def getCachedFBIDs(cacheDir):
    return set([int(s.split(".")[0]) for s in os.listdir(cacheDir) if s.endswith(".jpg")])

def downloadProfilePictures(sourceFile, cacheDir):
    print "Obtaining Facebook IDs..."
    fbids = getFBIDs(sourceFile)
    print str(len(fbids)) + " loaded!"

    cachedFBIDs = getCachedFBIDs(cacheDir)
    print str(len(cachedFBIDs)) + " cached!"
    fbids = fbids - cachedFBIDs

    print ""

    print "Downloading " + str(len(fbids)) + " photos..."
    skipped = 0
    processed = 0
    for fbid in fbids:
        url = getPhotoURL(fbid)
        if processed % 10 == 0:
            print str(processed) + " processed..."
        if url is None:
            skipped += 1
        else:
            processed += 1
        downloadPhoto(url, cacheDir, fbid)

    print "Download complete! (" + str(processed) + " processed, " + str(skipped) + " skipped)"

def main():
    parser = argparse.ArgumentParser(description='Builds photo cache from Facebook/Faces of Facebook')
    parser.add_argument('source', metavar='FBID_FILE', help="Source file containing comma-delimited FBIDs")
    parser.add_argument('-c', '--cache-dir', dest='cachedir', default='cache', metavar='DIR', help="Destination image cache directory")
    args = parser.parse_args()

    if not os.path.isdir(args.cachedir):
        os.makedirs(args.cachedir)

    downloadProfilePictures(args.source, args.cachedir)

if __name__ == '__main__':
    main()
