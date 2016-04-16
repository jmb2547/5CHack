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
API_key = "b23f19cf8c791e60adbf1fd26fa892d6"


yelp_api = YelpAPI(os.environ['YELP_KEY'], os.environ['YELP_SECRET'],
                   os.environ['YELP_TOKEN'], os.environ['YELP_TOKEN_SECRET'])

firebase = firebase.FirebaseApplication('https://yelphackweek.firebaseio.com/',
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
            
            if len(dict1) == 3:
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
        business_id = request.form.get("id")
        business_rs = yelp_api.business_query(id=business_id)
        result = firebase.post('/Restaurants', {
            "image_url": business_rs["image_url"][:-6] + "ls.jpg",
            "name": business_rs["name"],
            "description": business_rs["snippet_text"],
            "rating": business_rs["rating_img_url"],
            "id": business_rs["id"]
        })
        return redirect(url_for("favorites"))
    except (YelpAPI.YelpAPIError):
        return "Error!"


@app.route("/favorites")
def favorites():
    restaurants = firebase.get("/Restaurants", None)
    businesses = []
    for k in restaurants:
        businesses.append(restaurants[k])
    return render_template("index.html", businesses=businesses,
                           search_page=False)

@app.route("/beer")
def beer():
    query = request.args.get("beer")
    qtype = "beer"

    response = requests.get(BASE_URL + SEARCH_URL + "key=" + API_key + "&type=" + qtype + "&q=" + query)
    data = json.loads(response.content)
    return data['data'][0]['name']
