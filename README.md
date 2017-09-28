# twitter-follow-bot
bot to automatically increase followers in twitter

## how to use
prepare config.yaml

config.yaml
```
# twitter API OAuth info
consumer_key: "{consumerKey}"
consumer_secret: "{consumerSecret}"
access_token: "{accessToken}"
access_token_secret: "{accessTokenSecret}"
# filepath to save a text file to save mode (mode 0 = increase following mode / mode 1 = unfollow uni-directional following mode )
mode_filepath: /root/twitter-follow-bot/mode.txt
# filepath to save a text file to save user Ids that you once ever followed
once_followed_filepath: /root/auto-twitter-follow/once_followed_user_ids.txt
# string to search users to follow
user_search_query: エンジニア
```
