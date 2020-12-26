#!/usr/bin/env python
# coding: utf-8

# In[6]:


import queue
import threading
import time
import PySimpleGUI as sg
import os.path
from pdf2image import convert_from_path

# First the window layout in 2 columns

left_column = [
    [
        sg.Text("Select Folder"),
        sg.In(size=(25, 1), enable_events=True, readonly=True, key="-FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Text("Select Image Quality"),
        sg.Combo([250,300,400,500], default_value = 250, enable_events=True, size=(20, 20), key='-QUALITY-')
    ],
    [
        sg.Text("Select Image Type"),
        sg.Combo(["JPG","PNG"], default_value = "JPG", enable_events=True, size=(20, 20), key='-TYPE-')
    ],
    [
        sg.Listbox(values=[], enable_events=True, size=(40, 20), select_mode="multiple" , key="-FILE LIST-")
    ],
    [
        sg.Text("Selected DPI - 250, Type - JPG", size=(40,1),key='-GUIDE-')
    ],
    [
        sg.Text("Convert Selected PDF or Folder to Image"),
        sg.Button("Convert")
    ]
]

# Second columns
# For now will only show the name of the file that was chosen
right_column = [
    [sg.Text("Selected PDF Files:")],
    [sg.Text(size=(40, 1), key="-TOUT-")],
    [sg.Output(size=(50, 12))],
]


def pdf_to_image(imageFolder,imageList,imageQuality,imageType,imageTypeExt,gui_queue):

    for i in range(len(imageList)):
        pdffile = os.path.join(imageFolder, imageList[i])
        pages = convert_from_path(str(pdffile), imageQuality)
        for page in pages:
            if range(len(pages)) == range(0,1):
                #outputfile = listOfFiles[i].split(".")[0]+"."+listOfFiles[i].split(".")[1]+".jpg"
                outputfile = os.path.join(imageFolder, imageList[i])+imageTypeExt
            else:
                imageListName = imageList[i].rsplit('.', 1)[0]
                outputfile = os.path.join(imageFolder, imageListName)+" Page_"+str(pages.index(page)+1)+imageTypeExt
            page.save(outputfile, imageType)
        gui_queue.put(str(i+1) + " / " + str(len(imageList)) + " PDF Files Converted")  # put a message into queue for GUI


######   ##     ## ####
##    ##  ##     ##  ##
##        ##     ##  ##
##   #### ##     ##  ##
##    ##  ##     ##  ##
##    ##  ##     ##  ##
######    #######  ####

def the_gui():

    gui_queue = queue.Queue()  # queue used to communicate between the gui and the threads

    # ----- Full layout -----
    layout = [
        [
            sg.Column(left_column),
            sg.VSeperator(),
            sg.Column(right_column),
        ]
    ]

    window = sg.Window("PDF to Image Convertor").Layout(layout)

    # --------------------- EVENT LOOP ---------------------
    while True:
        event, values = window.Read(timeout=100)       # wait for up to 100 ms for a GUI event
        if event is None or event == 'Exit':
            break
            
        if event == "-FOLDER-":
            folder = values["-FOLDER-"]
            try:
                # Get list of files in folder
                file_list = os.listdir(folder)
            except:
                file_list = []

            fnames = [
                f
                for f in file_list
                if os.path.isfile(os.path.join(folder, f))
                and f.lower().endswith((".pdf"))
            ]
            window["-FILE LIST-"].update(fnames)

        elif event == "-FILE LIST-":  # A file was chosen from the listbox
            try:
                filename = values["-FILE LIST-"]
                window["-TOUT-"].update(filename)
            except:
                pass

        elif event == '-QUALITY-':
            try:
                window['-GUIDE-'].update("Selected DPI - "+str(values['-QUALITY-'])+", Type - "+values['-TYPE-'])
            except:
                pass

        elif event == '-TYPE-':
            try:
                window['-GUIDE-'].update("Selected DPI - "+str(values['-QUALITY-'])+", Type - "+values['-TYPE-'])
            except:
                pass
        
        elif event == 'Convert':
                       
            imageFolder = values["-FOLDER-"]
            imageQuality = values['-QUALITY-']
            
            if not imageFolder and imageQuality:
                gui_queue.put("Please click folder browser and Select the folder")  # put a message into queue for GUI
                continue
            
            if values['-TYPE-'] == "JPG":
                imageType = "JPEG"
                imageTypeExt = ".jpg"

            elif values['-TYPE-'] == "PNG":
                imageType = "PNG"
                imageTypeExt = ".png"
            
            if len(values['-FILE LIST-']):
                try:
                    imageList = values["-FILE LIST-"]
                    threading.Thread(target=pdf_to_image, args=(imageFolder,imageList,imageQuality,imageType,imageTypeExt,gui_queue,), daemon=True).start()
                except:
                    pass
            
            elif len(fnames):
                try:
                    imageList = fnames
                    threading.Thread(target=pdf_to_image, args=(imageFolder,imageList,imageQuality,imageType,imageTypeExt,gui_queue,), daemon=True).start()
                    #sg.Popup('All PDF had being converted', fnames)
                except:
                    pass

        # --------------- Check for incoming messages from threads  ---------------
        try:
            message = gui_queue.get_nowait()
        except queue.Empty:             # get_nowait() will get exception when Queue is empty
            message = None              # break from the loop if no more messages are queued up

        # if message received from queue, display the message in the Window
        if message:
            print('Application Update: ', message)
                
    window.close()


##     ##    ###    #### ##    ##
###   ###   ## ##    ##  ###   ##
#### ####  ##   ##   ##  ####  ##
## ### ## ##     ##  ##  ## ## ##
##     ## #########  ##  ##  ####
##     ## ##     ##  ##  ##   ###
##     ## ##     ## #### ##    ##

if __name__ == '__main__':
    the_gui()
    print('Exiting Program')


# In[ ]:




