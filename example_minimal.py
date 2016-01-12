from stackoverflow_users_taginfo import taginfo
from wordcloud import WordCloud

# Parameters
user_id = 22656                    # User ID from user's profile
n_tags = 200                       # Max number of tags to be plotted on image

info = taginfo(user_id, num_tags=n_tags)
WC = WordCloud().generate_from_frequencies(info)
WC.to_image().save('examples/TagCloud_minimal.png')