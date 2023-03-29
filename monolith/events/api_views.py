from django.http import JsonResponse
import json
from .models import Conference, Location, State
from common.json import ModelEncoder
from django.views.decorators.http import require_http_methods
from .acls import pexels_photo, get_weather


class ConferenceListEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name",
    ]


@require_http_methods(["GET", "POST"])
def api_list_conferences(request):
    """
    Lists the conference names and the link to the conference.

    Returns a dictionary with a single key "conferences" which
    is a list of conference names and URLS. Each entry in the list
    is a dictionary that contains the name of the conference and
    the link to the conference's information.

    {
        "conferences": [
            {
                "name": conference's name,
                "href": URL to the conference,
            },
            ...
        ]
    }
    """
    if request.method == "GET":
        conferences = Conference.objects.all()
        return JsonResponse({"conferences": conferences} , ConferenceListEncoder, safe=False)
    else:
        content = json.loads(request.body)
        try:
            location = Location.objects.get(id=content["location"])
            content["location"] = location
        except Location.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid Location Id"},
                status=400,
            )
    conference = Conference.objects.create(**content)
    return JsonResponse(
        conference,
        ConferenceDetailEncoder,
        safe=False,
    )


class LocationListEncoder(ModelEncoder):
    model = Location
    properties = [
        "name",
    ]


class LocationDetailEncoder(ModelEncoder):
    model = Location
    properties = [
        "name",
        "city",
        "room_count",
        "created",
        "updated",
        "picture_url",
    ]

    def get_extra_data(self, o):
        return {"state": o.state.abbreviation}


class ConferenceDetailEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name",
        "description",
        "max_presentations",
        "max_attendees",
        "starts",
        "ends",
        "created",
        "updated",
        "location",
    ]
    encoders = {
        "location": LocationListEncoder(),
    }


@require_http_methods(["GET", "DELETE", "PUT"])
def api_show_conference(request, id):
    """
    Returns the details for the Conference model specified
    by the id parameter.

    This should return a dictionary with the name, starts,
    ends, description, created, updated, max_presentations,
    max_attendees, and a dictionary for the location containing
    its name and href.

    {
        "name": the conference's name,
        "starts": the date/time when the conference starts,
        "ends": the date/time when the conference ends,
        "description": the description of the conference,
        "created": the date/time when the record was created,
        "updated": the date/time when the record was updated,
        "max_presentations": the maximum number of presentations,
        "max_attendees": the maximum number of attendees,
        "location": {
            "name": the name of the location,
            "href": the URL for the location,
        }
    }
    """

    if request.method == "GET":
        conference = Conference.objects.get(id=id)
        weather = get_weather(
            conference.location.city, conference.location.state.abbreviation
        )

        return JsonResponse(
            {"conference": conference, "weather": weather},
            ConferenceDetailEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        count, _ = Location.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})
    else:
        content = json.loads(request.body)
        try:
            if "location" in content:
                location = Location.objects.get(
                    conferences=content["location"]
                )
                content["location"] = location
        except Location.DoesNotExist:
            return JsonResponse({"message": "Invalid Location"}, status=400)
        Conference.objects.filter(id=id).update(**content)
        conference = Conference.objects.get(id=id)
        return JsonResponse(conference, ConferenceDetailEncoder, safe=False)


@require_http_methods(["GET", "POST"])
def api_list_locations(request):
    """
    Lists the location names and the link to the location.

    Returns a dictionary with a single key "locations" which
    is a list of location names and URLS. Each entry in the list
    is a dictionary that contains the name of the location and
    the link to the location's information.

    {
        "locations": [
            {
                "name": location's name,
                "href": URL to the location,
            },
            ...
        ]
    }
    """
    if request.method == "GET":
        locations = [
            {
                "name": i.name,
                "href": i.get_api_url(),
            }
            for i in Location.objects.all()
        ]
        return JsonResponse({"conferences": locations})
    else:
        content = json.loads(request.body)
        # Get the State object and put it in the content dict
        try:
            state = State.objects.get(abbreviation=content["state"])
            content["state"] = state
        except State.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid state Abbreviation"},
                status=400,
            )
        photo = pexels_photo(content["city"], content["state"].abbreviation)
        content.update(photo)
        location = Location.objects.create(**content)
        return JsonResponse(location, LocationDetailEncoder, safe=False)


@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_location(request, id):
    """
    Returns the details for the Location model specified
    by the id parameter.

    This should return a dictionary with the name, city,
    room count, created, updated, and state abbreviation.

    {
        "name": location's name,
        "city": location's city,
        "room_count": the number of rooms available,
        "created": the date/time when the record was created,
        "updated": the date/time when the record was updated,
        "state": the two-letter abbreviation for the state,
    }
    """
    if request.method == "GET":
        location = Location.objects.get(id=id)
        return JsonResponse(
            location,
            LocationListEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        count, _ = Location.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})
    else:
        # Convert the jsonformatted string into a dict
        content = json.loads(request.body)
        # Convert state abbreviation into a state if it exists.
        try:
            if "state" in content:
                state = State.objects.get(abbreviation=content["state"])
                # Use the dict to update the existing Location
                content["state"] = state
        except State.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid state abbreviation"},
                status=400,
            )
        Location.objects.filter(id=id).update(**content)

        location = Location.objects.get(id=id)
        return JsonResponse(
            location,
            LocationDetailEncoder,
            safe=False,
        )
