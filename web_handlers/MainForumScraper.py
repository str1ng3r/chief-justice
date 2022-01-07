import bs4
from database_managers.CaseManager import CaseManager
import requests


def get_num_pages(response):
    str_response = str(response)
    page_str_index = str_response.find("Page 1 of ")
    if page_str_index != -1:
        return int(str_response[page_str_index + 10])
    else:
        return 1


class MainForumScraper:
    def __init__(self, user, password):
        self.url = 'https://forum.gta.world/'
        self.login_url = 'https://forum.gta.world/en/login/'
        self.user = user
        self.password = password
        self.criminal_url = 'https://forum.gta.world/en/forum/389-criminal-division/'
        self.traffic_url = 'https://forum.gta.world/en/forum/708-traffic-division/'
        self.civil_url = 'https://forum.gta.world/en/forum/390-civil-division/'
        self.cases = dict()
        self.browser = None

    def __process_response(self, response, case_type):
        # Creates a beautiful soup object based on the response
        soup = bs4.BeautifulSoup(response, features="html5lib")
        # Finds all of the forum posts, individual and ignores the first one, since it's the archive link.
        posts = soup.find_all("li", {"class": "ipsDataItem"})[1:]

        main_body_divs = list()
        last_post_uls = list()
        # Will loop through ahh the forum posts
        for post in posts:
            # This gets all the divs that have that class and places them in a list (Because it contains the url)
            main_body_divs.append(post.find("div", {"class": "ipsDataItem_main"}))
            # And this gets all the uls that contain the last poster info, into a list.
            last_post_uls.append(post.find("ul", {"class": "ipsDataItem_lastPoster"}))

        # Iterates through the lists and transforms the time into a unix timestamp, then adds them to a list.
        for div, ul in zip(main_body_divs, last_post_uls):
            self.cases[div.find('a')['title'][:-1]] = [div.find('a')['href'], case_type]

    async def get_cases(self, case_type):
        if case_type == 'civil':
            url = self.civil_url
        elif case_type == 'traffic':
            url = self.traffic_url
        else:
            url = self.criminal_url
        # Opens a requests session
        with requests.Session() as s:

            # Sets the headers that work for the gta world forums.
            headers = {
                "Host": "forum.gta.world",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            }
            # Goes to the base page of the forum, gets it and grabs the csrf and ref key from it.
            response = s.get(self.url, headers=headers)
            soup = bs4.BeautifulSoup(response.text, "html.parser")
            csrf_key = soup.find("input", {"name": "csrfKey"}).get("value")
            ref_key = soup.find("input", {"name": "ref"}).get("value")
            # Create the payload dictionary and
            payload = {
                "csrfKey": csrf_key,
                "ref": ref_key,
                "auth": self.user,
                "password": self.password,
                "remember_me": "1",
                "_processLogin": "usernamepassword"
            }
            # Makes a post request to log in to the page
            s.post(self.login_url, headers=headers, data=payload)
            response = s.get(url, headers=headers)
            # Computes how many pages the forum has
            pages = get_num_pages(response.text)

            # Processes the first forum page
            self.__process_response(response.text, case_type)
            # Processes the other pages, 2, 3, ...
            for i in range(pages - 1):
                response = s.get(f'{url}/page/{i + 2}', headers=headers)
                self.__process_response(response.text, case_type)
        cm = CaseManager()
        await cm.add_case(self.cases)
        await cm.close()
        self.cases.clear()
