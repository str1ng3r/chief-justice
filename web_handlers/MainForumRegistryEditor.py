from database_managers.LawyerManager import LawyerManager
from bs4 import BeautifulSoup
import requests


class MainForumRegistryEditor:
    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.login_url = 'https://forum.gta.world/en/login/'
        self.edit_url = 'https://forum.gta.world/en/topic/26626-san-andreas-bar-association-%E2%80%94-bar-registry' \
                        '/?do=edit'
        self.registry_base_text = self.get_registry_base_text()
        self.headers = {
            "Host": "forum.gta.world",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }

    @staticmethod
    def get_registry_base_text():
        with open('web_handlers/forum_post_code/registry_base.txt', 'r') as f:
            base_text = f.read()
        return base_text

    async def process_lawyers(self, lawyers):
        with open('web_handlers/forum_post_code/final_post.txt', 'w') as f:
            f.write(self.get_registry_base_text())
            async for lawyer in lawyers:
                f.write(f"<strong>Name:</strong> {lawyer['name']}<br>")
                f.write(f"<strong>Bar ID:</strong> {lawyer['bar_id']}<br>")
                f.write(f"<strong>Firm:</strong> {lawyer['firm']}<br>")
                f.write(f"<strong>Specialty:</strong> {lawyer['specialty']}<br>")
                f.write(f"<strong>Availability:</strong> {lawyer['availability']}<br>")
                f.write(f"<strong>Billing:</strong> {lawyer['billing']}<br>")
                f.write(f"<strong>Phone:</strong> {lawyer['phone']}<br>")
                f.write(f"<strong>Email:</strong> {lawyer['email']}<br>")
                f.write(f"<strong>(( Forum name:</strong> {lawyer['forum_name']} <strong>))</strong><br>")
                f.write(f"<strong>(( Discord:</strong> {lawyer['discord']} <strong>))</strong><br>")
                f.write("<br>")
            f.write("</div>")

    def log_in(self, session):
        # Goes to the login url and grabs the csrf key
        response = session.get(self.login_url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        csrf_key = soup.find("input", {"name": "csrfKey"}).get("value")
        payload = {
            "csrfKey": csrf_key,
            "auth": self.user,
            "password": self.password,
            "remember_me": "0",
            "_processLogin": "usernamepassword"
        }
        # Logs in using the payload and header
        session.post("https://forum.gta.world/en/login/", headers=self.headers, data=payload)

    def edit_registry_post(self, session):
        # Reads the file to grab the final forum post.
        with open('web_handlers/forum_post_code/final_post.txt', 'r') as f:
            forum_post_content = f.read()
        # Goes to the edit page in order to grab the CSRF key
        response = session.get(self.edit_url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        csrf_key = soup.find("input", {"name": "csrfKey"}).get("value")
        payload = {
            "csrfKey": csrf_key,
            "form_submitted": 1,
            "topic_title": "San Andreas Bar Association — Bar Registry",
            "comment_edit_reason": 'If there are any errors, contact stringer#7136',
            "topic_content": forum_post_content
        }
        # Updates the post.
        session.post(self.edit_url, headers=self.headers, data=payload)

    async def update_forum_post(self):
        lawyer_manager = LawyerManager()
        lawyers = lawyer_manager.get_lawyers()
        await self.process_lawyers(lawyers)
        # Session is created here.
        session = requests.Session()
        self.log_in(session)
        self.edit_registry_post(session)
