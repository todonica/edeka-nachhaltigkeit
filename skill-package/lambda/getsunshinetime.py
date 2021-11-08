import datetime
import pytz
def getsunshinetime(weather,start,end):
    
    timeFrom = None
    timeTo = None
    for i in range(1,40): #Go through Daily forecast
        hourly = weather['hourly'][i] # weather at current hour
        weatherBefore = weather['hourly'][i - 1] # weather last hour
        weatherAfter = weather['hourly'][i + 1]  # weather next hour
        weatherDateTime = datetime.datetime.fromtimestamp(hourly['dt']) # extract timestamp
        if weatherDateTime.date() == datetime.datetime.now().date(): # only continue if date matches
            if weatherDateTime.time() > datetime.datetime.now().time() and start < weatherDateTime.time() < end: # only continue if time is past now
                weatherType = hourly["weather"][0]["main"] # extract weathertype
                if  weatherType == "Rain" or weatherType == "Drizzle" or weatherType == "Snow"  or weatherType == "Tornado": # check if its bad weather
                    pass
                else:
                    if not timeFrom: # if good weather set start time of good weather period
                        timeFrom = weatherDateTime.time() 
                    if timeTo and weatherBefore == "Rain" or weatherBefore == "Drizzle" or weatherBefore == "Snow"  or weatherBefore == "Tornado": #If endtime is set and there is bad weather break ot of loop because we found hour interval
                        break
                    else:
                        timeTo = weatherDateTime.time()
    getwet = None
    if not start or not end: #if its raining all day long we notice it in getwet
        getwet = True
    
    return start, end, getwet