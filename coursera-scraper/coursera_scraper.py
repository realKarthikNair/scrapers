import requests
from bs4 import BeautifulSoup
import json
import os


def scrap_course(course_link, n):
    response = requests.get(course_link)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        course_elements = soup.find_all("h3", class_="cds-CommonCard-title css-6ecy9b")
        print(f"Found {len(course_elements)} courses.")
        course_names = [course.text for course in course_elements][:n]
        partner_elements = soup.find_all(
            "p", class_="cds-ProductCard-partnerNames css-vac8rf"
        )
        partner_names = [partner.text.strip() for partner in partner_elements][:n]
        stars = soup.find_all("p", class_="css-2xargn")
        print(f"Found {len(stars)} ratings.")
        ratings = [star.text for star in stars][:n]
        print(ratings)
        reviews_container = soup.find("div", class_="product-reviews css-pn23ng")
        reviews = (
            reviews_container.find_all("p", class_="css-vac8rf")
            if reviews_container
            else []
        )
        review_count = [review.text.strip() for review in reviews]
        script_tag = soup.find("script", type="application/ld+json")
        if script_tag:
            json_data = json.loads(script_tag.string)
            courses = []
            i = 0
            for item in json_data.get("itemListElement", [])[:n]:
                print("hello")
                position = item.get("position")
                url = item.get("url")
                if url:
                    try:
                        course_name = course_names[i]
                    except IndexError:
                        course_name = "N/A"
                    try:
                        partner_name = partner_names[i]
                    except IndexError:
                        partner_name = "N/A"
                    try:
                        rating = ratings[i]
                    except IndexError:
                        rating = "N/A"
                    try:
                        review = review_count[i]
                    except IndexError:
                        review = "N/A"

                    course = {
                        "position": position,
                        "url": url,
                        "course_name": course_name,
                        "partner_name": partner_name,
                        "rating": rating,
                        "review": review,
                    }
                    courses.append(course)
                    i += 1
                    print(i)
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
    return (
        "https://www.coursera.org/search?query="
        + course
        + "&productDifficultyLevel="
        + difficulty
        + "&=null"
    )


if __name__ == "__main__":
    course_name = "python"
    difficulty = "Advanced"
    # os.path.join("DB","courses", f"{course_name}_{difficulty}.json")
    file_name = os.path.join("DB", "courses", f"{course_name}_{difficulty}.json")
    link = generate_link(course_name, difficulty)
    print(f"Scraping data from {link}")
    n = 10

    # try:
    #     courses = scrap_course(link, n)
    #     break
    # except Exception as e:
    #     print(f"Error: {e}")
    #     if n == 1:
    #         break
    #     n -= 1
    try:
        courses = scrap_course(link, n)
        if courses:
            with open(file_name, "w") as f:
                json.dump(courses, f, indent=2)
                print(f"Data saved to {file_name}")
    except Exception as e:
        print(f"Error: {e}")
    else:
        print("No data was scraped.")
