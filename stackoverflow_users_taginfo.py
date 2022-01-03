from datetime import datetime
import itertools
import re
import requests
import sys
import time
from bs4 import BeautifulSoup
import numpy as np
from wordcloud import WordCloud


def find_between(in_str, start='>', end='<'):
    """ Find string between two search patterns.
    """
    return in_str.split(start)[1].split(end)[0]


def unquote_str(in_str):
    """ Decode URL strings. For example, replace %2b with plus sign and so on.
    """
    if (sys.version_info >= (3, 0)):
        from urllib.parse import unquote
    else:
        from urllib import unquote
    return unquote(in_str)


def toint(a):
    """ Convert string to int and also scale them accordingly if they end
    in "k", "m" or "b".
    """
    weights = {'k': 1000, 'm': 1000000, 'b': 1000000000}
    if len(a) > 1:
        if a[-1] in weights:
            return weights[a[-1]] * int(a[:-1])
    return int(a)


def taginfo(link, lim_num_tags=None, print_page_count=False, request_frequency=1.5):
    """ Get information about Stack Overflow and all Stack Exchange sites users'
    tags (tags and corresponding tag points scored).
    This could be directly used with wordcloud module for generating tag cloud.

    Parameters
    ----------

    link : int or string
        For int case, we are assuming Stackoverflow site users. So, input as
        int is the user ID of the Stackoverflow user whose information is to be
        extracted. For string case, it's the complete user profile link to the
        Stackexchange site and is intended to cover all Stack Exchange sites
        profiles.

        A. As an example for int case, consider Stackoverflow's top reputation
        user Jon skeet. His Stack Overflow link is -
        "http://stackoverflow.com/users/22656/jon-skeet".
        So, we would have - link = 22656.

        B. As another example for string case, one can generate Jon's
        meta.stackexchange tag cloud with -
        link = "http://meta.stackexchange.com/users/22656/jon-skeet" or
        link = "http://meta.stackexchange.com/users/22656".

    lim_num_tags : int (default=None)
        Number of tags to be tracked. Default is None, which tracks all tags
        possible.

    print_page_count : bool(default=False)
        Print per page progress on processing data.

    request_frequency : float (default=1.5)
        Number of seconds to wait before making another request. Making
        requests too often will lead to throttling and eventually timeout
        errors.

    Output
    ------
    Output is a dictionary with tag names for keys and tag count for values.
    """

    # Get start link (profile page's tag link)
    if '.com' in str(link):
        start_link = link + "?tab=tags&sort=votes&page="
    else:
        start_link = "http://stackoverflow.com/users/" + str(link) + \
                                                "?tab=tags&sort=votes&page="

    # regex pattern to match title of tag divs
    tag_patt = re.compile(r'\d+ non-wiki questions \(\d+ score\)\. \d+ non-wiki answers \(\d+ score\)\.')
    # pattern to match score inside the title
    score_patt = re.compile(r'non-wiki answers \((\d+) score\)')

    info = {}
    last_get = None
    for page in itertools.count(1):
        if print_page_count:
            print("Processing page: ", page)

        if last_get is None:
            last_get = datetime.now()
        else:
            delta = datetime.now() - last_get
            wait_needed = request_frequency - delta.total_seconds()
            if wait_needed > 0:
                time.sleep(wait_needed)
            last_get = datetime.now()

        resp = requests.get(start_link + str(page))
        soup = BeautifulSoup(resp.text, 'lxml')
        tag_divs = soup.find_all('div', title=tag_patt)
        if not tag_divs:
            # we're out of tags
            break

        if print_page_count:
            print(len(tag_divs), 'tags found on page')

        for tag_div in tag_divs:
            tag_score = int(score_patt.search(tag_div.get('title')).group(1))
            tag_name = tag_div.find('a', class_='post-tag').text
            info[tag_name] = tag_score

            if len(info) == lim_num_tags:
                # we're done
                break
        if len(info) == lim_num_tags:
            # break out of pagination loop
            break

    # For a case when all tag counts are zeros, it would throw error.
    # So, for such a case, escape it by setting all counts to "1".
    if info and max(info.values()) == 0:
        info = dict.fromkeys(info, 1)

    return info


def draw_taginfo(info, 
                 image_dims, 
                 out_filepath,
                 skip_tags = [],
                 font_path="fonts/ShortStack-Regular.ttf",
                 ):
    
    W, H = image_dims    # Wordcloud image size (width, height)
    for sk in skip_tags:
        del info[sk]
                  
    if info is None:
        print("Error : No webpage found!")
    else:
        if len(info) == 0:
            print("Error : No tags found!")
        else:         # Successfully extracted tag info
            WC = WordCloud(font_path=font_path, width=W, height=H,
                           max_words=len(info)).generate_from_frequencies(info)
            WC.to_image().save(out_filepath)
            print("Tag Cloud Saved as " + out_filepath)
            

def tag_cloud(link=22656, 
              lim_num_tags=200, 
              image_dims=(400, 200),
              skip_tags = [],
              out_filepath="TagCloud.png",
              ):
    """ Generate tag cloud and save it as an image.

    Parameters
    ----------
    link : same as used for the function taginfo.

    num_tags : same as used for the function taginfo.

    image_dims : tuple of two elements.
        Image dimensions of the tag cloud image to be saved.

    out_filepath : string
        Output image filepath.

    Output
    ------
    None
    """

    info = taginfo(link=link, lim_num_tags=lim_num_tags)    
    draw_taginfo(info, image_dims=image_dims, out_filepath=out_filepath, skip_tags = skip_tags)
