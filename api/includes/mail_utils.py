from requests_futures.sessions import FuturesSession

from config import preferences


class EmailUtil:
    def __init__(
        self,
        subject: str,
        body: str,
        receiver_mail: str,
        attachment: bytes = None,
        file_name: str = None,
    ):
        app_conf = preferences.AppPreferences()
        self.subject = subject
        self.body = body
        self.receiver_mail: str = receiver_mail
        self.attachment: bytes = attachment
        self.file_name: str = file_name
        self.company_mail: str = app_conf.company_mail
        self.mail_domain: str = app_conf.mail_domain
        self.mail_api_key: str = app_conf.mail_api_key
        self.mail_provider_base_url: str = app_conf.mail_provider_base_url

    def send_mail(self):
        """Send the email with or without attachment"""
        session = FuturesSession()
        url = f"{self.mail_provider_base_url}/v3/{self.mail_domain}/messages"
        data = session.post(
            url,
            auth=("api", self.mail_api_key),
            files=(
                [("attachment", (self.file_name, self.attachment))]
                if self.attachment
                else None
            ),
            data={
                "from": self.company_mail,
                "to": self.receiver_mail,
                "subject": self.subject,
                "body": self.body,
                "text": self.body,
            },
        )
        return data
