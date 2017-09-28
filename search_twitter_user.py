#!/usr/bin/python
#-*- coding:utf-8 -*-
"""
任意のテキストによるTwitterサーチを利用して、
twitterユーザを探し出すためのUtility。
"""

from requests_oauthlib import OAuth1Session
import json
import traceback

def search_twitter_users(oauth_client, query="エンジニア"):
    """
    テキストによるTwitterサーチを利用して、Twitterユーザを検索する。
    デフォルトは、「エンジニア」という文字列でのTwitterサーチAPI
    https://dev.twitter.com/rest/public/search
    を利用することでユーザを見つけ出す。
    テキストを含むツイートをリツイートをしてるだけだった場合は、リツイートされているユーザのIDを返却する。
    Args:
        oauth_client:
        query: ユーザを見つけ出すための検索に用いる文字列。
    Returns:
        検索結果で出てきたツイートを行ったユーザのuser_id(数値)のセット。
        ex. [862938216, 375371082, 2420156958, 720565580881735680, 818373987768025089, 39003058, 100656188, 836217378824282112, 382402042, 4874196511, 765772220715139072, 831804997016760321, 704998000150466560, 92685240, 585402723]
    Raises:
        IOError: twitter APIを実行する際にエラーとなったときや, API responseのstatus codeが200以外だったとき
    """

    # tweet検索用のURL
    target_url = "https://api.twitter.com/1.1/search/tweets.json"


    # 検索に用いるテキストをクエリに与える
    params = {"q" : query, "count": 100}

    user_ids =[]
    try:
        # Search APIを使用
        response = oauth_client.get(target_url, params = params)

        if response.status_code == 200:
            # レスポンスはJSON形式なので parse する
            statuses = json.loads(response.text)["statuses"]
            for status in statuses:
                if status.has_key("retweeted_status"):
                    # 誰かのリツイートだった場合
                    user_id = status["retweeted_status"]["user"]["id"]
                    #print status["retweeted_status"]["user"]["screen_name"]
                else:
                    user_id = status["user"]["id"]
                    #print 
                #print status["user"]["screen_name"]
                user_ids.append( user_id )
        else:
            # status code 200 OK 以外が返ってきた
            raise IOError("couldn't get users by twitter's search API. query="+ str(query))
    except:
        raise IOError("unexpected error occurred while consuming twitter's search API. query="+ str(query) +", stacktrace="+ traceback.format_exc())
    
    return set(user_ids)


# このスクリプト自体を実行してテスト
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
    print search_twitter_users(twitter_client)
    
    

