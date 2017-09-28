#!/usr/bin/python
#-*- coding:utf-8 -*-

"""
twitterのフォロワー数を自動的に増やしていくためのツール。
普段はユーザを探索してフォローし、フォロー上限に当たった場合はモードを0に切り替えて「自分をフォローしてくれていない人をアンフォローする」という動作を行う。
これ以上アンフォローできるユーザが居なくなった場合は再びモードを1に切り替えて

"""

import yaml
import os
import twitter_util
import search_twitter_user
from datetime import datetime
from requests_oauthlib import OAuth1Session
import sys
import random

#----------------------------
def get_config( config_filepath = os.path.dirname(os.path.abspath(__file__)) +"/config.yaml" ):
	"""
	yaml形式の設定ファイルを読み込んで辞書形式で返却する
	"""
	with open( config_filepath, "r") as f:
		return yaml.load( f.read() )

#----------------------------
def get_mode(mode_filepath):
    """
    0か1の数字が書かれたファイルから中の数字を読み取って
    数字で返す
    """

    # ファイルの1行目に書かれている数字を数値で返す
    with open( mode_filepath, "r" ) as f:
        for line in f:
            return int( line.rstrip() )

#---------------------------
def update_mode( mode, mode_filepath = os.path.dirname(os.path.abspath(__file__)) +"/mode.txt" ):
    """
    モード0 (ユーザを探索して誰かをフォローするモード)と
    モード1 (フォロー上限に達したので誰かをアンフォローするモード)を切り替える
    Args:
        mode: 更新したいモード数値
        mode_filepath: モード数値を保存するテキストファイルのパス
    Returns:
        なし
    """
    with open( mode_filepath, "w" ) as f:
        f.write( str(mode) )
    print "[%s] updated mode. new mode=%s" % (str(datetime.now()), str(mode))
    

#---------------------------
def unfollow_random_user(oauth_client):
    """
    twitterで自分をフォローしてくれていないユーザをランダムに一人選んでアンフォローする。

    Args:
      oauth_client: OAuth1Session object which is initiated with OAuth1Session(ConsumeKey, ConsumerSecret, AccessTokne, AccessTokenSecret)
    Returns:
     アンフォローに成功した場合はTrue, twitterサーバメンテなどでAPI実行に失敗した場合もTrueが返る仕様。
     もうアンフォロー対象が居ない場合だけ、Falseが返却される。

    """
    # seek  following users who are not following me
    target_user_ids = twitter_util.find_users_not_following_me(twitter_client)

    # もうアンフォロー対象が居ない場合はFalseを返却する
    if len(target_user_ids) == 0:
        print "[%s] There is no user to unfollow. " % ( str(datetime.now()) )
        return False

    # randomly choose a user
    target_user_id = random.choice( target_user_ids )
    
    # get user information and unfollow
    user_info = twitter_util.show_user( twitter_client,  target_user_id )
    unfollow_succeeded = twitter_util.unfollow( twitter_client, target_user_id )

    if unfollow_succeeded:
        print "[%s] successfully unfollow a user. user_id=%s, screen_name=%s" % (str(datetime.now()), target_user_id, user_info["screen_name"] )
    else:
        print "[%s] failed to unfollow a user. user_id=%s" % (str(datetime.now()), target_user_id)

    return True

