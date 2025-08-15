#! /usr/bin/env python3
#
# Copyright (C) 2025 The Authors
# All rights reserved.
#
# This file is part of cps_impress.
#
# cps_impress is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation.
#
# cps_impress is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with cps_impress. If not, see http://www.gnu.org/licenses/
#
import argparse
import hashlib
import magic
import os
import requests
import sys

from dotenv import load_dotenv

def main():
    ##################################################################
    # CLASS TEST AND DEBUG
    #
    parser = argparse.ArgumentParser(description="URL Cache", epilog="example: urlcache URL", add_help=True)

    parser.add_argument("url", type=str, help="URL")

    # Get main args
    args = parser.parse_args()
    
    # Create object
    obj = URLCache(args.url)

    # Output filename
    print(obj.cache_file)

class URLCache:
    # akamaitechnologies hangs unless it recognises the User-Agent
    _USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134."

    cache_file = None

    def __init__(self, url):
        load_dotenv(os.getcwd() + os.sep + ".env")

        ##################################################################
        # Cache dir
        #
        cache_dir = os.getenv("CACHE_DIR")
        if not cache_dir:
            raise Exception("CACHE_DIR is missing")

        cache_dir = os.path.abspath(cache_dir)
        if not os.path.isdir(cache_dir):
            raise Exception(f"no cache directory [{cache_dir}]")

        ##################################################################
        # Lookup file
        #
        sha256 = hashlib.sha256(url.encode()).hexdigest()
        for file in os.listdir(cache_dir):
            if file.startswith(sha256):
                self.cache_file = cache_dir + '/' + file
                return

        ##################################################################
        # Cache file
        #
        tempfile = cache_dir + "/" + sha256
        header = {"User-Agent": self._USER_AGENT}
        try:
            response = requests.get(url, headers=header, stream=True)
        except:
            raise Exception(f"URL request failed [{url}]")
        try:
            with open(tempfile, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
        except:
            raise Exception(f"cache write failed [{tempfile}]")

        ##################################################################
        # Rename file
        #
        self.cache_file = tempfile + '.' + \
            magic.from_file(tempfile, mime=True).split('/')[1]
        try:
            os.rename(tempfile, self.cache_file)
        except:
            raise Exception(f"file rename failed [{tempfile} => {self.cache_file}]")

if __name__=="__main__":
    main()

# vim: shiftwidth=4 tabstop=4 softtabstop=4 expandtab
