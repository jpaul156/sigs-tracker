import csv
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def scraper():

    ##
    ## Phase 1 numbers
    ## Pulled from back end of Google Form
    ##
    sheet = client.open_by_key("1a2TtKlmi_6Md6bYtMLWG1rUu8QWY4BetZRRchNsSp7E")
    global entriesWS
    entriesWS = sheet.worksheet("Form Responses 1")
    global entries
    entries = entriesWS.get_all_values()

    ##
    ## New check-off form
    ##
    sheet = client.open_by_key("1TTA0GAN_DksWCkytJdnm6MbBO_WMbkqqa8pBSEP15dw")
    global incomingWS
    incomingWS = sheet.worksheet("Sheet1")
    global incoming
    incoming = incomingWS.get_all_values()

    ##
    ## Signature Tracker
    ##
    sheet = client.open_by_key("1SIpW06l9QIKGX0IOnDXql1YNSMmZKNqUmRuxmKijNJ4")
    global trackerWS
    trackerWS = sheet.worksheet("Phase 1 Totals")


    for n, value in enumerate(entries[0]):
        if value == "Status":
            global statusCol
            statusCol = n

    for entry in entries:
        if entry[statusCol] == "": 
            newEntries.append(entry)


    if len(newEntries) == 0:
        trackerWS.update_acell("A2", updateTime)
    else:
        foundSome()


def foundSome():

    ##
    ## find last row in "incoming"
    ##
    lenInc = 0

    for i in incoming:
        if i[3] != "":
            lenInc += 1
        else:
            break

    ##
    ## write new entries to "incoming"
    ##
    startRow = lenInc + 1
    startCol = 4
    lastRow = len(newEntries) + startRow - 1
    lastCol = len(newEntries[0]) + startCol - 1
    cellList = incomingWS.range(startRow,startCol,lastRow,lastCol)


    for r, entry in enumerate(newEntries):
        for c, value in enumerate(entry):
            cellList[r*(lastCol-3)+c].value = value
    incomingWS.update_cells(cellList, value_input_option="USER_ENTERED")
    

    ##
    ## entries "synced"
    ##
    lastRow = len(entries)
    cellList = entriesWS.range(2,statusCol+1,lastRow,statusCol+1)
    for cell in cellList:
        if cell.value == "":
            cell.value = "synced"
    entriesWS.update_cells(cellList, value_input_option="USER_ENTERED")

    itemize()


def itemize():

    ##
    ## Separates entries to one town per line
    ##

    def concat(i,a,b):
        buff1 = i[a:b]
        buff2 = i[0:6]
        buff = buff1 + buff2
        newItems.append(buff)

    for row in newEntries:
        cn = 6    ## Col of first town name
        while row[cn] != "":
            concat(row, cn, cn+3)
            cn += 4

    for item in newItems:
        item[0] = item[0].title()
        item[0] = item[0].strip()
        item.insert(1,"")
        item[2] = int(item[2])
        item[3] = int(item[3])
        if len(item[7]) == 11 and item[7][0] == "1":
            item[7] = item[7][1:]

    townScope()


def townScope():
    ##
    ## Matches town to county
    ##

    ## Load Counties DB
    sheet = client.open_by_key("1MFAIox4wN81FaAubWdKsq3rj_8uMFu66zizYqusMKRo")
    countydbWS = sheet.worksheet("Sheet1")
    global countydb
    countydb = countydbWS.get_all_values()

    ## Load Towns DB
    sheet = client.open_by_key("1_4Guz-uWbkaPCcnyO2nZprXwDfREI4YSiL_Z-UiWeo0")
    towndbWS = sheet.worksheet("Sheet1")
    global towndb
    towndb = towndbWS.get_all_values()

    ## Load Villages DB
    sheet = client.open_by_key("1nq7f-RMXucR2q0eKlEm2ttR6ra4YEFUZwPP-x6bueeo")
    villagedbWS = sheet.worksheet("Sheet2")
    villagedb = villagedbWS.get_all_values()

    ## match town to county
    for item in newItems:
        for row in towndb[1:]:
            if row[0].lower() == item[0].lower():
                item[1] = row[2]
                break


    ## if town not found, check this list (villages/neighborhoods/common misspellings)
    for item in newItems:
        if item[1] == "":
            for row in villagedb[1:]:
                if row[0].lower() == item[0].lower():
                    item[0] = row[1]
                    item[1] = row[2]
                    break


    for item in newItems:
        if item[1] == "":
            item[1] = "Unknown"


    ## import "itemized" sheet
    sheet = client.open_by_key("1azm09bW1dR7WPH0uZ_RMk-OR8zQ8H1xeQPfivdY_gLs")
    itemizedWS = sheet.worksheet("Sheet1")
    global items
    items = itemizedWS.get_all_values()

    items[0][1] = updateTime


    ## append new entries to existing "items"
    for item in newItems:
        items.append(item)


    ## write out to "itemized"
    lastRow = len(items)
    lastCol = len(items[0])
    cellList = itemizedWS.range(1,1,lastRow,lastCol)

    for r, item in enumerate(items):
        for c, value in enumerate(item):
            cellList[r*lastCol+c].value = value

    itemizedWS.update_cells(cellList, value_input_option="USER_ENTERED")


    ## not sure why I have this here, seems redundant
    with open("itemized.csv","w", encoding = "utf-8") as outfile:
        writer = csv.writer(outfile)
        for item in items:
            writer.writerow(item)


    tots()


