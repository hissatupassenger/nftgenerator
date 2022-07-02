
# -*- coding: utf-8 -*-
import string
import requests
import os
import json
import get_tweets
import subprocess
from datetime import datetime
from eth_keys import keys
import time
import posttweet


bearer_token = os.environ.get("BEARER_TOKEN")
pk = keys.PrivateKey(b'\x79\x6F\x75\x72\x20\x70\x72\x69\x76\x61\x74\x65\x20\x61\x64\x64\x72\x65\x73\x73')
kiyoshi_address = pk.public_key.to_checksum_address()


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FilteredStreamPython"
    return r


def get_rules():
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", auth=bearer_oauth
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json(),ensure_ascii = False))
    return response.json()


def delete_all_rules(rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print(json.dumps(response.json(),ensure_ascii = False))


def set_rules(delete):
    # You can adjust the rules if needed
    sample_rules = [
        {"value": "CREATE NFT @NFTgen_crypto is:reply" , "tag": "CREATE NFT"},
    ]

# keyword
# ツイート本文に含まれるキーワードにマッチします。これはトークン化マッチです。つまり、キーワード文字列とツイート本文のトークン化されたテキストがマッチングされます。
# トークン化は、句読点、記号、Unicodeの基本プレーン区切り文字に基づいて単語を分割します。
# 例えば、「コカ・コーラが好き」というテキストを含むツイートは、次のようなトークンに分割されます。I, like, coca, cola.これらのトークンは、ルールで使用されているキーワード文字列と比較されます。
# 句読点（例：coca-cola）、記号、または区切り文字を含む文字列にマッチするには、キーワードを二重引用符で囲む必要があります。
# Example: pepsi OR cola OR "coca cola"

# "exact phrase match"	
# ツイート本文に含まれるフレーズに完全一致します。
# Example: ("Twitter API" OR #v2) -"filtered stream"

# @
# 指定されたユーザー名について言及しているツイートのうち、ユーザー名が認識可能なエンティティ（@を含む）である場合にマッチします。
# Example: (@twitterdev OR @twitterapi) -@twitter

# #
# ハッシュタグがツイート内で認識される場合、認識されたハッシュタグを含むツイートにマッチします。
# つまり、#thankuというルールは、#thankuというハッシュタグを含む投稿にはマッチしますが、#thankunextというハッシュタグを含む投稿にはマッチしません。
# Example: #thankunext #fanart OR @arianagrande

# is:reply
# ルールに合致する明示的な返信のみを配信する。否定することで、ルールに合致する返信を配信対象から除外することもできます。
# フィルター付きストリームで使用する場合、この演算子は元のツイートへの返信、引用ツイートでの返信、リツイートでの返信にマッチします。
# Example: from:twitterdev is:reply



    payload = {"add": sample_rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json(),ensure_ascii = False))


def get_stream(set):

    query_params = {'expansions': 'author_id,in_reply_to_user_id,referenced_tweets.id,attachments.poll_ids', 'tweet.fields':'conversation_id,referenced_tweets' }
# {'expansions': 'author_id,in_reply_to_user_id"
#'tweet.fields':'conversation_id"
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream", auth=bearer_oauth, stream=True, params = query_params
    )
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            
            

            if json_response["data"]["author_id"] == json_response["data"]["in_reply_to_user_id"]:
                print("NFT発行可能")
                url = get_tweets.create_url( json_response["data"]["conversation_id"])
                response= get_tweets.connect_to_endpoint(url)
                print(response)
                username = response["includes"]["users"][0]["username"]
                tweetID = json_response["data"]["conversation_id"]

                result = subprocess.run(["snap-tweet",f"https://twitter.com/{username}/status/{tweetID}","--locale","ja","--output-dir","/var/www/html/"],stdout=subprocess.PIPE)

                ##TweerID:O,auher:o,autherID:,Timestamp,Messege:o,signer,signiture,externalURL,Image

                MetaData = {"name":username+" "+str(datetime.now()), 
                            "description":response["data"][0]["text"],
                            "attributes": {
                                "id":tweetID,
                                "author":username,
                                "author_id":response["data"][0]["author_id"],
                                "timestamp":str(datetime.timestamp(datetime.now())),
                                "message":"Signed on Euphoria:\n\n"+response["data"][0]["text"],
                                "signer":pk.public_key.to_checksum_address(),
                                "signature":str(pk.sign_msg(bytes("Signed on Euphoria:\n\n"+response["data"][0]["text"],'utf-8'))),
                                },
                            "external_url":"https://twitter.com/"+username+"/status/"+tweetID,
                            "image":"http://www.nftgenerator.biz/snap-tweet-"+username+"-"+tweetID+"-ja.png"
                                            
                            }
                metafilename = username+tweetID+".json"
                with open("/var/www/html/"+metafilename,"w") as f:
                    json.dump(MetaData, f)
                onchain_metadir = "http://www.nftgenerator.biz/"+metafilename

                result = subprocess.run(["brownie","run","/root/nft-mix/scripts/simple_collectible/create_collectible.py","--network","polygon-main","--metafile",f"{onchain_metadir}"],stdout=subprocess.PIPE)
                result = str(result.stdout)
                print(result)
                print(json_response["data"]["conversation_id"])
                posttweet.post_tweet(result,json_response["data"]["conversation_id"])
                
            else:
                print("本人ではありません。NFT 発行不可能")


