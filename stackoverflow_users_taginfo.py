from bs4 import BeautifulSoup
import numpy as np
import requests
import itertools


def toint(a):
    """ Convert string to int and also scale them accordingly if they end 
    in "k", "m" and "b".
    """         
    weights = {'k': 1000, 'm': 1000000, 'b': 1000000000}
    if len(a)>1:
        if a[-1] in weights:
            return weights[a[-1]] * int(a[:-1])
    return int(a)


def taginfo(user_id, num_tags = -1, return_sort = True):
    """ Get information about Stackoverflow users' tags (tags and corresponding 
    tag points scored). This could be directly used with wordcloud module for 
    getting a tag cloud.

    Parameters
    ----------
    
    user_id : int
        User ID of the Stackoverflow user whose information is to be extracted. 
        Thus, from Jon skeet's Stackoverflow link - 
        http://stackoverflow.com/users/22656/jon-skeet, his user_id would be : 22656.
        
    num_tags : int (default=-1)
        Number of tags to be tracked. Default is -1, which tracks all tags possible.

    return_sort : bool (default=False)
        This boolean flag decides whether the output list has the tags
        sorted by their counts. Since WordCloud module internally sorts 
        them anyway, so the default value is kept as False.
        
    Output
    ------
    
    Output is a list of tuples. Each tuple holds tag name and its corresponding
    tag score. Please note that this is not in sorted order.
    """

    N = 8 # parameter used for convolution to find start, stop of tag block
    start_link = "http://stackoverflow.com/users/" + str(user_id) + "?tab=tags&sort=votes&page="
    
    tag_start_str = " Tags\r\n"  # html parsing string to detect start of tag block
    newline_str = "\n"           # newline string
    mult_str =  "\xc3\x97"       # utf-8 encoded hex string as they appear right after each tag name
    nobreak_str = "\xc2\xa0"     # utf-8 encoded no-break space that appears after hex string

    # Calculate number of tag pages to be scanned
    timeout_max_pages = 100
    if num_tags!=-1:
        max_pages = int(np.ceil(num_tags/52.0))+1
    else:
        max_pages = timeout_max_pages

    # Start processing      
    tag_name = []
    tag_count = []
    pagestartID = 1     
    for page_id in range(pagestartID,max_pages):
        
        # Get link for each tag page iteratively
        link = start_link + str(page_id)
        
        # Only extract text from page
        soup = BeautifulSoup(requests.get(link).text)
        texts = soup.findAll(text=True)
        
        # Crop out tag block from the text
        # 1. Detect starting index of tag block
        start_idx = np.where([item.startswith(tag_start_str) for item in texts])[0]
        texts1 = texts[start_idx:]
            
        # 2. Detect ending index of tag block
        stop_idx = np.where(np.convolve([item.startswith(newline_str) for item in texts1],np.ones(N),'same')>=N)[0] - N/2
        tag_block = texts[start_idx+stop_idx[0]+N:start_idx+stop_idx[1]]
        if len(tag_block)==0:
            break
        
        # Mask that has detected newlines and hex strings (to be removed as irrelevant) 
        newline_str_mask = np.array([item.startswith(newline_str) for item in tag_block])        
        mult_str_mask = np.array([item.encode("utf-8").startswith(mult_str) for item in tag_block])        

        # Mask that has detected no-break space and the next string  (to be removed as irrelevant)
        mask2 = np.convolve([item.encode("utf-8").startswith(nobreak_str) for item in tag_block],np.ones(2),'same')>0

        # Get rid of irrelevnt info, leaving us with tag names and counts
        select_idx = np.where(~(newline_str_mask | mult_str_mask | mask2))[0]
        out_info = [str(tag_block[id]) for id in select_idx]

        # Separate out names and counts into two lists
        tag_name.append(out_info[1::2])
        tag_count.append([toint(item) for item in out_info[::2]])
    
    # Zip tag names and their counts into a list. Sort by counts if needed.
    info = zip(itertools.chain(*tag_name),itertools.chain(*tag_count))
    if return_sort:
        info = [info[idx] for idx in np.argsort([item[1] for item in info])[::-1]]
    return info