def tots():
    ##
    ## Sorting by week/yesterday/today
    ##

    goalTotal = 0
    for county in countydb[1:]:
        counties.append([county[0],
                         0,0,0,0,0,0,0,0,0,0,0,0,0,0,
                         0,0,0,0,0,0,0,0,0,0,0,0,0,
                         0,0,0,0,0,0,0,0,0,0])
        goalTotal += int(county[1])

    for town in towndb[1:]:
        towns.append([town[0],
                         0,0,0,0,0,0,0,0,0,0,0,0,0,0,
                         0,0,0,0,0,0,0,0,0,0,0,0,0,
                         0,0,0,0,0,0,0,0,0,0])

    ##
    ## County Totals
    ##
    for item in items[2:]:
        item[2] = int(item[2])
        item[3] = int(item[3])
        for county in counties:
            if item[1] == county[0]:

                county[1] += item[3]

                date = datetime.datetime.strptime(item[8], '%m/%d/%Y')
                date = date.date()

                if date == dateToday.date():
                    county[5] += item[3]

                if date == dateYesterday.date():
                    county[8] += item[3]

                for n, week in enumerate(weeks[:-1]):
                    if date >= weeks[n].date() and date < weeks[n+1].date():
                        county[n*3+11] += item[3]
                break


    ##
    ## Daily Totals
    ##
    totalTotal = 0
    dailyGoal = round((goalTotal/daysTotal),0)
    for n in range(daysTotal):
        today = startDate + datetime.timedelta(days = n)
        todayDate = today.strftime("%Y-%m-%d")
        todayTotal = 0
        for item in items[2:]:
            date = datetime.datetime.strptime(item[8], '%m/%d/%Y')
            if date.date() == today.date():
                todayTotal += item[3]
                totalTotal += item[3]
        if n < daysElapsed:
            dailyTotals.append(["Day " + str(n+1) + " (" + todayDate + ")",
                            todayTotal, dailyGoal, totalTotal])
        else:
            dailyTotals.append(["Day " + str(n+1) + " (" + todayDate + ")",
                            todayTotal, dailyGoal, ""])


    ##
    ## Town Totals
    ##
    for item in items[2:]:
        for town in towns:
            if item[0] == town[0]:

                town[1] += item[2]  ## Adding Sheets
                town[2] += item[3]  ## Adding Sigs

                date = datetime.datetime.strptime(item[8], '%m/%d/%Y')
                date = date.date()

                if date == dateToday.date():
                    town[5] += item[2]
                    town[6] += item[3]

                if date == dateYesterday.date():
                    town[8] += item[2]
                    town[9] += item[3]

                for n, week in enumerate(weeks[:-1]):
                    if date > weeks[n].date() and date <= weeks[n+1].date():
                        town[n*3+11] += item[2]
                        town[n*3+12] += item[3]
                break

    ## Clearing out "0" from cell
    for town in towns:
        town[3] = ""
        for n in range(weeksTotal + 3):
            town[n*3+4] = ""    ## Same here

    summarize()


