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
                        "loc": details.group(2).strip(),
                        "prof": details.group(3).strip()
                    },
                    "groups": {}
                }

                result.append(dayData)
            else:

                dctG1 = {}
                dctG2 = {}

                if re.search('G1', ele, re.S):

                    g1Regex = "G1.+?\((.+?)\)(.+?),([^G2]+)?"

                    details = re.search(g1Regex, ele, flags=re.S | re.M)

                    dctG1 = {
                        "G1": {
                            "Time": time[i - 1],
                            "Subject": details.group(2).strip(),
                            "loc": details.group(1).strip(),
                            "prof": details.group(3).strip() if details.group(3) else "no name"
                        }
                    }

                if re.search('G2', ele, re.S):

                    g2Regex = "G2.*\((.+)\)(.+),(.*)"

                    details = re.search(g2Regex, ele, flags=re.S | re.M)

                    dctG2 = {
                        "G2": {
                            "Time": time[i - 1],
                            "Subject": details.group(2).strip(),
                            "loc": details.group(1).strip(),
                            "prof": details.group(3).strip() if details.group(3) else "no name"
                        }
                    }

                dayData = {
                    "cours": {},
                    "groups": {}
                }

                if dctG1:
                    dayData["groups"].update(dctG1)

                if dctG2:
                    dayData["groups"].update(dctG2)

                result.append(dayData)

    return result



def pdftoDataFrame(pdfFile, page):

    # convert PDF into CSV
    tabula.convert_into(pdfFile, "scraped.csv", output_format="csv", pages=page)
    
    df = pd.read_csv("scraped.csv", encoding="ISO-8859-1")

    return df


def csvToJson(df, outputJson):

    outDict = {
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
    # choose input and output files pdfToCsv("MIV.pdf", "1")
    df = pdftoDataFrame("MIV.pdf", "1")
    # pass the dataframe and the output file csvTojson(df, "data.json")
    csvToJson(df, "data.json")

    print("Done")


if __name__ == "__main__":
    run()