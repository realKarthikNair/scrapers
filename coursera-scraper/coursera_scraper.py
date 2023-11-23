import requests
from bs4 import BeautifulSoup
import json
import os

def scrap_course(course_link, n):
    response = requests.get(course_link)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        course_elements = soup.find_all('h3', class_='cds-119 cds-CommonCard-title css-e7lgfl cds-121')
        course_names = [course.text for course in course_elements][:n]
        partner_elements = soup.find_all('p', class_='cds-119 cds-ProductCard-partnerNames css-dmxkm1 cds-121')
        partner_names = [partner.text.strip() for partner in partner_elements][:n]
        script_tag = soup.find('script', type='application/ld+json')
        if script_tag:
            json_data = json.loads(script_tag.string)
            courses = []
            i = 0
            for item in json_data.get('itemListElement', [])[:n]:
                position = item.get('position')
                url = item.get('url')
                if url:
                    courses.append([course_names[i], partner_names[i], url])
                    i += 1
            return courses
        else:
            print("Error: Unable to find JSON data in the script tag.")
            return None
    else:
        # Print an error message if the request was not successful
        print(f"Error: Unable to fetch data. Status code {response.status_code}")
        return None


def generate_link(course_name, difficulty):
    # eg https://www.coursera.org/search?query=data+science&productDifficultyLevel=Beginner&=null
    course = course_name.replace(" ", "+")
    return "https://www.coursera.org/search?query=" + course + "&productDifficultyLevel=" + difficulty + "&=null"



if __name__ == '__main__':
    course_name = "python"
    difficulty = "Advanced"
    # os.path.join("DB","courses", f"{course_name}_{difficulty}.json")
    file_name = os.path.join("DB","courses", f"{course_name}_{difficulty}.json")
    link = generate_link(course_name, difficulty)
    n = 10
    while True:
        try:
            courses=scrap_course(link, n)
            break
        except:
            if n == 1:
                break
            n -= 1
    if courses:
        with open(file_name, 'w') as f:
            json.dump(courses, f, indent=2)
        print(f"Data saved to {file_name}")
    else:
        print("No data was scraped.")
    