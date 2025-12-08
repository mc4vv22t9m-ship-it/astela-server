from flask import Flask, request, jsonify
import swisseph as swe
from datetime import datetime
import pytz

app = Flask(__name__)

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def deg_to_sign(deg):
    sign_index = int(deg // 30)
    sign_deg = deg % 30
    return {
        "sign": ZODIAC_SIGNS[sign_index],
        "degree": round(sign_deg, 2)
    }

def get_julian_day(year, month, day, hour, minute, second, timezone_str):
    local_tz = pytz.timezone(timezone_str)
    local_dt = local_tz.localize(datetime(year, month, day, hour, minute, second))
    utc_dt = local_dt.astimezone(pytz.utc)
    ut = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, ut)
    return jd_ut

@app.route("/natal", methods=["POST"])
def natal():
    data = request.get_json()

    try:
        year = int(data["year"])
        month = int(data["month"])
        day = int(data["day"])
        hour = int(data.get("hour", 12))
        minute = int(data.get("minute", 0))
        second = int(data.get("second", 0))

        timezone_str = str(data.get("timezone", "Europe/Belgrade"))
        lat = float(data["lat"])
        lon = float(data["lon"])

        raw_house = data.get("house_system", "P")
        house_system = str(raw_house)[0].upper().encode("ascii")

    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Missing or invalid parameters"}), 400

    jd_ut = get_julian_day(year, month, day, hour, minute, second, timezone_str)

    planet_ids = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mercury": swe.MERCURY,
        "Venus": swe.VENUS,
        "Mars": swe.MARS,
        "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN,
        "Uranus": swe.URANUS,
        "Neptune": swe.NEPTUNE,
        "Pluto": swe.PLUTO,
        "Mean_Node": swe.MEAN_NODE
    }

    planets = {}
    for name, pid in planet_ids.items():
        lonlat, _ = swe.calc_ut(jd_ut, pid)
        pos = deg_to_sign(lonlat[0])
        planets[name] = {
            "longitude": round(lonlat[0], 4),
            "sign": pos["sign"],
            "degree_in_sign": pos["degree"]
        }

    houses, ascmc = swe.houses(jd_ut, lat, lon, house_system)

    houses_list = []
    for i, cusp in enumerate(houses, start=1):
        pos = deg_to_sign(cusp)
        houses_list.append({
            "house": i,
            "cusp_longitude": round(cusp, 4),
            "sign": pos["sign"],
            "degree_in_sign": pos["degree"]
        })

    asc_pos = deg_to_sign(ascmc[0])
    mc_pos = deg_to_sign(ascmc[1])

    response = {
        "input": {
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "minute": minute,
            "second": second,
            "timezone": timezone_str,
            "lat": lat,
            "lon": lon,
            "house_system": raw_house
        },
        "julian_day_ut": jd_ut,
        "planets": planets,
        "houses": houses_list,
        "angles": {
            "ASC": {
                "longitude": round(ascmc[0], 4),
                "sign": asc_pos["sign"],
                "degree_in_sign": asc_pos["degree"]
            },
            "MC": {
                "longitude": round(ascmc[1], 4),
                "sign": mc_pos["sign"],
                "degree_in_sign": mc_pos["degree"]
            }
        }
    }

    return jsonify(response), 200
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)