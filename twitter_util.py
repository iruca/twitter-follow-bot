#!/usr/bin/python
#-*- coding:utf-8 -*-

from requests_oauthlib import OAuth1Session
import traceback
import json

"""
様々なTwitter APIを使うためのUtility
"""
def follow( oauth_client, user_id ):
    """
    特定のユーザをTwitterでフォローする.
    Args:
    oauth_client: Oauth認証されたクライアント
            (requests_oauthlibのOAuth1Sessionオブジェクト)
    user_id:    フォローする対象twitterユーザのuserId (数値)
    Returns:
        フォロー成功すればTrue, すでにフォローしていたなどの理由でフォローできなかったときはFalseを返却する。
    Raises:
        IOError:
            TwitterAPIの実行に失敗したとき。
            すでにフォローしているユーザを指定されたときはErrorはraiseされないが、存在しないuserIDを指定されたときはErrorとなる。
    """
    target_url = "https://api.twitter.com/1.1/friendships/create.json"

    # follow対象ユーザIDと相手に通知を送るかどうかのフラグ(True固定)
    params = {"user_id":user_id, "follow": True}

    try:
        # Follow API実行
        response = oauth_client.post(target_url, params = params)

        if response.status_code == 200:
            #フォロー成功
            return True
        else:
            #フォロー失敗
            return False
    except:
        raise IOError("Unexpected error occurred while consuming twitter's Follow API. user_id="+ str(user_id)+", stacktrace="+ traceback.format_exc() )

#-----------------
def find_users_not_following_me(oauth_client):
    """
    using twitter following API, find a following user who is not following back me.
    Args:
      oauth_client: OAuth1Session object which is initiated with OAuth1Session(ConsumeKey, ConsumerSecret, AccessTokne, AccessTokenSecret)
    Returns:
      user_id list of the users which are not following me but I'm following
    """

    # following (otherwise known as their friends)
    following_api_url = "https://api.twitter.com/1.1/friends/ids.json"
    follower_api_url = "https://api.twitter.com/1.1/followers/ids.json"

    user_ids =[]
    try:
        # API call to get following/follower users
        following_api_response = oauth_client.get(following_api_url)
        follower_api_response = oauth_client.get(follower_api_url)
        if following_api_response.status_code == 200 and follower_api_response.status_code == 200:
            # parse JSON
            following_user_ids = json.loads( following_api_response.text )["ids"]
            follower_user_ids = json.loads( follower_api_response.text )["ids"]

        else:
            # status code is not 200 OK
            print "follower_api_response-----------"
            print follower_api_response.content
            print "following_api_response----------"
            print following_api_response.content
            raise IOError("couldn't get following/follower users by twitter's  API.")

    except:
        raise IOError("unexpected error occurred while consuming twitter's following/follower API. stacktrace="+ traceback.format_exc())

    # return the diff of the following users and follower users
    return list( set( following_user_ids ) - set( follower_user_ids ) )

#--------------------
def unfollow( oauth_client, user_id ):
    """
    unfollow user
    """
    target_url = "https://api.twitter.com/1.1/friendships/destroy.json"
    params = { "user_id" : user_id }

    try:
        response = oauth_client.post(target_url, params=params )

        if response.status_code != 200:
            raise IOError("couldn't unfollow user. user_id="+ str(user_id) +", API response = "+ response.text )

        return True
    except:
        raise IOError("couldn't unfollow user. user_id="+ str(user_id) +", stack trace="+ traceback.format_exc() )

#---------------------
def show_user( oauth_client, user_id ):
    """
    show specific user's information
    Returns:
      user information dictionary object
    """
    target_url = "https://api.twitter.com/1.1/users/show.json?user_id="+ str(user_id)

    try:
        response = oauth_client.get(target_url )

        if response.status_code != 200:
            raise IOError("couldn't get user information. user_id="+ str(user_id) +", API response = "+ response.text )

        return json.loads( response.text )
    except:
        raise IOError("couldn't unfollow user. user_id="+ str(user_id) +", stack trace="+ traceback.format_exc() )

#----------------------
def get_following_user_ids(oauth_client):
    """
    現在フォローしているユーザのuser id一覧を配列の形で得る。
    Args:
      oauth_client: OAuth1Session object which is initiated with OAuth1Session(ConsumeKey, ConsumerSecret, AccessTokne, AccessTokenSecret)
    Returns:
      フォローしているユーザのuser_idのリスト
    """

    following_api_url = "https://api.twitter.com/1.1/friends/ids.json"

    user_ids =[]
    try:
        # API call to get following/follower users
        following_api_response = oauth_client.get(following_api_url)
        if following_api_response.status_code == 200:
            # parse JSON
            following_user_ids = json.loads( following_api_response.text )["ids"]
            return following_user_ids
        else:
            # status code is not 200 OK
            print "following_api_response----------"
            print following_api_response.content
    except:
        print traceback.format_exc()
        raise IOError("couldn't get following/follower users by twitter's  API.")

#----------------------

# このスクリプトを実行したら
if __name__ == "__main__":

    import sys
    import yaml
 
    # 設定ファイルからtokenを読み込み   
    with open("token.yaml", "r") as f:
        tokens = yaml.load( f.read() )
        CK = tokens["consumer_key"]
        CS = tokens["consumer_secret"]
        AT = tokens["access_token"]
        AS = tokens["access_token_secret"]

    twitter_client = OAuth1Session(CK, CS, AT, AS)

    # 一度でもフォローしたことがあるユーザのIDリスト
    with open("once_followed_user_ids.txt", "w") as f:
        user_ids = get_following_user_ids( twitter_client ) 
        for user_id in user_ids:
            f.write( str(user_id) +"\n" )
    
    
    
    
