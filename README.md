# BISE Sargodha Result Scraper

A Python script to automate fetching **BISE Sargodha Board exam results**. It lets you provide a **roll number range** and automatically scrapes each student’s **name, roll number, and result status**, then saves the data in a **clean, formatted PDF**.  
Built for the early hours of result announcements when **only roll number searches are available**.

---

## 📖 Why I Made This

When the BISE Sargodha results are announced, the site initially only supports **roll number-based searches**. Manually checking each student’s marks is slow and tedious, especially when you already know a school’s roll number range.  

I built this script to:
- Save time by automating the entire search process.
- Help quickly find results for a group of students.
- Learn **web scraping, Python automation, and PDF generation** in a fun way.

---

## 🚀 Features

- 🔢 Enter a **starting and ending roll number** to scan results.  
- 📜 Automatically fetch **name, roll number, and pass/fail or marks**.  
- 📝 Export results in a **neat, professional PDF**.  
- 🧩 Easy to customize for other boards or sites.  
- 🎓 Beginner-friendly with **clear comments** for learning.

---

## 🛠️ How It Works

1. The script uses `requests` to send roll number queries to the official result page.  
2. It scrapes the response using `BeautifulSoup4`.  
3. Data is organized and exported into a **PDF** using `reportlab`.  
4. The final PDF contains a **summary table of all results**.

---

## 📦 Requirements

- Python 3.x  
- `requests`  
- `beautifulsoup4`  
- `reportlab`  

Install them with:
```bash
pip install requests beautifulsoup4 reportlab
