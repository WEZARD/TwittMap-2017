from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json
import urllib2

'''
https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-django.html#python-django-deploy
'''

keywords = ['Sports, football, basketball, tennis, baseball, nba',
            'Game, data, lol, cs, devil may cry',
            'Technology, nodejs, java, python, database',
            'Weather, cloudy, rain, snow',
            'Food, restaurant, burger king, pepsi, chinese food, drink, pizza',
            'Fun, movie, ktv, theatre, bar, camel, marlboro',
            'Traffic, car, train, subway, bike',
            'Location, nyu, new york, usa, china',
            'App, twitter, facebook, weichat, snapchat, instagram',
            'Company, IBM, amazon, google, apple, hp, microsoft']


def index(request):
    # from test_data import SendData
    # sendData = SendData()
    # sendData.begin()
    return render(request, 'MapApp/map.html', {'app_name': 'TwittMap'})


def search(url, term):
    uri = url + term
    response = requests.get(uri)
    results = json.loads(response.text)
    return results


def getIndex(message):
    keyword_index = 0
    if message == 'Sports':
        keyword_index = 0
    elif message == 'Game':
        keyword_index = 1
    elif message == 'Technology':
        keyword_index = 2
    elif message == 'Weather':
        keyword_index = 3
    elif message == 'Food':
        keyword_index = 4
    elif message == 'Fun':
        keyword_index = 5
    elif message == 'Traffic':
        keyword_index = 6
    elif message == 'Location':
        keyword_index = 7
    elif message == 'App':
        keyword_index = 8
    elif message == 'Company':
        keyword_index = 9
    return keyword_index


def handle(es_request):
    message = es_request.POST.get('Search', None)
    keyword_index = getIndex(message)
    domain = 'https://******/twittmap/_search?size=9999&pretty=true&q='
    result = search(domain, keywords[keyword_index])
    print result
    
    myLength = int(result['hits']['total'])
    c_data = [res['_source']['coordinates'] for res in result['hits']['hits']]
    t_data = [res['_source']['twitts'] for res in result['hits']['hits']]
    s_data = [res['_source']['sentiment'] for res in result['hits']['hits']]
    
    print c_data 
    hits = len(c_data)
    length = {'hits': hits}
    coordinates = {}
    twitts = {}
    sentiments = {}

    for i in range(hits):
        if (c_data[i][0] < -90):
            c_data[i][0] += 180
        coordinates[i] = {'lat': c_data[i][1], 'lng': c_data[i][0]}
        twitts[i] = t_data[i]
        if(s_data[i]):
            sentiments[i] = s_data[i]
        else:
            sentiments[i] = "null"

    data = {'coordinates': coordinates, 'length': length, 'twitts': twitts, 'sentiments': sentiments}
    return JsonResponse(data)


def polling(request):
    message = request.GET.get('Search', None)
    old_len = request.GET.get('Num', None)
    keyword_index = getIndex(message)
    domain = 'https://******/twittmap/_search?size=9999&pretty=true&q='
    result = search(domain, keywords[keyword_index])
    new_len = int(result['hits']['total'])
    c_data = [res['_source']['coordinates'] for res in result['hits']['hits']]
    t_data = [res['_source']['twitts'] for res in result['hits']['hits']]
    s_data = [res['_source']['sentiment'] for res in result['hits']['hits']]
    hits = len(c_data)
    coordinates = {}
    twitts = {}
    sentiments = {}

    for i in range(hits):
        if (c_data[i][0] < -90):
            c_data[i][0] += 180
        coordinates[i] = {'lat': c_data[i][1], 'lng': c_data[i][0]}
        twitts[i] = t_data[i]
        if (s_data[i]):
            sentiments[i] = s_data[i]
        else:
            sentiments[i] = "null"

    data = {'coordinates': coordinates, 'new_len': new_len, 'old_len': old_len, 'twitts': twitts, 'sentiments': sentiments}
    return JsonResponse(data)

# Trigger this endpoint to subscribe SNS Twitt Topic for persisting twitts in ES
@csrf_exempt
def handle_sns(request):
    context = {"message": "Outside"}
    if request.method == "GET":
        return render(request, 'MapApp/map.html', {'app_name': 'TwittMap'})
    else:
        body = json.loads(request.body)
        if body['Type'] == "SubscriptionConfirmation":
            subscribleURL = body['SubscribeURL']
            urllib2.urlopen(subscribleURL).read()
        elif body['Type'] == "Notification":
            message = json.loads(json.loads(body["Message"]).get('default'))
            tweet = message.get('tweet')
            lat = message.get('lat')
            lng = message.get('lng')
            sentiment = message.get('sentiment')
            coordinate = [lat, lng]

            upload_data = {
                "twitts": tweet,
                "coordinates": coordinate,
                "sentiment": sentiment
            }
            print requests.post('https://******/twittmap/data', json=upload_data)
            context = {"message": "Notification"}

    return render(request, 'MapApp/map.html', context)
