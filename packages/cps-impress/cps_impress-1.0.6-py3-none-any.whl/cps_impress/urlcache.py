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
        # Cache file
        #
        cache_dir = os.getenv("CACHE_DIR")
        if not cache_dir:
            raise Exception("CACHE_DIR is missing")

        if not os.path.isdir(cache_dir):
            raise Exception(f"no cache directory [{cache_dir}]")

        self.cache_file = cache_dir + "/" + hashlib.sha256(url.encode()).hexdigest()
        if not os.path.isfile(self.cache_file):
            header = {"User-Agent": self._USER_AGENT}
            try:
                response = requests.get(url, headers=header, stream=True)
            except:
                raise Exception(f"URL request failed [{url}]")
            try:
                with open(self.cache_file, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        f.write(chunk)
            except:
                raise Exception(f"cache write failed [{self.cache_file}]")

if __name__=="__main__":
    main()

# vim: shiftwidth=4 tabstop=4 softtabstop=4 expandtab
