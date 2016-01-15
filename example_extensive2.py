from stackoverflow_users_taginfo import taginfo
from wordcloud import WordCloud

# Parameters for wordcloud generation
W = 1920; H = 1200                         # Wordcloud image size (width, height)
font_path = "fonts/ShortStack-Regular.ttf" # Font path

info = taginfo(link = "http://meta.stackexchange.com/users/22656", num_tags = 200)
if info!=-1:  # Successfully extracted tag info
    WC = WordCloud(font_path=font_path, width=W, height=H, max_words=len(info)).generate_from_frequencies(info)
    WC.to_image().save('TagCloud.png')
