import tabula
import pandas as pd
import json
import re


def getDayData(df, index):

    data = (df.iloc[index, :]).values
    time = df.columns.values[1:]

    result = []

    for i in range(1, len(data)):

        if not pd.isnull(data[i]):  # check if data is null before adding

            ele = data[i].replace("\r", " ")   # remove new lines from data


            if re.search('cours', ele, re.S):

                coursRegex = "(.+)cours ?\((.+)\)(.*)"

                details = re.search(coursRegex, ele, flags=re.S | re.M)

                dayData = {
                    "cours": {
                        "Time": time[i - 1],
                        "Subject": details.group(1).strip(),
                        "loc": details.group(2).strip().replace(".",""),
                        "prof": details.group(3).strip() if details.group(3) else "no name"
                    },
                    "groups": {}
                }

                result.append(dayData)
            else:

                dayData = groupsExtraction(ele, time[i - 1])
                result.append(dayData)

    return result


# the default maximum number of groups can be changed 
def groupsExtraction(text, time, number = 4):

    if(number < 2):
        number = 2

    extractedList = []
    
    for i in range(number):

        if re.search('G'+ str(i+1)+":", text, re.S):

            regex = "G"+str(i+1)+".+?\((.+?)\)(.+?),([^:]+)?"

            details = re.search(regex, text, flags=re.S | re.M)

            
            if details.group(3) and details.group(3).strip() != "":
                prof = details.group(3).strip()
                prof = prof.split(" ")[0]
            else:
                prof = "no name"

            dct = {
                "G"+ str(i+1): {
                    "Time": time,
                    "Subject": details.group(2).strip(),
                    "loc": details.group(1).strip().replace(".",""),
                    "prof": prof
                }
            }

            extractedList.append(dct)

    dayData = {
        "cours": {},
        "groups": {}
    }

    
    for group in extractedList:
        if group:
            dayData["groups"].update(group)
    
    
    return dayData


def pdftoDataFrame(pdfFile, page):

    # convert PDF into CSV
    tabula.convert_into(pdfFile, "scraped.csv", output_format="csv", pages=page)
    
    df = pd.read_csv("scraped.csv", encoding="ISO-8859-1")

    return df


def dataFrameToJson(df, outputJson):

    outDict = {
        "specialty": "MIV", # <----  specify specialty here
        "year": "2",    # <----  specify year here
        "Semestre": "1",    # <----  specify semestre
        "days": {}
    }


    days = (df.iloc[:, 0]).values


    for index, day in enumerate(days):
        outDict["days"][day] = getDayData(df, index)

    json_object = json.dumps(outDict, ensure_ascii=False)

    # Writing to sample.json
    with open(outputJson, "w", encoding="UTF-8") as outfile:
        outfile.write(json_object)



def run():
    # choose input file and the desired schedule page pdfToCsv("MIV.pdf", "1")
    df = pdftoDataFrame("data/SSI.pdf", "1")
    # pass the dataframe and the output file csvTojson(df, "data.json")
    dataFrameToJson(df, "Extracted/M1_SSI.json")

    print("Done")


if __name__ == "__main__":
    run()