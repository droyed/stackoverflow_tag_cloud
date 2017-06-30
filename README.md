[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

### Stack Overflow (Stack Exchange) Users Tag Cloud
[**Stack Exchange**](http://stackexchange.com/) is a network of `Q&A` websites covering various fields. Users earn reputation and score tag points based on the tags of the questions and answers they involve themselves with. Each user has a tag section under his/her profile page that lists the tag names and the respective counts. The Python scripts in this repository parse and extract the tag names and scores, which could then be fed to [wordcloud module for Python](https://github.com/amueller/word_cloud) to produce a word cloud image with tags being the words and their respective sizes being proportional to the respective scores. The scripts could extract such information from [**all Stack Exchange Q&A sites**](http://stackexchange.com/sites), including of course it's biggest `Q&A` site 
[**Stack Overflow**](http://stackoverflow.com/). Please note that the scripts work with the current (as of <s>Jan 11th, 2016</s> March 7th, 2017) webpage format used by Stack Exchange for storing user profiles and their tags information.

### Examples

Let's take Stack Overflow's highest reputation user [Jon Skeet](http://stackoverflow.com/users/22656/jon-skeet) as the sample. His profile page link has the ID : `22656`. So, a minimal Python script to generate his tag-cloud would be -

	from stackoverflow_users_taginfo import tag_cloud
	
	tag_cloud(link = 22656)


Giving it more options, here's a tag-cloud with the first **`1000`** tags on a `4K canvas` being produced using [example_extensive.py](https://github.com/droyed/stackoverflow_tag_cloud/blob/master/example_extensive.py) -

![Screenshot](https://raw.githubusercontent.com/droyed/stackoverflow_tag_cloud/master/example_output/example_extensive_output.png)

As a demo on extracting tag information and generating tag-cloud from other Q&A sites, here's a tag-cloud of [Jon Skeet's meta.stackexchange profile](http://meta.stackexchange.com/users/22656) generated with  [example_extensive2.py](https://github.com/droyed/stackoverflow_tag_cloud/blob/master/example_extensive2.py) -

![Screenshot](https://raw.githubusercontent.com/droyed/stackoverflow_tag_cloud/master/example_output/example_extensive2_output.png)

We are living in `8K` age, so here's [Jon Skeet's `1000` tags on `8K` canvas](https://raw.githubusercontent.com/droyed/stackoverflow_tag_cloud/master/example_output/8K.png)!

### Requirements
* Python 2.x.
* Python modules : NumPy, Requests, itertools.
* [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) - To extract html information. Works with version 4.4.1, might work with older versions too, but not tested. 
* [Word_cloud](https://github.com/amueller/word_cloud) - Word cloud creation.
