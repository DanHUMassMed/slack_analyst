import os
import csv
import json
import uuid
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from reseacher_session_state import SessionState

def load_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def load_url_to_pdf(file_name):
    data = {}
    
    if not os.path.exists(file_name):
        # Create the file with the header only
        with open(file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['URL', 'PDF_NM', 'UUID'])
        # Return the empty dictionary
        return data
    
    with open(file_name, mode='r') as file:
        # Create a CSV reader object
        csv_reader = csv.DictReader(file)
        
        # Parse each line into the dictionary
        for row in csv_reader:
            data[row['URL']] = row['PDF_NM']

    return data


def urls_to_process(channel):
    
    pdf_pages_id = session.get('pdf_pages_id')
    if not pdf_pages_id:
        
        urls = load_json(f"resources/{channel}_urls.json")
        url_pdf_map = load_url_to_pdf(f"resources/{channel}_map.csv")
        session['pdf_pages_id'] = pdf_pages_id
        session['channel'] = channel
        
        pdf_pages_id = str(uuid.uuid4())
        session['pdf_pages_id'] = pdf_pages_id
        session_state = SessionState()
        pdf_pages = session_state.session_data(pdf_pages_id)
        for url in urls:
            pdf_pages[url] = url_pdf_map.get(url,"")
    else:
        session_state = SessionState()
        pdf_pages = session_state.session_data(pdf_pages_id) 
        
    for url in pdf_pages:
        print(f"YYYYYYYYYYYYYYY {url} {pdf_pages[url]}")
        
    return render_template("url_to_pdf_map.html", pdf_pages=pdf_pages)


def url_to_process_submit():
    button_clicked = int(request.form['submit_button'])
    url = request.form.get(f'url_{button_clicked}')
    pdf_page_nm = request.form.get(f'pdf_{button_clicked}')
    
    pdf_pages_id = session['pdf_pages_id']
    channel = session['channel']
    session_state = SessionState()
    pdf_pages = session_state.session_data(pdf_pages_id) 
    
    pdf_pages[url] = pdf_page_nm
    
    for field in request.form:
        print(f"XXXXXXXXXXXXXXX {field} {request.form[field]}")
        
    if url and pdf_page_nm:
        with open(f"resources/{channel}_map.csv", 'a', newline='') as f:
            writer = csv.writer(f)
            pdf_uuid = str(uuid.uuid4())
            writer.writerow([url, pdf_page_nm, pdf_uuid])
            
    return redirect(url_for(f"urls_to_process", channel=channel))

