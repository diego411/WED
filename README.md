# WED: Weeb Emote Detection for Twitch Chat using ML

![NaM](assets/nam.png)

This service allows to check for the occurence of weeb emotes for a message in a given twitch chat using a neural network trained on some of the most popular emotes on twitch. Third-party emotes (BTTV, FFZ and 7TV), global twitch emotes, and sub-emotes are supported.

## Installation:

* Install redis: see [documentation](https://redis.io/docs/getting-started)
* Install dependencies: pip install -r requirements.txt
* Setup .env: 
  * OAUTH=[oauth twitch token]
  * CLIENT_ID=[twitch client id]
  * FLASK_APP="main" 
  * REDIS_HOST
  * REDIS_PORT
  * EXPIRING_RATE=18000 //Cached values will expire after 5h.

## Run Server:

* Make sure a redis instance is running on port 6379. Run: <code>redis-server</code>
* Run: <code>flask run</code>

## API Endpoints:

BASE URL: http://localhost:5000/api/v1

#### Get weeb score:
**GET** <code>/hwis</code>

**MINIMAL BODY**: 
```json
{ 
  "channel": channel name, 
  "message": message 
}
```
**RETURNS**: 
```json
{ 
  "response_code": 200, 
  "isWeeb": boolean, 
  "confidence": confidence for given assessment, 
  "number_of_weeb_terms": count of weeb terms in given message for given channel 
}
```
Optinally, the parameter "emotes" can be passed, which should consist of a map of every first party emote name in the message to its corresponding emote id.

**EXAMPLE BODY:**
```json
{
  "channel": "forsen",
  "message": "Kappa = Grey Face (no space)",
  "emotes": {
    "Kappa": 25
  }
}
```
The response looks the same. Note that, in this example no check regarding if Kappa actually has the id 25 is made. The API trusts that you provide it with the right ids and with every first party emote in the message. With the help of this parameter db hits for sub-emotes are enabled.

#### Get joined channels:
**GET** <code>/channels</code>

**RETURNS:**
```json
{
  "response_code": 200,
  "channels": [channel names]
}
```

#### GET stored scores:
**GET** <code>/scores</code>

**RETURNS**:
```json
{
  "response_code": 200,
  "scores": [{
    "id": emote id,
    "name": emote name,
    "score": score for emote
  }]
}
```

#### POST whitelist term:
**POST** <code>/whitelist</code>

**BODY**
```json
{
  "term": term to whitelist
}
```

**RETURNS**
```json
{
  "response_code": 200
}
```

#### GET whitelist:
**GET** <code>/whitelist</code>

**RETURNS**
```json
{
  "response_code": 200,
  "whitelist": [whitelisted terms]
}