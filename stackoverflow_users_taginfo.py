from bs4 import BeautifulSoup
import numpy as np
import requests
import itertools

def toint(a):
    """ Convert string to int and also scale them accordingly if they end 
    in "k", "m" or "b".
    """         
    weights = {'k': 1000, 'm': 1000000, 'b': 1000000000}
    if len(a)>1:
        if a[-1] in weights:
            return weights[a[-1]] * int(a[:-1])
    return int(a)


def taginfo(link, num_tags = -1, return_sort = True):
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
    mult_str =  "\xc3\x97"       # utf-8 encoded hex string as they appear right after each tag name
    nobreak_str = "\xc2\xa0"     # utf-8 encoded no-break space that appears after hex string
    timeout_max_pages = 100      # Max number of pages to be scanned (acts as a timeout criteria)

    # Set number of tag pages to be scanned
    max_pages = timeout_max_pages
    if num_tags!=-1:
        max_pages = int(np.ceil(num_tags/52.0))+1        

    # II. Start processing per page basis to get tag name and their counts   
    tag_name = []
    tag_count = []
    for page_id in range(1,max_pages):
        
        # 1. Get link for each tag page iteratively. Extract text only info
        link = start_link + str(page_id)        
        soup = BeautifulSoup(requests.get(link).text,"lxml")
        texts = soup.findAll(text=True)
        
        # 2.Crop out tag block from the text
        ## Detect starting index of tag block and crop "texts" starting at it
        start_idx = np.where([item.startswith(tag_start_str) for item in texts])[0]
        if len(start_idx)==0:
            # Error : Tag block start not found. Most probably the profile does not exist!
            return -1
        texts1 = texts[start_idx:]
            
        ## Detect ending index of tag block and thus crop out tag block
        N = 8 # parameter used for convolution to find start, stop of tag block        
        stop_idx = np.where(np.convolve([item.startswith(newline_str) for item in texts1],np.ones(N),'same')>=N)[0] - N/2
        tag_block = texts[start_idx+stop_idx[0]+N:start_idx+stop_idx[1]]
        if len(tag_block)==0:
            break

        # 3. Remove irrelevant text from tag block
        ## Masks to detect newlines and hex strings
        newline_str_mask = np.array([item.startswith(newline_str) for item in tag_block])        
        mult_str_mask = np.array([item.encode("utf-8").startswith(mult_str) for item in tag_block])        

        ## Common mask to detect no-break space and the immediate next string
        nobreak_str_mask = np.convolve([item.encode("utf-8").startswith(nobreak_str) for item in tag_block],np.ones(2),'same')>0

        # Remove irrelevnt info with masks, leaving us with tag names and counts
        select_idx = np.where(~(newline_str_mask | mult_str_mask | nobreak_str_mask))[0]
        out_info = [str(tag_block[id]) for id in select_idx]

        ## 4. Finally separate out names and counts into two lists
        tag_name.append(out_info[1::2])
        tag_count.append([toint(item) for item in out_info[::2]])
        
    # III. For a case when all tag counts are zeros, it would throw error.
    # So, for such a case, escape it by setting all counts to "1".
    if ((np.array(tag_count)==0).ravel()).all():
        tag_count = [(np.array(item)+1).tolist() for item in tag_count]

    # IV. Zip tag names and their counts into a list. Sort by counts if needed.
    info = zip(itertools.chain(*tag_name),itertools.chain(*tag_count))
    if return_sort:
        info = [info[idx] for idx in np.argsort([item[1] for item in info])[::-1]]
    return info

    