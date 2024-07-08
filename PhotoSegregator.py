"""
Application sorts all photo files from selected folder to the new folder.
Sorting process is based on meta-datas (datatime, gps location data) included in photo files.
Script use Google Geocodidng API, Geolocation API and Directions API
After sorting process, summary will be showed in console.

Script uses private Google API key - in necessary please contact with me or use your own.
"""
import os
import time
import tkinter
from tkinter import filedialog
from exif import Image
import googlemaps
import shutil
import re


class Photosegregator:
    def __init__(self, photoDir, photoDest, photo4verification):
        self.file: str = ''
        self.photoDir: str = photoDir
        self.photoDest: str = photoDest
        self.photo4verification: str = photo4verification
        self.photopath = ""
        self.filelist = os.listdir(self.photoDir)
        self.reverse_geocode_result: dict = {}
        self.dataFolder: str = ""
        self.nameFolder: str = ''

    # read all photo files as path
    def photoPaths(self):
        path = self.photoDir
        for photo in self.filelist:
            self.photopath = os.path.join(path, photo)
            yield self.photopath

    def decimal_coords(coords, ref):
        decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
        if ref == "S" or ref == 'W':
            decimal_degrees = -decimal_degrees
        return decimal_degrees

    def metadataReader(self):
        for file in self.photoPaths():
            self.file = file
            print("file: ", self.file)
            with open(file, 'rb') as src:
                img = Image(src)
            if img.has_exif:
                try:
                    img.gps_longitude
                    coords = (Photosegregator.decimal_coords(img.gps_latitude,
                                                             img.gps_latitude_ref),
                              Photosegregator.decimal_coords(img.gps_longitude,
                                                             img.gps_longitude_ref))

                    data2 = {"imageTakenTime": img.datetime_original, "geolocation_lat": coords[0],
                             "geolocation_lng": coords[1]}
                    photo = data2["geolocation_lat"], data2["geolocation_lng"]
                    imageTakenData = data2["imageTakenTime"]
                    imageTakenData = imageTakenData.replace(":", "-").split(" ")
                    self.dataFolder = imageTakenData[0]
                    gmaps = googlemaps.Client(key='AIzaSyDpwFuUkZ8Zf0syoG7oiYVT8TTqIgZxU3o')
                    # About 'KEY' please contact with me or use your own.
                    reverseGeocodeResult = gmaps.reverse_geocode(photo)
                    try:
                        place = reverseGeocodeResult[0]
                        city2 = str(place['formatted_address'])

                        if city2:
                            try:
                                city = city2.split(",")[-2]
                                city = re.sub(r"[^\D]", '', city)
                                city = re.sub("\s\-", '', city).strip()
                            except IndexError:
                                city = city2.split(",")[-2].split(" ")[-1]
                                print("city: ", city)

                        self.nameFolder = self.dataFolder + ' -' + city
                        print("Name of directory", self.nameFolder)
                        self.copier()

                    except IndexError:
                        print("Issue with medatada in photo file")
                        shutil.copy(self.file, self.photo4verification)

                except AttributeError:
                    print("Issue with medatada in photo file {}".format(self.file.split(r"/")[-1]))
                    shutil.copy(self.file, self.photo4verification)

    def copier(self):
        newFolder = os.path.join(self.photoDest, self.nameFolder)
        if os.path.exists(newFolder):
            shutil.copy(self.file, newFolder)
            print("Photo {} was copied to {}".format(self.file, newFolder))
        else:
            os.mkdir(newFolder)
            shutil.copy(self.file, newFolder)
            print("Photo {} was copied to {}".format(self.file, newFolder))


class Statistic(Photosegregator):
    def __init__(self, photoDir, photoDest, photo4verification):
        super().__init__(photoDir, photoDest, photo4verification)
        self.metadataReader()
        self.finalStatistic()

    def baseStatistic(self):
        lst = os.listdir(self.photoDest)  # your directory path
        numberFiles = lst

        for directory in numberFiles:
            fullPath = os.path.join(self.photoDest, directory)
            yield fullPath

    def finalStatistic(self):
        counter = 0
        for path in self.baseStatistic():
            allFiles = next(os.walk(path))[2]  # directory is your directory path as string
            counter = counter + len(allFiles)

        errorPhotosCouter = len(self.filelist) - counter

        print("=" * 50)
        print("Count of files to copy: {} piece(s)".format(len(self.filelist)))
        print("Count of copied files: {} piece(s)".format(counter))
        print("Count of files without geo metadata inside: {} piece(s)".format(errorPhotosCouter))
        print("=" * 50)


print("Select your directory with photos:")
tkinter.Tk().withdraw()  # prevents an empty tkinter window from appearing
time.sleep(1)
photoDir = filedialog.askdirectory()

print("Select directory for photos after segregation")
time.sleep(2)
tkinter.Tk().withdraw()  # prevents an empty tkinter window from appearing
photoDest = filedialog.askdirectory()

print("Select directory for photos without geo metadatas for manual segregation")
time.sleep(2)
tkinter.Tk().withdraw()  # prevents an empty tkinter window from appearing
photo4verification = filedialog.askdirectory()

start = Statistic(photoDir, photoDest, photo4verification)
