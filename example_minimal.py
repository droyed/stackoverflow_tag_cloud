from stackoverflow_users_taginfo import taginfo
from wordcloud import WordCloud

info = taginfo(link = 22656, num_tags = 200)
WordCloud().generate_from_frequencies(info).to_image().save('TagCloud.png')