#---------------------------
def follow_random_user( oauth_client, query, followed_filepath = os.path.dirname(os.path.abspath(__file__)) +"/once_followed_user_ids.txt" ):
    """
    誰かしらフォローできるユーザをみつけてフォローする。
    ただし、過去に一度でもフォローしたことがある人はフォローしない。
    (何度もフォローすると迷惑なので)
    Args:
        oauth_client: OAuth1Session object which is initiated with OAuth1Session(ConsumeKey, ConsumerSecret, AccessTokne, AccessTokenSecret)
        query: フォローすべきユーザを検索するときに使用するクエリ文字列
        followed_filepath: 過去一度でもフォローしたことがあるユーザID一覧を保管しているテキストファイルのパス

    Returns:
     フォローに成功した場合はTrue, twitterサーバメンテなどでAPI実行に失敗した場合もTrueが返る仕様。
     フォロー数上限に達しておりフォローできない場合だけ、Falseが返却される。
    """
    user_id_set = search_twitter_user.search_twitter_users(oauth_client, query)
    follow_ok_flag = False
    # 過去に一度でもフォローしたことがある人は避けて
    for user_id in user_id_set:
        user_id_to_follow = user_id
        if not once_followed( user_id_to_follow ):
            follow_ok_flag = True
            break
        
    # 過去に一度でもフォローしたことがある人しか見つからなかった場合はTrueを返却して終わらせる (レアケース)
    if follow_ok_flag == False:
        return True

    # フォローする
    res = twitter_util.follow( oauth_client, user_id_to_follow )
    
    if res==True: #フォロー成功
        # フォローしたことある人リストに加えておく
        # ユーザ情報をログ出力
        user_info = twitter_util.show_user( oauth_client, user_id_to_follow )
        print "[%s] successfully followed a user. user_id=%s, screen_name=%s" % ( str(datetime.now()), str(user_id_to_follow), user_info["screen_name"] )
        add_once_followed_list( user_id_to_follow )
        return True
    else: # フォロー失敗。フォロー数上限に当たったのでこれ以上フォローできない場合
        print "[%s] cannot follow a user. 'follow_random_user' function will return False." % ( str(datetime.now() ) )
        return False

#---------------------------
once_followed_id_set = set()
def read_followed_id_set( followed_filepath = os.path.dirname(os.path.abspath(__file__)) +"/once_followed_user_ids.txt" ):
    """
    followed_filedpathの各行に書いてあるuser_idをsetとして読み込む。
    過去に一度でもフォローしたことがあるユーザのID setとして使用する。

    returns:
        読み込んだユーザID set.
        ただし何度もファイルを読み込まないように、グローバル変数としてuser ID setは保持するので
        この関数を何度も使わないこと
    """
    global once_followed_id_set
    with open( followed_filepath, "r" ) as f:
        for line in f:
            user_id = int( line.rstrip() )
            once_followed_id_set.add( user_id )

#---------------------------
def once_followed( user_id, followed_filepath = os.path.dirname(os.path.abspath(__file__)) +"/once_followed_user_ids.txt" ):
    """
    followed_filedpathに書いてあるテキストファイルに、指定されたユーザIDが含まれているかどうかを判断する。
    Args:
        user_id: 判別するユーザID
        followed_filepath: 過去一度でもフォローしたことがあるユーザID一覧を保管しているテキストファイルのパス
    """
    global once_followed_id_set

    # まだ一度も読み込んでいない場合は読み込む
    if len( once_followed_id_set ) == 0:
        read_followed_id_set( followed_filepath )

    if user_id in once_followed_id_set:
        return True
    else:
        return False

#---------------------------
def add_once_followed_list( user_id, followed_filepath = os.path.dirname(os.path.abspath(__file__)) +"/once_followed_user_ids.txt" ):
    """
    一度でもフォローしたことある人リストにユーザを追加する
    Args:
        user_id: 追加するユーザID数値
        followed_filepath: 一度でもフォローしたことある人のユーザIDを各行に保存するテキストファイルへの絶対パス
    """

    # "a"は追記モード（ファイルが存在しない場合は新規作成される)
    with open( followed_filepath, "a") as f:
        f.write( str(user_id) + "\n")

#---------------------------

if __name__ == "__main__":

    config = get_config()
    CK = config["consumer_key"]
    CS = config["consumer_secret"]
    AT = config["access_token"]
    AS = config["access_token_secret"]
    twitter_client = OAuth1Session(CK, CS, AT, AS)
    
    # mode 取得
    mode = get_mode( config["mode_filepath"] )
   
    # もうこれ以上フォローできないモード
    if mode==1:
        # 誰かアンフォローする
        res = unfollow_random_user(twitter_client)
        # もうアンフォローするユーザが居ない場合はモードを0に変更して終了
        if res == False:
            update_mode(0)
            
        # まだアンフォローするユーザが居る場合はモードを更新せず、次回もアンフォローを行う
        sys.exit()
    else:
        #フォローできる余裕があるモード
        # フォローする人を探索してフォローする
        res = follow_random_user(twitter_client, config["user_search_query"], config["once_followed_filepath"])
        if res==False:
            # フォロー数上限に達したときはモードを1に変更して終了する
            update_mode(1)

        # まだフォローできるときはモードを更新せず次回もフォローを行う
        sys.exit()
