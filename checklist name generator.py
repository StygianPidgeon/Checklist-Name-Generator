#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Filename: checklist name generator.py
Author: Dawn Holley
Date: 2026-09-16
Version: 1.0.4
Description: This script offers a GUI in order to name scanned mandatory checklists for Mercedes-Benz
'''

'''
License: GPL License
Contact: dawn.holley@infosys.com
Dependencies: PIL, tkinter, pdf2image
'''

from PIL import Image, ImageTk
from pdf2image import convert_from_path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pypdf
import os, sys, re, shutil, subprocess


CURRENT_VERSION = '1.0.4'

#create a root window so popup windows can be displayed
root = tk.Tk()
root.withdraw()

#set poppler path locally
if getattr(sys, 'frozen', False) :
    #running as exe
    base_path = os.path.dirname(sys.executable)
else :
    #running in vscode for testing
    base_path = os.path.dirname(os.path.abspath(__file__))

poppler_path = os.path.join(
    base_path,
    'Poppler',
    'Library',
    'bin'
)

print(f"Poppler Path: {poppler_path}")
i = 0
writer = pypdf.PdfWriter()
selected_path = filedialog.askdirectory()
output_path = selected_path + r'/output'

#if output folder already exists, ask for whether it should be removed before continuing
if os.path.exists(output_path):
    response = messagebox.askyesnocancel(
        'Output Folder Exists',
        'The output folder already exists\n\n'
        'Would you like to remove it and all its contents before continuing?\n\n' \
        'Note: If you continue without removing it, there may be issues running the script.'
    )
    if response:
        try : 
            shutil.rmtree(output_path)
        except Exception as e :
            messagebox.showerror("Error", f"Could not remove output path: {e}")
    elif not response:
        pass
    else:
        raise SystemExit
    os.makedirs(output_path)
else:
    os.makedirs(output_path)
    
#splits each pdf in the selected directory into individual pdf files per page

for file in os.listdir(selected_path):
    try:
        if file.endswith('.pdf') and not file == 'output':
            file_name = file.split(r'.')
            file_path = selected_path + '/' + file
            data = open(file_path, 'rb')
            reader = pypdf.PdfReader(data)
            for x, page in enumerate(reader.pages):
                writer.add_page(page)
                writer.write(f'{output_path}/{file_name[0]}_{x}.pdf')
                writer.remove_page(0)
    except Exception as e:
        print (repr(e))
    
total_files : int = len(os.listdir(output_path))
processed_files : int = 0
failure_count : int = 0
for file in os.listdir(output_path):
    file_name = file.split(r'.')
    file_path = output_path + '/' + file
    print(file_path)
    doc = convert_from_path(file_path, poppler_path=poppler_path)

    dialog = tk.Toplevel()
    dialog.title("File Naming Interface")
    dialog.resizable(False, False)
    dialog.grab_set()

    result = {'filename': None}

    #method called when pressing 'open existing file' button
    def open_existing_file():
        try:
            os.startfile(file_path)
        except Exception as e:
            messagebox.showerror(
                'Error', f'Could not open file:\n\n{e}'
            )
    
    #method called when pressing 'confirm' button
    def confirm():
        global failure_count, processed_files, total_files
        print(request_nr.get())
        print(ci_nr.get())
        if(not no_ci_found.get()) :
            if not (re.match(pattern = r'^\d{8}$', string = request_nr.get()) 
                    and re.match(pattern = r'^\d{8}$', string = ci_nr.get())
                    and re.match(pattern = r'^(Deployment|Return)$', string = checklist_type.get())):
                messagebox.showwarning(
                    'Incorrect information',
                    'One or more pieces of information entered does not conform to the naming convention.\n' \
                    'Please ensure that Request number and CI number are 8 digits long each, and that a Checklist Type has been selected.'
                )
                return
            try:
                input = f'{checklist_type.get()}_{request_nr.get()}_{ci_nr.get()}.pdf'
                os.rename(f'{file_path}', f'{output_path}/{input}')
            except Exception as e:
                messagebox.showerror(
                    'Error', f'Could not save file:\n\n{e}'
                )
                return
            try:
                os.remove(f'{file_path}_image.bmp')
            except Exception as e:
                messagebox.showerror(
                    'Error', f'Could not remove image file:\n\n{e}'
                )
                return
        else : 
            try:
                input = f'Deployment_auftragsnr_unknown_{failure_count}.pdf'
                failure_count += 1
                os.rename(f'{file_path}', f'{output_path}/{input}')
            except Exception as e:
                messagebox.showerror(
                    'Error', f'Could not save file:\n\n{e}'
                )
                return
            try:
                os.remove(f'{file_path}_image.bmp')
            except Exception as e:
                messagebox.showerror(
                    'Error', f'Could not remove image file:\n\n{e}'
                )
                return
        processed_files += 1
        dialog.destroy()

    #method called when pressing 'cancel' button
    def cancel():
        print("Exiting dialog")
        os._exit(0)

    #cuts up the page into an image
    for page_number, page_data in enumerate(doc):
        full_scan = doc[page_number]
        full_scan = full_scan.convert('L')
        image_coords = (0, 0, full_scan.width, 1000)

        request = full_scan.crop(image_coords)
        request.save(f'{file_path}_image.bmp')

    MAX_IMAGE_HEIGHT = 500
    img = Image.open(f'{file_path}_image.bmp')
    w, h = img.size
    aspect_ratio = w / h
    new_height = min(h, MAX_IMAGE_HEIGHT)
    new_width = int(new_height * aspect_ratio)
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    picture = ImageTk.PhotoImage(img)

    progress_label = tk.Label(
        dialog,
        text = f'Processing file {processed_files + 1} of {total_files}.'
    )
    progress_label.pack(padx = 15, pady = (15, 10))

    progress_bar = ttk.Progressbar(
        dialog,
        length = 300,
        mode = 'determinate',
        maximum = total_files
    )
    progress_bar['value'] = processed_files
    progress_bar.pack(padx=15, pady=(5, 15))


    tk.Label(
        dialog,
        text = (
            f'Please name the file according to convention.\n\n'
            f'Original File location: {file_path}'
        ),
        justify = 'left',
        wraplength = 550
    ).pack(padx = 15, pady = (15, 10))

    tk.Label(
        dialog,
        text = 'Type of Checklist'
    ).pack(padx = 15, pady = (15, 0))

    checklist_type = tk.StringVar()

    type_dropdown = ttk.Combobox(
        dialog,
        textvariable=checklist_type,
        values=['Deployment', 'Return'],
        state='readonly',
        width=15
    ).pack(padx = 15, pady = (15, 0))

    tk.Label(
        dialog,
        text = 'Request number'
    ).pack(padx = 15, pady = (15, 0))

    request_nr = tk.StringVar()

    tk.Entry(
        dialog,
        textvariable = request_nr,
        width = 15
    ).pack(padx = 15, pady = (15, 0))

    no_ci_found = tk.BooleanVar(value=False)

    tk.Checkbutton(
        dialog,
        text='There is no way for me to find the Request Number',
        variable=no_ci_found
    ).pack(padx=15, pady=(5, 15))

    tk.Label(
        dialog,
        text = 'CI number'
    ).pack(padx = 15, pady = (15, 0))

    ci_nr = tk.StringVar()

    tk.Entry(
        dialog,
        textvariable = ci_nr,
        width = 15
    ).pack(padx=15, pady=(5, 15))

    button_frame = tk.Frame(dialog)
    button_frame.pack(padx = 15, pady = (5, 15))
    
    request_img_label = tk.Label(
        dialog,
        image = picture,
        relief = "solid",
    ).pack(padx=15, pady=(5, 15))

    tk.Button(
        button_frame,
        text = 'Open existing file',
        command = open_existing_file,
        width = 12
    ).pack(side = 'left', padx = 5)

    tk.Button(
        button_frame,
        text = 'Rename',
        command = confirm,
        width = 12
    ).pack(side = 'left', padx = 5)

    tk.Button(
        button_frame,
        text = 'Cancel',
        command = cancel,
        width = 12
    ).pack(side = 'left', padx = 5)

    #binding keys and closing the window to relevant methods
    dialog.protocol("WM_DELETE_WINDOW", cancel)     
    dialog.bind('<Return>', lambda event: confirm())
    dialog.bind('<Escape>', lambda event: cancel())

    dialog.attributes('-topmost', True)
    dialog.focus_set()
    dialog.lift()
    
    dialog.wait_window()
    

#inform user of completion of the script
messagebox.showinfo(
    'Operation Complete',
    'All PDF files have been processed and renamed successfully.'
)
    
                    

        
            


