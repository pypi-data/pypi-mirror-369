import smtplib
from email.mime.text import MIMEText


class SendEmail:

    def __init__(self, login, password, smtp_server, smtp_port, sender=None, destination=None):
        self.sender = sender
        self.destination = destination
        self.login = login
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def check_config(self):
        try:
            # Connect to the SMTP server
            _server = smtplib.SMTP(self.smtp_server, int(self.smtp_port))
            _server.starttls()
            print("Connected to SMTP server")
            try:
                _server.login(self.login, self.password)
                print("I just logged in to see in what condition, my condition was him.\n")
            except:
                raise Exception("Your smtp looks fine, maybe the problem is on your login information.")

            return True

        except Exception as e:
            raise Exception(f"Error registering e-mail: {e}")

    def send_email(self, subject, message, destination=None):
        # msg = MIMEText(message, 'plain')
        msg = MIMEText(message, 'html')
        msg['From'] = self.login
        if self.destination is None or destination is not None:
            msg['To'] = destination
        else:
            msg['To'] = self.destination
        msg['Subject'] = subject

        try:
            # Connect to the SMTP server
            _server = smtplib.SMTP(host=self.smtp_server, port=self.smtp_port)
            _server.starttls()
            print("Connected to SMTP server")
            # Login to the server
            _server.login(self.login, self.password)
            # Send the email
            print(f"Sending the email {self.login, self.destination, msg.as_string()}")
            _server.sendmail(self.login, self.destination, msg.as_string())
            return {'message': 'E-mail sent successfully.'}

        except Exception as e:
            raise Exception(f"Error sending email: {e}")


