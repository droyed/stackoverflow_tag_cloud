from bs4 import BeautifulSoup
import numpy as np
import requests
import itertools
import sys
from wordcloud import WordCloud

def toint(a):
    """ Convert string to int and also scale them accordingly if they end 
    in "k", "m" or "b".
    """         
    weights = {'k': 1000, 'm': 1000000, 'b': 1000000000}
    if len(a)>1:
        if a[-1] in weights:
            return weights[a[-1]] * int(a[:-1])
    return int(a)


def taginfo(link, num_tags = None, return_sort = True, print_page_count = False):
    """ Get information about Stack Overflow and all Stack Exchange sites users' 
    tags (tags and corresponding tag points scored). 
    This could be directly used with wordcloud module for generating a tag cloud.

    Parameters
    ----------
    
    link : int or string
        For int case, we are assuming Stackoverflow site users. So, input as int
        is the user ID of the Stackoverflow user whose information is to be extracted. 
        For string case, it's the complete user profile link to the Stackexchange
        site and is intended to cover all Stack Exchange sites profiles.
                
        A. As example for int case, consider Stackoverflow's top reputation user Jon skeet.
        His Stack Overflow link is - "http://stackoverflow.com/users/22656/jon-skeet".
        So, we would have -
        link = 22656.

        B. As example for string case, one can generate Jon's meta.stackexchange tag cloud with -
        link = "http://meta.stackexchange.com/users/22656/jon-skeet" or
        link = "http://meta.stackexchange.com/users/22656".
                
    num_tags : int (default=-1)
        Number of tags to be tracked. Default is -1, which tracks all tags possible.

    return_sort : bool (default=True)
        This boolean flag decides whether the output list has the tags
        sorted by their counts. Since WordCloud module internally sorts 
        them anyway, so for performance one can turn it off.
        
    Output
    ------
    
    Output is a list of tuples. Each tuple holds tag name and its corresponding
    tag score.
    """

    # I. Setup parameters
    # Get start link (profile page's tag link)
    if str(link).find(".com")==-1:
        start_link = "http://stackoverflow.com/users/" + str(link) + "?tab=tags&sort=votes&page="
    else:
        start_link = link + "?tab=tags&sort=votes&page="
    
    # Html codes to be detected for parsing relevant info
    tag_start_str = " Tags\r\n"  # html parsing string to detect start of tag block
    newline_str = "\n"           # newline string
    timeout_max_pages = 100      # Max number of pages to be scanned (acts as a timeout criteria)
        
    
    # Detect the indices for newlines
    start_link0 = start_link + "1"
    soup = BeautifulSoup(requests.get(start_link0).text,"lxml")
    texts = soup.findAll(text=True)
    idx_nl = np.where([item.startswith(tag_start_str) for item in texts])[0]
    
    # If an invalid webpage were fed, we would have empty idx_nl. 
    # If so, exit out with None.
    if len(idx_nl)==0:
        return None

    if num_tags==None: 
        num_tags = int(texts[idx_nl[0]-1].replace(",",""))

    # Set number of tag pages to be scanned
    max_pages = timeout_max_pages
    if num_tags!=-1:
        max_pages = int(np.ceil(num_tags/52.0))+1        

    # II. Start processing per page basis to get tag name and their counts   
    tag_name = []
    tag_count = []
    for page_id in range(1,max_pages):
        
        if print_page_count==1:
            print("Processing page : " + str(page_id) + "/" + str(max_pages-1))
            sys.stdout.flush()
        
        # 1. Get link for each tag page iteratively. Extract text only info
        link = start_link + str(page_id)        

        # 2. Get webpage text data
        soup = BeautifulSoup(requests.get(link).text,"lxml")
        texts = soup.findAll(text=True)
            
        # 3. Get block of text data that contains tag info (name and score/count)
        start_idx = np.where([item.startswith(tag_start_str) for item in texts])[0][0]
        texts1 = np.array(texts[start_idx:])
        
        # 4. Detect ending index of tag block and thus crop out tag block
        N1 = 8 # parameter used for convolution to find start, stop of tag block   
        N2 = 2 # no. of newlines used right before each tag count
        sep_idx = np.where(np.convolve(texts1 == newline_str, np.ones(N1))==N1)[0]
        tagcode = texts1[sep_idx[0]-1 : sep_idx[1]]
        
        # 5. Get tag names and count
        idx1 = np.convolve(tagcode == newline_str, np.ones(N2),'same')>=N2
        idx2 = np.flatnonzero(idx1[1:] < idx1[:-1])+1
        page_tag_count = [toint(i.encode("utf-8")) for i in tagcode[idx2]]
        page_tag_name = [i.encode("utf-8") for i in tagcode[idx2+2]]
        
        ## 6. Finally accumulate data into output lists
        tag_name.append(page_tag_name)
        tag_count.append(page_tag_count) 
        
    # III. For a case when all tag counts are zeros, it would throw error.
    # So, for such a case, escape it by setting all counts to "1".
    if ((np.array(tag_count)==0).ravel()).all():
        tag_count = [(np.array(item)+1).tolist() for item in tag_count]

    # IV. Zip tag names and their counts into a list. Sort by counts if needed.
    info = zip(itertools.chain(*tag_name),itertools.chain(*tag_count))
    if return_sort:
        info = [info[idx] for idx in np.argsort([item[1] for item in info])[::-1]]
    return info
    
    
def tag_cloud(link=22656, num_tags = 200, image_dims = (400, 200), out_filepath = "TagCloud.png"):
    
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
    font_path = "fonts/ShortStack-Regular.ttf" # Font path    
    info = taginfo(link = link, num_tags = num_tags)
    if info==None: 
        print("Error : No webpage found!")
    else:    
        if len(info)==0:
            print("Error : No tags found!")
        else:         # Successfully extracted tag info
            WC = WordCloud(font_path=font_path, width=W, height=H, \
                    max_words=len(info)).generate_from_frequencies(info)
            WC.to_image().save(out_filepath)
            print("Tag Cloud Saved as " + out_filepath)
        