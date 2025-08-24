# -------------------------------------------------------------
# BISE SARGODHA RESULT SCRAPER
# -------------------------------------------------------------
# What this script does:
# - Connects to the official BISE Sargodha result website
# - Sends roll numbers one by one (in a given range)
# - Collects student name, roll number, and result (marks/fail/pass)
# - Saves all the data in a neat PDF table
#
# Why this script is useful:
# - When results are first announced, you can ONLY search by roll number.
# - If you know your friend's school roll number range, you can loop through all of them
#   and find their marks without manually entering numbers on the website.
#
# How to use:
# 1. Change the `start_roll` and `end_roll` variables at the bottom to your desired roll numbers.
# 2. Run the script. It will fetch results and save them in a PDF file.
# -------------------------------------------------------------

import requests                     # lets us send requests to websites
from bs4 import BeautifulSoup       # makes it easy to read and search HTML pages

# this is the website URL for results
BASE = "http://119.159.230.2/biseresultday2/resultday.aspx"


# -------------------------------------------------------------
# STEP 1: GET THE TOKENS NEEDED TO TALK TO THE WEBSITE
# -------------------------------------------------------------
def get_tokens(session):
    """
    The result page uses hidden security fields called __VIEWSTATE and __EVENTVALIDATION.
    Without these, the server will reject your request.
    This function goes to the page, finds those tokens, and returns them.
    """
    # open the result page
    r = session.get(BASE, timeout=20)
    r.encoding = 'utf-8'  # make sure text is displayed correctly

    # use BeautifulSoup to search through the page HTML
    soup = BeautifulSoup(r.text, "lxml")

    # find the hidden fields by their ID
    viewstate = soup.select_one("#__VIEWSTATE")["value"]
    eventvalidation = soup.select_one("#__EVENTVALIDATION")["value"]

    # return them so they can be used in the next request
    return viewstate, eventvalidation


# -------------------------------------------------------------
# STEP 2: FETCH RESULT FOR ONE ROLL NUMBER
# -------------------------------------------------------------
def fetch_one_roll(session, roll_no):
    """
    Takes one roll number, sends it to the website, and extracts:
    - Student's Name
    - Student's Roll Number (as displayed on site)
    - Student's Result (marks, pass/fail, etc.)
    
    Returns a dictionary like:
    {"Roll No": "763130", "Name": "Ali Khan", "Result": "Passed with 850 marks"}
    """
    try:
        # get the hidden security tokens for this request
        viewstate, eventvalidation = get_tokens(session)

        # this is the data we are "posting" to the website
        # it simulates what happens when you fill in the form and press "Show Result"
        payload = {
            "__VIEWSTATE": viewstate,
            "__EVENTVALIDATION": eventvalidation,
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "RbtSearchType": "Search by Roll No.",  # tells the website we are searching by roll number
            "TxtSearchText": str(roll_no),          # this is the actual roll number we are searching for
            "BtnShowResults": "Show Result",        # simulates clicking the button
        }

        # headers to make us look like a normal browser
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": BASE
        }

        # send the data to the site
        resp = session.post(BASE, data=payload, headers=headers, timeout=20)
        resp.encoding = "utf-8"

        # parse the response page
        soup = BeautifulSoup(resp.text, "lxml")

        # check if the site gave an error message (invalid roll number, etc.)
        err = soup.select_one("#LblErr")
        if err and err.get_text(strip=True):
            return {"Roll No": roll_no, "Name": "", "Result": err.get_text(strip=True)}

        # extract the student's name
        name_tag = soup.select_one("#LblName")
        name = name_tag.get_text(strip=True) if name_tag else ""

        # extract the roll number shown on the page
        roll_tag = soup.select_one("#LblRollNo")
        roll_on_page = roll_tag.get_text(strip=True) if roll_tag else str(roll_no)

        # extract the result or marks
        res_tag = soup.select_one("#lblGazres")
        final_result = res_tag.get_text(strip=True) if res_tag else ""

        # return the collected data
        return {
            "Roll No": roll_on_page,
            "Name": name,
            "Result": final_result
        }

    except Exception as e:
        # if something goes wrong, return an error message
        return {"Roll No": roll_no, "Name": "", "Result": f"Error: {e}"}


# -------------------------------------------------------------
# STEP 3: SAVE RESULTS TO A PDF
# -------------------------------------------------------------
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def save_summary_pdf(data_list, filename="bise_results_summary.pdf"):
    """
    Takes a list of dictionaries (with Roll No, Name, and Result)
    and saves them into a neat PDF table for easy viewing.
    """
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(filename, pagesize=landscape(A4))
    elements = []

    # title of the PDF
    elements.append(Paragraph("BISE Sargodha Exam Results (Summary)", styles['Title']))
    elements.append(Spacer(1, 20))  # space under the title

    # create table header
    rows = [["Roll No", "Name", "Final Result"]]

    # add each student's data to the table
    for entry in data_list:
        rows.append([
            entry.get("Roll No", ""),
            entry.get("Name", ""),
            entry.get("Result", ""),
        ])

    # style the table to look nice
    table = Table(rows, colWidths=[100, 180, 250])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.darkblue),  # dark blue header
        ("TEXTCOLOR",(0,0),(-1,0),colors.whitesmoke),   # white header text
        ("ALIGN",(0,0),(-1,-1),"CENTER"),               # center align text
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),  # bold header text
        ("FONTSIZE", (0,0), (-1,0), 12),                # header font size
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey]), # alternating colors
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),    # table borders
        ("BOTTOMPADDING", (0,0), (-1,0), 8),            # extra padding under header
    ]))

    elements.append(table)
    doc.build(elements)
    print(f"✅ PDF saved: {filename}")


# -------------------------------------------------------------
# STEP 4: MAIN SCRIPT
# -------------------------------------------------------------
# Change these numbers to the roll number range you want to check
start_roll = 123456  # first roll number
end_roll = 123456   # last roll number

# empty list to store all student data
results = []

# create a session (keeps cookies and speeds up requests)
with requests.Session() as session:
    for rn in range(start_roll, end_roll + 1):
        print(f"Fetching result for Roll No: {rn}...")  # show progress
        data = fetch_one_roll(session, rn)              # get data for one student
        print(data)                                     # print to console
        results.append(data)                            # save in list

# once all results are collected, save them to a PDF
save_summary_pdf(results, "bise_results_summary.pdf")

# -------------------------------------------------------------
# NOTE:
# If 'reportlab' is not installed, install it by running:
#    pip install reportlab
# -------------------------------------------------------------
