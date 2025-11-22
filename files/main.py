import os
import json
from PIL import Image
import PySimpleGUI as sg
from auxFunctions import (
    searchMedia,
    createFolders,
    setWindowsTime,
    set_EXIF,
)

def mainProcess(browserPath, window, editedW):
    piexifCodecs = [k.casefold() for k in ['TIF', 'TIFF', 'JPEG', 'JPG']]

    mediaMoved = set()  # set with names of all the media already matched
    path = browserPath  # source path
    fixedMediaPath = os.path.join(path, "MatchedMedia")  # destination path
    nonEditedMediaPath = os.path.join(path, "EditedRaw")
    errorCounter = 0
    successCounter = 0
    editedWord = editedW or "editado"
    print(editedWord)

    try:
        obj = list(os.scandir(path))  #Convert iterator into a list to sort it
        obj.sort(key=lambda s: len(s.name)) #Sort by length to avoid name(1).jpg be processed before name.jpg
        createFolders(fixedMediaPath, nonEditedMediaPath)
    except Exception as e:
        window['-PROGRESS_LABEL-'].update("Choose a valid directory", visible=True, text_color='red')
        return

    for idx, entry in enumerate(obj):
        if entry.is_file() and entry.name.endswith(".json"):  # Check if file is a JSON
            with open(entry, encoding="utf8") as f:  # Load JSON into a var
                data = json.load(f)

            progress = round(idx/len(obj)*100, 2)
            window['-PROGRESS_LABEL-'].update(str(progress) + "%", visible=True)
            window['-PROGRESS_BAR-'].update(progress, visible=True)

            #SEARCH MEDIA ASSOCIATED TO JSON

            # Validate JSON structure
            if 'title' not in data:
                print(f"Missing 'title' in JSON: {entry.name}")
                errorCounter += 1
                continue

            titleOriginal = data['title']  # Store metadata into vars

            try:
                title = searchMedia(path, titleOriginal, mediaMoved, nonEditedMediaPath, editedWord)

            except Exception as e:
                print("Error on searchMedia() with file " + titleOriginal)
                errorCounter += 1
                continue

            if title is None:
                print(titleOriginal + " not found")
                errorCounter += 1
                continue

            filepath = os.path.join(path, title)

            # METADATA EDITION
            if 'photoTakenTime' not in data or 'timestamp' not in data.get('photoTakenTime', {}):
                print(f"Missing timestamp in JSON: {entry.name}")
                errorCounter += 1
                continue

            timeStamp = int(data['photoTakenTime']['timestamp'])  # Get creation time
            print(filepath)

            if title.rsplit('.', 1)[1].casefold() in piexifCodecs:  # If EXIF is supported
                try:
                    with Image.open(filepath) as im:
                        rgb_im = im.convert('RGB')
                        new_filepath = filepath.rsplit('.', 1)[0] + ".jpg"
                        os.replace(filepath, new_filepath)
                        filepath = new_filepath
                        rgb_im.save(filepath)
                except ValueError as e:
                    print("Error converting to JPG in " + title)
                    errorCounter += 1
                    continue

                try:
                    set_EXIF(filepath, data['geoData']['latitude'], data['geoData']['longitude'], data['geoData']['altitude'], timeStamp)

                except Exception as e:  # Error handler
                    print("Inexistent EXIF data for " + filepath)
                    print(str(e))
                    errorCounter += 1
                    continue

            setWindowsTime(filepath, timeStamp) #Windows creation and modification time

            #MOVE FILE AND DELETE JSON

            os.replace(filepath, os.path.join(fixedMediaPath, title))
            os.remove(os.path.join(path, entry.name))
            mediaMoved.add(title)
            successCounter += 1

    successMessage = " successes"
    errorMessage = " errors"

    #UPDATE INTERFACE
    if successCounter == 1:
        successMessage = " success"

    if errorCounter == 1:
        errorMessage = " error"

    window['-PROGRESS_BAR-'].update(100, visible=True)
    window['-PROGRESS_LABEL-'].update("Matching process finished with " + str(successCounter) + successMessage + " and " + str(errorCounter) + errorMessage + ".", visible=True, text_color='#c0ffb3')
