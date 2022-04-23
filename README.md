# WED: Weeb Emote Detection for Twitch Chat using ML

![NaM](assets/nam.png)

This service allows to check for the occurence of weeb emotes for a message in a given twitch chat using a neural network trained on some of the most popular emotes on twitch. Currently, third-party emotes (BTTV, FFZ and 7TV), global twitch emotes, and v1 sub-emotes are supported. Support for v2 emotes coming soon (Copesen).

## Installation:

* Install redis: see [documentation](https://redis.io/docs/getting-started)
* Install dependencies: pip install -r requirements.txt
* Setup .env: 
  * OAUTH=[oauth twitch token]
  * CLIENT_ID=[twitch client id]
  * FLASK_APP="main" 

## Run Server:

* Make sure a redis instance is running on port 6379. Run: <code>redis-server</code>
* Run: <code>flask run</code>

## API Endpoints:

BASE URL: http://localhost:5000/api/v1

#### Get weeb score:
**GET** <code>/hwis</code>

**BODY**: 
```json
{ 
  "channel": [channel name], 
  "message": [message] 
}
```
**RETURNS**: 
```json
{ 
  "response_code": 200, 
  "isWeeb": [boolean], 
  "confidence": [confidence for given assessment], 
  "number_of_weeb_terms": [count of weeb terms in given message for given channel] 
}
```

#### Join channel for caching:
**GET** <code>/join</code>

**BODY**:
```json
{
  "channel": [channel name]
}
```
**RETURNS**:
```json
{
  "response_code": 200
}
```
