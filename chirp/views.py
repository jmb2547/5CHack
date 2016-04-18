from firebase import firebase
from flask import render_template, request, redirect, url_for
from yelpapi import YelpAPI

import os
import requests
import json
import urllib
from chirp import app


BASE_URL = "http://api.brewerydb.com/v2/"
SEARCH_URL = "search?"



yelp_api = YelpAPI(os.environ['YELP_KEY'], os.environ['YELP_SECRET'],
                   os.environ['YELP_TOKEN'], os.environ['YELP_TOKEN_SECRET'])

firebase = firebase.FirebaseApplication('https://beergenius.firebaseio.com/',
                                        None)


@app.route("/")
def index():
    return render_template("index.html", search_page=True)


@app.route("/search")
def search():
    try:
        
        query = urllib.quote_plus(request.args.get("beer"))
        qtype = "beer"

        response = requests.get(BASE_URL + SEARCH_URL + "key=" + API_key + "&type=" + qtype + "&q=" + query)
        data = json.loads(response.content)
        
        
        beers = []
        for b in data['data']:
            dict1 = {}
            if 'name' in b.keys():
                dict1['name'] = b['name']
            if 'description' in b.keys():
                dict1['description'] = b['description']
            if 'labels' in b.keys():
                dict1['image'] = b['labels']['large']
            if 'id' in b.keys():    
                dict1['id'] = b['id']
            
            if len(dict1) == 4:
                beers.append(dict1)
            
            
        
#        return data['data'][0]['name']
#        businesses = [
#            {"image_url": i['image_url'][:-6] + 'ls.jpg', "name": i["name"],
#             "description": i["snippet_text"], "rating": i["rating_img_url"],
#             "id": i["id"]}
#            for i in yelp_rs['businesses']]
    except (YelpAPI.YelpAPIError):
        return "Oops! Error!"
    return render_template("index.html", businesses=beers,
                           search_page=True)


@app.route("/save", methods=["POST"])
def save():
    try:
        beer_id = request.form.get("id")
        beer_rs = requests.get(BASE_URL + "beer/" + beer_id + "/?key=" + API_key)
        data = json.loads(beer_rs.content)
        
        result_attr = {
            "image": data['data']['labels']['large'],
            "name": data['data']['name'],
            "description": data['data']["description"],
            "ibu": data['data']['ibu'],
            "abv": data['data']['abv'],
            "id": data['data']['id'],
            "srmId": data['data']['srmId'],
            "styleId": data['data']['styleId'],
            "og": data['data']['originalGravity']
        }
        
        result = firebase.post('/Beers/', result_attr)
        
    
#        business_id = request.form.get("id")
#        business_rs = yelp_api.business_query(id=business_id)
#        result = firebase.post('/Beers', {
#            "image_url": business_rs["image_url"][:-6] + "ls.jpg",
#            "name": business_rs["name"],
#            "description": business_rs["snippet_text"],
#            "rating": business_rs["rating_img_url"],
#            "id": business_rs["id"]
#        })
        return redirect(url_for("favorites"))
    except:
        return "Error!"


@app.route("/favorites")
def favorites():
    data = firebase.get("/Beers", None)
    beers = []
    for k in data:
        beers.append(data[k])
#    return render_template("index.html", businesses=beers,
#                           search_page=False)
    return render_template("garden.html",
                           search_page=False)

@app.route("/beer")
def beer():
    query = request.args.get("beer")
    qtype = "beer"

    response = requests.get(BASE_URL + SEARCH_URL + "key=" + API_key + "&type=" + qtype + "&q=" + query)
    data = json.loads(response.content)
    return data['data'][0]['name']
