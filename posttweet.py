from requests_oauthlib import OAuth1Session
import os
import json

# In your terminal please set your environment variables by running the following lines of code.
# export 'CONSUMER_KEY'='<your_consumer_key>'
# export 'CONSUMER_SECRET'='<your_consumer_secret>'

#consumer_key = os.environ.get("CONSUMER_KEY")
#consumer_secret = os.environ.get("CONSUMER_SECRET")

# Be sure to add replace the text of the with the text you wish to Tweet. You can also add parameters to post polls, quote Tweets, Tweet with reply settings, and Tweet to Super Followers in addition to other features.


def Get_oauth():
    oauth = OAuth1Session(
            "hoge",
            client_secret="fuga", 
            resource_owner_key="piyo",
            resource_owner_secret="naisho",
            )
    #print(oauth_values)
    return oauth

# Making the request
def post_tweet(result,convid):
    oauth = Get_oauth()
    if "opensea" in result:
        payload = {"text": "here we minted! https://opensea.io/assets/matic/"+"/".join(result.split("assets")[1].split("/")[1:3]),"reply":{"in_reply_to_tweet_id": f"{convid}"}}
        response = oauth.post(
            "https://api.twitter.com/2/tweets",
            json=payload,
        )
        print("Response code: {}".format(response.status_code))

        # Saving the response as JSON
        json_response = response.json()
        print(json.dumps(json_response, indent=4, sort_keys=True))
    else:
        payload = {"text":  "fail to mint! fix it @hyper0dietter"}
        response = oauth.post(
            "https://api.twitter.com/2/tweets",
            json=payload,
        )
        print("Response code: {}".format(response.status_code))

        # Saving the response as JSON
        json_response = response.json()
        print(json.dumps(json_response, indent=4, sort_keys=True))

