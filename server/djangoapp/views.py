# Uncomment the required imports before adding the code

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data["userName"]
    password = data["password"]
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)


# Create a `logout_request` view to handle sign out request
def logout(request):
    data = {"userName": ""}  # Return empty username
    return JsonResponse(data)


# Create a `registration` view to handle sign up request
# @csrf_exempt
@csrf_exempt
def registration(request):
    context = {}

    # Load JSON data from the request body
    data = json.loads(request.body)
    username = data["userName"]
    password = data["password"]
    first_name = data["firstName"]
    last_name = data["lastName"]
    email = data["email"]
    username_exist = False
    email_exist = False
    try:
        # Check if user already exists
        User.objects.get(username=username)
        username_exist = True
    except:
        # If not, simply log this is a new user
        logger.debug("{} is new user".format(username))

    # If it is a new user
    if not username_exist:
        # Create user in auth_user table
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email,
        )
        # Login the user and redirect to list page
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
        return JsonResponse(data)
    else:
        data = {"userName": username, "error": "Already Registered"}
        return JsonResponse(data)


def get_cars(request):
    count = CarMake.objects.filter().count()
    print(f"Número de marcas encontradas: {count}")

    if count == 0:
        initiate()  # Esto poblará la base de datos si está vacía

    car_models = CarModel.objects.select_related("car_make")
    cars = []
    for car_model in car_models:
        cars.append(
            {
                "car_model": car_model.name,
                "car_make": car_model.car_make.name,
                "type": car_model.type,
                "year": car_model.year,
                "dealer_id": car_model.dealer_id,
            }
        )
    return JsonResponse({"CarModels": cars})


# # Update the `get_dealerships` view to render the index page with
# a list of dealerships
def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})


# Create a `get_dealer_reviews` view to render the reviews of a dealer
def get_dealer_reviews(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchReviews/dealer/" + str(dealer_id)
        reviews = get_request(endpoint)

        for review_detail in reviews:
            # Llamamos a la función de sentimiento
            response = analyze_review_sentiments(review_detail["review"])

            # VALIDACIÓN: Solo asignamos si la respuesta no es None
            if response is not None and "sentiment" in response:
                review_detail["sentiment"] = response["sentiment"]
            else:
                # Valor por defecto si falla el servicio
                review_detail["sentiment"] = "neutral"

        return JsonResponse({"status": 200, "reviews": reviews})


# Create a `get_dealer_details` view to render the dealer details
# djangoapp/views.py


def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchDealer/" + str(dealer_id)
        dealership = get_request(endpoint)

        # El microservicio suele devolver una lista.
        # Si es así, tomamos el primer (y único) elemento.
        if isinstance(dealership, list) and len(dealership) > 0:
            dealership = dealership[0]

        return JsonResponse({"status": 200, "dealer": dealership})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


# Create a `add_review` view to submit a review
# djangoapp/views.py


@csrf_exempt
def add_review(request):
    # Verificamos que el método sea POST
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # Asegúrate de haber importado post_review de .restapis
            response = post_review(data)
            return JsonResponse({"status": 200})
        except Exception as e:
            logger.error(f"Error en add_review: {e}")
            return JsonResponse({"status": 401, "message": "Error in posting review"})

    # Si llega un GET, aquí es donde devuelve el 405
    return JsonResponse({"status": 405, "message": "Method not allowed"})