def summarize():

    ##
    ## Percent to goal by date
    ##
    for county in counties:  ## Getting daily/weekly goals by county
        for row in countydb:  ## From info_county file
            if county[0] == row[0]:
                goal = int(row[1])  ## Sigs goal for each county
                goalDaily = goal/daysTotal
                goalWeekly = goal/weeksTotal

                county[2] = round(goal*(daysElapsed/daysTotal),0)  ## Col C in Sig Tracker (calculating cumulative goal)
                county[3] = round(county[2]-county[1],0)
                county[6] = round(goalDaily-county[5],0)
                county[9] = round(goalDaily-county[8],0)
                if goal != 0:
                    county[4] = str(round(((county[2]-county[3])/county[2])*100,1))+"%"  ## Filling in daily percent to goal colored columns
                    county[7] = str(round(((goalDaily-county[6])/goalDaily*100),1))+"%"
                    county[10] = str(round(((goalDaily-county[9])/goalDaily*100),1))+"%"
                else:
                    county[4] = "N/A"
                    county[7] = "N/A"
                    county[10] = "N/A"

                for n in range(9):  ## 9 is number of weeks of SG
                    county[n*3+12] = round(goalWeekly - county[n*3+11],0)  ## Filling in weekly percent to goal colored columns
                    if goal != 0:
                        county[n*3+13] = str(round(((goalWeekly-county[n*3+12])/goalWeekly*100),1))+"%"
                    else:
                        county[n*3+13] = "N/A"

    ##
    ## Deviation from goal by county
    ##
    for county in counties:
        countyName = county[0]
        avgActual = county[1]/daysElapsed
        for row in countydb:
            if row[0] == county[0]:
                goal = int(row[1])
                avgGoalDay = goal/daysTotal
                avgGoalWeek = goal/weeksTotal
                avgNeedDay = (goal-county[1])/daysLeft
                avgNeedWeek = (goal-county[1])/weeksLeft
        newGoals.append([countyName,
                         round(avgActual,0),"",
                         round(avgGoalDay,0),"",
                         round(avgGoalWeek,0),"",
                         round(avgNeedDay,0),"",
                         round(avgNeedWeek,0)])

    writeOut()


def writeOut():

    cellList1 = trackerWS.range("A3:AL17")
    for n, county in enumerate(counties):
        for i, item in enumerate(county):
            cellList1[n*len(county)+i].value = item

    cellList2 = trackerWS.range("A21:J35")
    for n, ng in enumerate(newGoals):
        for i, item in enumerate(ng):
            cellList2[n*len(ng)+i].value = item

    cellList3 = trackerWS.range("A40:AL390")
    for n, town in enumerate(towns):
        for i, item in enumerate(town):
            cellList3[n*len(town)+i].value = item

    cellList4 = trackerWS.range("A400:D471")
    for n, total in enumerate(dailyTotals):
        for i, item in enumerate(total):
            cellList4[n*len(total)+i].value = item

    cellList = cellList1 + cellList2 + cellList3 + cellList4
    trackerWS.update_cells(cellList, value_input_option="USER_ENTERED")

    updateTime = dateToday.strftime("%Y-%m-%d %I:%M%p")
    trackerWS.update_acell("A2", updateTime)




##
## Google Sheets API
##
scope = ["https://spreadsheets.google.com/feeds",
         'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)


##
## Define timeframe
##

dateToday = datetime.datetime.today() - datetime.timedelta(hours = 4)
dateYesterday = datetime.datetime.today() - datetime.timedelta(days = 1, hours = 4)


weeks = [datetime.datetime(2019,9,10),
         datetime.datetime(2019,9,18),
         datetime.datetime(2019,9,25),
         datetime.datetime(2019,10,2),
         datetime.datetime(2019,10,9),
         datetime.datetime(2019,10,16),
         datetime.datetime(2019,10,23),
         datetime.datetime(2019,10,30),
         datetime.datetime(2019,11,6),
         datetime.datetime(2019,11,13)]


startDate = weeks[0]
endDate = weeks[-1]

weeksTotal = len(weeks) - 1

daysTotal = endDate - startDate
daysTotal = daysTotal.days

daysLeft = endDate - dateToday
daysLeft = daysLeft.days

weeksLeft = daysLeft/7

daysElapsed = daysTotal-daysLeft

updateTime = dateToday.strftime("%Y-%m-%d %I:%M%p")


##
## Global lists
##
newEntries = []
newItems = []
counties = []
towns = []
dailyTotals = []
newGoals = []


##
## Start here
##
scraper()
