from flask import Flask, render_template, request, redirect, send_file
from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup
import csv
from file import save_to_file

app = Flask("JobScrapper")

# 새로운 전역 변수를 추가하여 검색된 작업을 저장합니다. 
cached_jobs_db = {}

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/search")
def search():
    keyword = request.args.get("keyword")
    if keyword == None:  # 키워드가 이미 cached_jobs_db에 있는지 확인합니다.
         return redirect("/")
    if keyword not in cached_jobs_db:
        jobs_db = scrape_jobs(keyword)
        cached_jobs_db[keyword] = jobs_db   # 새로운 검색 결과를 cached_jobs_db에 저장합니다.
    else: 
        jobs_db = cached_jobs_db[keyword]# 키워드가 이미 cached_jobs_db에 있다면, 그 값을 사용합니다.
    save_to_file(keyword, jobs_db)
    return render_template("search.html", keyword=keyword, jobs=jobs_db)

@app.route("/export")
def export():
    keyword = request.args.get("keyword")
    if keyword ==None:
        return redirect("/")
    if keyword  not in cached_jobs_db:
        return redirect(f"/search?keword={keyword}")
    save_to_file(keyword, cached_jobs_db[keyword])
    return send_file(f"{keyword}_jobs.csv", as_attachment=True)

def scrape_jobs(keyword):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(f"https://www.wanted.co.kr/search?query={keyword}&tab=position")
        time.sleep(1)

        for x in range(3):
            time.sleep(1)
            page.keyboard.down("End")

        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
        jobs = soup.find_all("div", class_="JobCard_container__REty8")
        jobs_db = []

        for job in jobs:
            link = f"https://www.wanted.co.kr{job.find('a')['href']}"
            title = job.find("strong", class_="JobCard_title__HBpZf").text
            company_name = job.find("span", class_="JobCard_companyContent___EEde").text
            reward = job.find("span", class_="JobCard_reward__cNlG5").text
            job = {
                "keyword": keyword,
                "title": title,
                "company_name": company_name,
                "reward": reward,
                "link": link
            }
            jobs_db.append(job)
            
        browser.close()
    return jobs_db

def save_to_file(keyword, jobs_db):
    file = open(f"{keyword}_jobs.csv", "w")
    writer = csv.writer(file)
    writer.writerow(["Title", "Company", "Reward", "Link"])

    for job in jobs_db:
        writer.writerow(job.values())
    file.close()

app.run("0.0.0.0", port=5001,  debug=True)
