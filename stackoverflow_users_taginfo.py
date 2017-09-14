from bs4 import BeautifulSoup
import numpy as np
import requests
import itertools
import sys
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


def info_mainpage(url):
    """ Given the main tag page, this function gets basic information about tag
    pages and tag names and their scores as well. 
    On the basic info, there are three numbers scraped :
    1. Number of tag pages
    2. Total number of tags
    3. Number of tags per page

    Parameters
    ----------
    url : string
        URL link to user's main tag page.
    
    Output
    ------
    pginfo : dict
        Dictionary that holds the three page info as listed earlier.
        
    name : list of strings
        Holds the tag names
        
    count : list of ints
        Holds the tag scores
    """

    soup = BeautifulSoup(requests.get(url).text, "lxml")

    pg_blk = soup.find_all("div", class_="pager fr")
    tag_blk = soup.find_all("div", class_="answer-votes")
    tag_blk_str = [str(i) for i in tag_blk]
    str0 = find_between(str(soup.find_all("span", class_="count")))
    lim_ntags = int(str0.replace(',', ''))

    max_tags = None
    num_pages = 1
    if len(pg_blk) != 0:
        max_tags = len(tag_blk)
        last_page_blk = pg_blk[0].find_all("span", class_="page-numbers")[-2]
        num_pages = int(find_between(str(last_page_blk)))
    pginfo = {'pages': num_pages, 'tags': lim_ntags, 'tags_perpage': max_tags}

    name = [unquote_str(find_between(i, '[', ']')) for i in tag_blk_str]
    count = [toint(find_between(i)) for i in tag_blk_str]
    return pginfo, name, count


def stackoverflow_taginfo(url):
    """ Get information about an user's tags from their Stack Overflow
    tag pages fed as the input URL. Mainly two pieces of information are scraped :
    tag names and their respective counts/scores.

    Parameters
    ----------
    url : string
        URL link to user's main tag page.
    
    Output
    ------
    name : list of strings
        Holds the tag names
        
    count : list of ints
        Holds the tag scores
    """

    soup = BeautifulSoup(requests.get(url).text, "lxml")
    tag_blk = soup.find_all("div", class_="answer-votes")
    tag_blk_str = [str(i) for i in tag_blk]
    name = [unquote_str(find_between(i, '[', ']')) for i in tag_blk_str]
    count = [toint(find_between(i)) for i in tag_blk_str]
    return name, count


def taginfo(link, lim_num_tags=None, return_sort=True, print_page_count=False):
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

    return_sort : bool (default=True)
        This boolean flag decides whether the output list has the tags
        sorted by their counts. Since WordCloud module internally sorts
        them anyway, so for performance one can turn it off.

    print_page_count : bool(default=False)
        Print per page progress on processing data.

    Output
    ------
    Output is a dictionary with items for tag names and keys for tag count.
    """

    # Get start link (profile page's tag link)
    if '.com' in str(link):
        start_link = link + "?tab=tags&sort=votes&page="
    else:
        start_link = "http://stackoverflow.com/users/" + str(link) + \
                                                "?tab=tags&sort=votes&page="

    tag_name = []
    tag_count = []

    info1 = info_mainpage(start_link + '1')
    fields = ['pages', 'tags', 'tags_perpage']
    num_pages, num_tags, tags_per_page = [info1[0][i] for i in fields]
    tag_name.append(info1[1])
    tag_count.append(info1[2])

    num_tags = min(lim_num_tags, num_tags)
    lim_num_tags = [num_tags if lim_num_tags is None else num_tags][0]
    if num_pages > 1:
        num_pages = int(np.ceil(lim_num_tags/float(tags_per_page)))
        for page_id in range(2, num_pages+1):
            if print_page_count:
                print("Processing page#" + str(page_id) + "/" + str(num_pages))
                sys.stdout.flush()

            url = start_link + str(page_id)
            page_tag_name, page_tag_count = stackoverflow_taginfo(url)
            tag_name.append(page_tag_name)
            tag_count.append(page_tag_count)

    info0 = list(zip(itertools.chain(*tag_name), itertools.chain(*tag_count)))
    sorted_indx = np.argsort([item[1] for item in info0])[::-1]
    info = [info0[idx] for idx in sorted_indx][:lim_num_tags]

    # For a case when all tag counts are zeros, it would throw error.
    # So, for such a case, escape it by setting all counts to "1".
    dict_info = dict(info)
    if info[0][1] == 0:
        dict_info = dict.fromkeys(dict_info, 1)

    return dict_info


def tag_cloud(link=22656, lim_num_tags=200, image_dims=(400, 200),
              out_filepath="TagCloud.png"):
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

    W, H = image_dims    # Wordcloud image size (width, height)
    font_path = "fonts/ShortStack-Regular.ttf"  # Font path
    info = taginfo(link=link, lim_num_tags=lim_num_tags)
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
