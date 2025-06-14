import requests
import datetime
import random
from django.shortcuts import render
from django.conf import settings

def nasa_apod(request):
    date = request.GET.get("date", None)
    random_request = request.GET.get("random", None)
    max_attempts = 10

    api_url = "https://api.nasa.gov/planetary/apod"
    base_params = {"api_key": settings.REMOVED}

    data = {}
    today = datetime.date.today().isoformat()

    if random_request or not date:
        for _ in range(max_attempts):
            start = datetime.date(1996, 1, 1)
            end = datetime.date.today()
            random_date = start + datetime.timedelta(days=random.randint(0, (end - start).days))

            params = base_params.copy()
            params["date"] = random_date.isoformat()

            try:
                resp = requests.get(api_url, params=params)
                resp.raise_for_status()
                json_data = resp.json()
                if json_data.get("media_type") == "image":
                    data = json_data
                    break
            except (requests.RequestException, ValueError):
                continue
        else:
            params = base_params.copy()
            params["date"] = today
            try:
                fallback = requests.get(api_url, params=params)
                fallback.raise_for_status()
                fallback_json = fallback.json()
                if fallback_json.get("media_type") == "image":
                    data = fallback_json
                else:
                    return render(request, "nasa_app/apod.html", {
                        "error": "No image found after several tries.",
                        "today": today
                    })
            except:
                return render(request, "nasa_app/apod.html", {
                    "error": "Unable to fetch data.",
                    "today": today
                })
    else:
        try:
            date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return render(request, "nasa_app/apod.html", {"error": "Invalid date format.", "today": today})

        for _ in range(max_attempts):
            params = base_params.copy()
            params["date"] = date_obj.isoformat()
            try:
                resp = requests.get(api_url, params=params)
                resp.raise_for_status()
                json_data = resp.json()
                if json_data.get("media_type") == "image":
                    data = json_data
                    break
            except (requests.RequestException, ValueError):
                date_obj -= datetime.timedelta(days=1)
        else:
            return render(request, "nasa_app/apod.html", {
                "error": "No image found near that date.",
                "today": today
            })

    context = {
        "title": data.get("title", "Unknown Title"),
        "image_url": data.get("url", ""),
        "explanation": data.get("explanation", "No explanation available."),
        "date": data.get("date", date),
        "media_type": data.get("media_type", ""),
        "today": today
    }
    return render(request, "nasa_app/apod.html", context)
