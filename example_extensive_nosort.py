from stackoverflow_users_taginfo import taginfo
from wordcloud import WordCloud

# Parameters
user_id = 22656                    # User ID from user's profile
n_tags = 200                       # Max number of tags to be plotted on image
W = 1920; H = 1200                 # Wordcloud image size parameters
outfile = "examples/TagCloud_extensive_Sketch Serif.png"  # image o/p filename
font_path = "fonts/Sketch Serif.ttf"   # Font path

info = taginfo(user_id, num_tags=n_tags, return_sort = False)
WC = WordCloud(font_path=font_path,width=W, height=H, max_words=n_tags).generate_from_frequencies(info)
WC.to_image().save(outfile)