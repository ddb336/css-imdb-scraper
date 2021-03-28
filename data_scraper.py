from bs4 import BeautifulSoup
from selenium import webdriver
import time
import csv
import lxml
import cchardet
from datetime import datetime

earliest = datetime(2017, 2, 28) # must be greater than this date

direction = 'desc' # or 'asc'

date_sections = []
for i in range(4):
    date_sections.append([datetime(2017+i, 2, 28), datetime(2017+i, 6, 1)])

movie_ids = []
with open('ids.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        movie_ids.append(row)

patience_time1 = 60
XPATH_loadmore = "//*[@id='load-more-trigger']"
XPATH_grade = "//*[@class='review-container']/div[1]"

custom_options = webdriver.ChromeOptions()
custom_options.headless = True

driver = webdriver.Chrome(options=custom_options)

for movie_id in movie_ids:

    url = 'https://www.imdb.com/title/' + movie_id[0] + '/reviews?sort=submissionDate&dir=desc&ratingFilter=0'

    print(url)

    driver.get(url)

    prev_date = datetime(1800, 1, 1)

    while True:
        soup = BeautifulSoup(driver.page_source[-150000:], "lxml")
        try:
            date_time_str = soup.select(".review-container")[-1].select(".review-date")[0].text
        except:
            continue
        date_time_obj = datetime.strptime(date_time_str, '%d %B %Y')
        
        if date_time_obj <= earliest:
            break

        time.sleep(0.1)

        loadmore = driver.find_element_by_id("load-more-trigger")
        driver.execute_script("arguments[0].click();", loadmore)

        if prev_date != date_time_obj:
            print("Earliest date: ", date_time_obj)

        prev_date = date_time_obj

    soup = BeautifulSoup(driver.page_source, "lxml")

    with open(movie_id[0] + '.csv', mode='w') as data_file:
        data = csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        data.writerow(['title', 'date', 'rating', 'review'])

        for item in soup.select(".review-container"):

            review_date = item.select(".review-date")[0].text
            date_time_obj = datetime.strptime(review_date, '%d %B %Y')
            if date_time_obj < earliest:
                break

            in_section = False
            for dates in date_sections:
                if date_time_obj > dates[0] and date_time_obj < dates[1]:
                    in_section = True
                    break
            if not in_section:
                continue

            review_title = item.select(".title")[0].text

            review_text = item.select(".text")[0].text

            review_rating = item.find_all("span")
            if len(review_rating) == 0:
                continue
            review_rating = review_rating[0].find_all("span")
            if len(review_rating) == 0:
                continue
            review_rating = review_rating[0].text

            data.writerow([str(review_title), str(date_time_obj), str(review_rating), str(review_text)])

    driver.quit()