"""
Script gets json file from web.
User can select which data will be filtered from basic file by entered keys.
Base on geo information, script checks from witch country is person uses Google Api
Finally all information is exported to new json and excell file.

Script uses private Google API key - in necessary please contact with me or use your own.

"""
import urllib.request, json
import googlemaps
import pandas as pd


class ApiSegregationData:
    def __init__(self, apiPath):
        self.apiPath: str = apiPath
        self.wholeListDict: list = []
        self.parserData()
        self.exportJson()
        self.exportExcel()

    def getData(self):
        with urllib.request.urlopen(self.apiPath) as url:
            data = json.load(url)
            print(data)
        return data

    def parserData(self):
        data = self.getData()
        self.wholeListDict = []

        #hardcode input data keys for loops
        personalKeysList = ["id", "name", "email", "phone"]
        addressKeysList = ["street", "suite", "city", "zipcode", "geo"]
        companyKeysList = ["name", "catchPhrase"]

        #flexy way to input keys data
        # personalKeysList = input("Please provide personal data keys: ").split(" ")# ex (id name email phone)
        # addressKeysList = input("Please provide address data keys: ").split(" ")# ex (street suite city zipcode geo)
        # companyKeysList = input("Please provide company data keys: ").split(" ")# ex (name catchPhrase)

        for information in data:
            print("data: ", data)
            print("information", information)
            # create dict with personal data
            personalDataList = []
            for personalData in personalKeysList:
                personalDataList.append(information[personalData])
            personalDataDict = dict(zip(personalKeysList, personalDataList))
            # create dict with address data
            adressDatas = information["address"]
            addressDataList = []
            addressDataDict = {}
            for addressData in addressKeysList:
                # create new data based on geo information
                if addressData == "geo":
                    geodata = (adressDatas[addressData]["lat"], adressDatas[addressData]["lng"])
                    gmaps = googlemaps.Client(key='KEY')
                    # About 'KEY' please contact with me or use your own.
                    reverseGeocodeResult = gmaps.reverse_geocode(geodata)
                    try:
                        country = reverseGeocodeResult[1]['formatted_address']
                    except IndexError:
                        country = "Somewhere on Earth"
                    addressDataDict = dict(zip(addressKeysList, addressDataList))
                    addressDataDict["country"] = country
                else:
                    addressDataList.append(adressDatas[addressData])
                    addressDataDict = dict(zip(addressKeysList, addressDataList))

            personalDataDict["address"] = addressDataDict

            # create dict and append list of dicts into one list
            companyDatas = information["company"]
            companyDataList = []
            for companyData in companyKeysList:
                companyDataList.append(companyDatas[companyData])
            companyDataDict = dict(zip(companyKeysList, companyDataList))
            personalDataDict["company"] = companyDataDict
            self.wholeListDict.append(personalDataDict)

        print(self.wholeListDict)
        return self.wholeListDict

    def exportJson(self):
        with open("sample.json", "w") as outfile:
            json.dump(self.wholeListDict, outfile)

        return None

    def exportExcel(self):
        dictData = pd.DataFrame.from_dict(self.wholeListDict)
        print(dictData)
        dictData.to_excel("data.xlsx")

        return None


start = ApiSegregationData('https://jsonplaceholder.typicode.com/users')
