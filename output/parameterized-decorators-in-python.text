Title: Parameterized Decorators in Python   
Date: 2023-04-23             
Category: Python          
Tags: Python              
Authors: James D. Triveri                      
Summary: Using parameterized decorators in Python with applications   


A decorator is a function that takes another function and extends the behavior of the latter function without explicitly modifying it. 
In what follows, I demonstrate a practical use case for parameterized decorators focusing on units conversion. 

To illustrate, we refer to the `getspeed` function used to estimate the spped of the International Space Station w.r.t. the surface of 
the Earth. `getspeed` returns a scalar representing the average speed of the ISS over a given time differential. The result is returned 
in kilometers per hour, with no parameter available to apply a change of units. To incorporate this functionality, we can either (1) 
add a units parameter to change the units of the calculated speed prior to `getspeed` returning, or (2) implement a decorator  
specifying the units of the calculated value fully outside of `getspeed`. The declarations for `haverdist`, `getiss` and `getspeed`
are provided below:


```python
import datetime
import math
import os
import sys
import time
import requests


def haverdist(coords1, coords2):
    """
    Compute distance between geographic coordinate pairs.

    Parameters
    ----------
    coords1: tuple or list;
        (lat1, lon1) of first geolocation.
        
    coords2: tuple or list
        (lat2, lon2) of second geolocation.

    Returns
    -------
    float
        Distance in kilometers between coords1 and coords2.
    """
    # Convert degrees to radians then compute differences.
    R = 6367 
    rlat1, rlon1 = [ii * math.pi / 180 for ii in coords1]
    rlat2, rlon2 = [ii * math.pi / 180 for ii in coords2]
    drlat, drlon = (rlat2 - rlat1), (rlon2 - rlon1)
    inner = (math.sin(drlat / 2.))**2 + (math.cos(rlat1)) * \
            (math.cos(rlat2)) * (math.sin(drlon /2.))**2
    return(2.0 * R * math.asin(min(1., math.sqrt(inner))))


def getiss():
    """
    Get timestamped geo-coordinates of International Space Station.

    Returns
    -------
    dict
        Dictionary with keys "latitude", "longitude" and 
        "timestamp" indicating time and position of ISS. 
    """
    dpos = dict()
    resp = requests.get("http://api.open-notify.org/iss-now.json").json()
    if resp["message"] != "success":
        raise RuntimeError("Unable to access Open Notify API.")
    dpos["timestamp"] = resp["timestamp"]
    dpos["latitude"]  = float(resp["iss_position"]["latitude"])
    dpos["longitude"] = float(resp["iss_position"]["longitude"])
    return(dpos)


def getspeed(dloc1, dloc2):
    """
    Compute speed of ISS relative to Earth's surface using a pair of coordinates 
    retrieved via `getiss`. 

    Parameters
    ----------
    dloc1: dict
        Dictionary with keys "latitude", "longitude" "timestamp"
        associated with the first positional snapshot.
    dloc2: dict
        Dictionary with keys "latitude", "longitude" "timestamp"
        associated with the second positional snapshot.

    Returns
    -------
    float
        Scalar value representing the average speed in km/s of the
        International Space Station relative to the Earth in translation 
        from `dloc1` to `dloc2`. 
    """
    # Convert unix epochs to timestamp datetime objects.
    ts1  = datetime.datetime.fromtimestamp(dloc1['timestamp'])
    ts2  = datetime.datetime.fromtimestamp(dloc2['timestamp'])
    secs = abs((ts2-ts1).total_seconds())
    loc1 = (dloc1["latitude"], dloc1["longitude"])
    loc2 = (dloc2["latitude"], dloc2["longitude"])
    dist = haverdist(loc1, loc2)
    return((dist / secs) * 3600)
```


In this case, the first option seems like a good choice. But instead of a simple function like `getspeed`, imagine a different function 
(we'll call it `legacyfunc`) that we didn't author, which has been in production for a very long time, which has lots of unfamiliar
optional parameters and many more lines of code than `getspeed`, is responsible for returning the value, and this value is the one 
requiring a change of units. In this case, leaving `legacyfunc` unmodified and wrapping it's result with logic to handle the change of 
units would be preferable.

We'll implement a function to handle the change of units conversion. This will result in a parameterized decorator, the parameter 
indicating which units the final result should be converted to. For this example, the only options will be kilometers per hour or miles 
per hour, but the decorator can be extended to facilitate any number of additional distance or time conversions.


```python
"""
Demonstration of parameterized decorator to facilitate change of units conversion.
"""
import functools

def units(spec):
    """
    Specify the units to represent orbital speed. `spec` can be either "kmph" 
    (kilometer per hour) or "mph" (miles per hour). Defaults to "kmph".
    """
    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            result_init = function(*args, **kwargs)
            # result_init is result returned by original function.
            if spec=="mph":
                result = result_init * 0.62137119 
            else: 
                result = result_init
            return(result)
        return(wrapper)
    return(decorator)
```


Next, we modify `getspeed` by referencing the `units` decorator as follows:


```python
import functools


@units("mph")
def getspeed(dloc1, dloc2):
    """
    Compute speed of ISS relative to Earth's surface using
    a pair of coordinates retrieved from `getiss`. 

    Parameters
    ----------
    dloc1: dict
        Dictionary with keys "latitude", "longitude" "timestamp"
        associated with the first positional snapshot.
    dloc2: dict
        Dictionary with keys "latitude", "longitude" "timestamp"
        associated with the second positional snapshot.

    Returns
    -------
    float
        Scalar value representing the average speed of the International
        Space Station relative to the Earth going from ``dloc1`` to 
        ``dloc2``. 
    """
    # Convert unix epochs to timestamp datetime objects.
    ts1   = datetime.datetime.fromtimestamp(dloc1['timestamp'])
    ts2   = datetime.datetime.fromtimestamp(dloc2['timestamp'])
    secs  = abs((ts2-ts1).total_seconds())
    loc1  = (dloc1["latitude"], dloc1["longitude"])
    loc2  = (dloc2["latitude"], dloc2["longitude"])
    dist  = haverdist(geoloc1=loc1, geoloc2=loc2)
    vinit = (dist / secs) # kilometers per second
    return(vinit * 3600)
```

With this change, the scalar representing kilometers per hour returned by `getspeed` will be converted to miles per hour. Calling this 
can be confirmed by calling `getspeed`.

```python
In [2]: dpos1 = getiss(); time.sleep(5); dpos2 = getiss()
In [3]: getspeed(dpos1, dpos2)
Out[2]: 16126.21
```

A speed of 16126mph equates to ~26,000km/h, right around what we'd expected (Wikipedia puts the ISS average orbital velocity at ~27,000km/h).
