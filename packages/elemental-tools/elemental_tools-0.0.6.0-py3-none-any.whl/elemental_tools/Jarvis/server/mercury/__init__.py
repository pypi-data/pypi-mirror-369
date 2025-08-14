import threading
from time import sleep
import re
from bson import ObjectId
from selenium import webdriver
from selenium.common import TimeoutException, \
    WebDriverException, NoSuchWindowException

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains

from elemental_tools.Jarvis.server.basic import BasicServer
from elemental_tools.logger import Logger
from elemental_tools.Jarvis.config import chrome_options, webdriver_url, log_path, chrome_data_dir
from elemental_tools.Jarvis.brainiac import Brainiac, NewRequest, BrainiacRequest
from elemental_tools.Jarvis.exceptions import Unauthorized, Error, InvalidOption
from elemental_tools.safety import InternalClock
from elemental_tools.api.controllers.user import UserController
from elemental_tools.api.controllers.wpp import WppController
from elemental_tools.api.controllers.notification import NotificationController
from elemental_tools.api.models import UserRequestModel
from elemental_tools.api.models.notification import NotificationRequestModel
from elemental_tools.api.settings import SettingsController
from elemental_tools.config import enable_grid, root_user
from elemental_tools.Jarvis.tools import Tools, extract_and_remove_quoted_content
from elemental_tools.adb import send_wpp_message, ADB
from elemental_tools.templates import Templates

module_name = 'mercury'

logger = Logger(app_name='jarvis', owner='mercury', destination=log_path).log


class RequestMercury(BrainiacRequest):
    cellphone = None
    language = 'en'

    translated_message = None
    translated_message_model = None

    skill_examples = None

    translated_message_model_lemma = None
    user: UserRequestModel = UserRequestModel()

    quoted_content = None

    def __init__(self, request):
        super().__init__()

        self.request = request

        for attr_name in dir(request):
            if not callable(getattr(request, attr_name)) and not attr_name.startswith("__"):
                setattr(self, attr_name, getattr(request, attr_name))

    def __call__(self):
        return self.request


class Mercury(BasicServer):
    """
    The Mercury class represents a tool for interacting with WhatsApp Web.
    It is server based because consists on a never stopping loop (I guess) and receives the brainiac arg.
    We also fixed some internal variables to limit requesting as it's not the most conventional way to work with whatsapp.

    I hope you`ll enjoy, cuz I`ll not.

    Read the documentation for more.

    Args:
        brainiac (Brainiac): An instance of Brainiac or None.
        bypass_translator (bool): Flag to bypass the translator.
        adb (bool): Flag to enable Android Debug Bridge (ADB).
        notifications_only (bool): Flag to enable notifications only.`
        smooth (bool): Flag for smooth interactions, avoiding excessive iterations.
            To not break the limits of whatsapp customer load.
        smooth_timer (bool): This allows you to control in how much time your old messages and this kind of stuff gets rechecked.

    Attributes:
        connected (bool): Indicates whether Mercury is connected to WhatsApp Web.
        wts_url (str): The URL for WhatsApp Web.
        wpp_db (WppController): The controller for WhatsApp data.
        notification_db (NotificationController): The controller for notifications.
        cellphone (str): The title of the WhatsApp contact.
        user_db (UserController): The controller for user data.
        page_content: The content of the web page.
        log_owner (str): The owner identifier for logging purposes.
        driver_options: Options for configuring the web driver (provide the actual options).
        tools (Tools): Tools for various purposes.

    Note:
        The `driver_options` attribute should be initialized with actual Chrome options.

    """
    _clock = InternalClock(logger=logger)
    connected = False
    wts_url = "https://web.whatsapp.com/"
    wpp_db = WppController()
    notification_db = NotificationController()
    cellphone = ""
    user_db = UserController()
    page_content = None
    log_owner = 'mercury'
    driver_options = chrome_options
    _b = webdriver.Chrome
    _first_state = True


    def __init__(self, brainiac: Brainiac, bypass_translator: bool = False, adb: bool = False,
                 notifications_only: bool = False, smooth: bool = True):

        self._adb = adb

        if self._adb:
            ADB()

        self.bypass_translator = bypass_translator

        if not notifications_only:
            self.brainiac = brainiac
            self.brainiac.bypass_translator = bypass_translator

            logger('alert', f'Setting Chrome data dir: {chrome_data_dir}')

            self.driver_options.add_argument(f"profile-directory=Profile 1")
            self.driver_options.add_argument(f"user-data-dir={chrome_data_dir}")

        self.notifications_only = notifications_only
        self.smooth = smooth
        self.smooth_timer = 100
        self.start()

    def is_browser_enabled(self):
        try:
            if self._b.session_id is not None:
                return True
        except:
            try:
                self._b.close()
            except:
                pass

        return False

    def browser(self):

        if not enable_grid:
            self._b = webdriver.Chrome(options=self.driver_options)

        else:
            try:
                self._b = webdriver.Remote(command_executor=webdriver_url, options=self.driver_options)
            except Exception as e:
                logger('critical', f"Browser failed because of an error: {str(e)}")

        return self._b

    def connect(self):
        self._b.get(self.wts_url)

        while not self.connected:
            try:
                logger('info', "Waiting for QR code scan...")

                WebDriverWait(self._b, 1000).until(
                    expected_conditions.presence_of_element_located((By.CLASS_NAME, "_3WByx")))

                self.page_content = self._b.page_source
                self.connected = True

            except TimeoutException:
                print("Timeout occurred. Retrying...")
                sleep(2)
                continue

        return self.connected

    def clean_phone(self, phone):
        _result = phone
        _result = _result.replace(' ', '')
        _result = _result.replace('-', '')
        return _result

    @_clock.limiter_decorator('2/minute', enable_sleep=True)
    def send_message(self, request: NewRequest):
        logger('info', f'Sending Message')

        cellphone, message = request.cellphone, request.skill.result

        _header = SettingsController().get(root_user, "attendant_default_response_header")
        if _header is not None:
            message = f"*{_header}*\n\n{message}"

        if self._adb:
            logger('info', f'Sending Message: {cellphone, message}', new_own="ADB")
            send_wpp_message(cellphone, message)

        else:
            log_owner = module_name + '-send-message'
            logger('info', f'Client Title: {str(cellphone)} Response: {str(message)}', new_own=log_owner)

            self._b.find_element(By.XPATH, f"//span[@dir='auto' and @title='{cellphone}']").click()
            logger('info', f"""Mercury clicked on: //span[@dir='auto' and @title='{cellphone}']""")

            input_xpath = (
                '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]'
            )

            logger('alert', f"Mercury typing...")

            input_box = WebDriverWait(self._b, 60).until(
                expected_conditions.presence_of_element_located((By.XPATH, input_xpath)))
            input_box.send_keys(message)
            input_box.send_keys(Keys.ENTER)

        sleep(2)
        logger('success', f"Message processed!")

    def get_selected_conversation(self, old=False):
        contact_title = None
        default_path = """//div[@class='g0rxnol2']//div[@aria-selected='true']//div[contains(@class, '_199zF _3j691')]//div[@class='_8nE1Y']//div[@role='gridcell' and @aria-colindex='2']"""

        # selected_contact = self._b.find_element(By.XPATH, f"{default_path}//div[@class='_21S-L']")

        # cellphone = selected_contact.find_element(By.XPATH, f"{default_path}//div//span[@dir='auto']").get_attribute("title")

        if not old:
            contact_title = self._b.find_element(By.XPATH, f"{default_path}//span[@dir='auto']").get_attribute(
                "title")
        else:
            contact_title = self._b.find_element(By.XPATH, f"{default_path}//span[@dir='auto']").get_attribute(
                "title")

        logger('conversation', f"The selected conversation is: {contact_title}")

        return contact_title

    def get_lang_from_country_code(self, cellphone):
        log_owner = module_name + '-language-selector'
        self.tools.codes_and_languages()
        try:
            contact_lang = \
            [lang for code, lang in self.tools.codes_and_languages().items() if cellphone.startswith(code)][0]
        except:

            if cellphone.startswith('+'):
                contact_lang = 'en'
            else:
                contact_lang = 'auto'

        logger('info', f"The defined language is {contact_lang}")
        return contact_lang

    @_clock.limiter_decorator('30/hour', enable_sleep=True)
    def verify_notifications(self):

        _to_send_notifications = {}
        _to_send_responses = {}
        _failed = []

        _result_notifications = {}
        _result_responses = {}

        _is_there_notifications = self.notification_db.is_there_notifications()
        _is_there_responses = self.notification_db.is_there_responses()

        logger('info', f"Verifying for new notifications...", new_own='notification')

        # PREPARE NOTIFICATIONS
        if _is_there_notifications:
            logger('info', f"Notifications found!")
            _notifications = self.notification_db.query_all(self.notification_db.notification_selector)
        else:
            logger('alert', f"No Notifications found, skipping...")
            _notifications = []

        # PREPARE RESPONSES
        if _is_there_responses:
            logger('info', f"Responses found!")
            _responses = self.notification_db.query_all(self.notification_db.responses_selector)
        else:
            logger('alert', f"No Responses found, skipping...")
            _responses = []

        # ATTACH NOTIFICATIONS TO BE SENT
        for notification in _notifications:
            try:
                logger('info', f"Processing Notification {str(notification['_id'])}")

                notification = NotificationRequestModel(**notification)

                if notification.sub is not None:
                    _destination = self.user_db.query({'_id': ObjectId(notification.sub)})
                    _destination = UserRequestModel(**_destination)

                    _content = self.translate_output(notification.content, _destination.language)

                    _to_send_notifications = {**_to_send_notifications,
                                              str(notification.get_id()): {"destination": str(_destination.get_id()),
                                                                           "content": str(_content)}}

                if notification.role is not None:

                    _users_in_role = self.user_db.query_all({'role': {"$in": notification['role']}})

                    for user in _users_in_role:
                        _destination = self.user_db.query({'_id': ObjectId(user['_id'])})
                        _content = self.translate_output(notification['content'], _destination['language'])
                        _to_send_notifications[notification.get_id()] = {"destination": str(_destination.get_id()),
                                                                           "content": str(_content)}
            except:
                pass

        # ATTACH RESPONSES TO BE SENT
        for response in _responses:

            response_id = str(response['_id'])
            template_id = None
            try:
                logger('info', f"Processing Response {str(response_id)}")

                response = NotificationRequestModel(**response)

                if response.customer_id is not None:

                    _destination = self.user_db.query({'_id': ObjectId(response.customer_id)})
                    _destination = UserRequestModel(**_destination)

                    _content = None

                    if response.template is not None:
                        _template = Templates(sub=response.sub, template_id=response.template)

                        if _template.this_template is not None:
                            _this_template = _template.this_template

                            for var in _this_template.variables:
                                try:
                                    if _destination.__getattribute__(var):
                                        _this_template.variables[var] = _destination.__getattribute__(var)

                                except AttributeError:
                                    _this_template.variables[var] = ''
                            try:
                                template_id = response.template
                                _content = _template.load(response.modifiers, _this_template.variables)

                            except Exception as e:
                                _failed[response.get_id()] = str(e)

                    else:
                        _content = response.response

                    _to_send_responses = {**_to_send_responses,
                                          str(response_id): {"destination": str(_destination.get_id()),
                                                             "content": str(_content), "template_id": template_id}}

            except Exception as e:
                logger('alert', f"Response {str(response_id)} failed because of exception: {str(e)}")
                pass

        # SEND NOTIFICATIONS (Internal "C2P")
        for notification_id in _to_send_notifications:
            try:
                for destination, content in _to_send_notifications[notification_id]:
                    destination = destination
                    content = content

                    logger('info',
                           f"Sending notification {str(notification_id)} to {str(destination)} and content {str(content)}")

                    try:
                        _request = NewRequest(
                            message=content,
                            cellphone=""
                        )
                        _this_user = self.user_db.query({"_id": ObjectId(destination)})
                        _request.cellphone = _this_user['cellphone']

                        _request.skill.result = content

                        self.send_message(_request)

                        _result_notifications[notification_id] = True

                    except:
                        _result_notifications[notification_id] = False
            except:
                pass

        # UPDATE THE NOTIFICATION DATABASE
        if _result_notifications.values() and _is_there_notifications:
            logger('info', f"Updating Notification Information")

            _update_notification_filter = []
            for notification_id in _result_notifications:
                if _result_notifications[notification_id]:
                    _update_notification_filter.append(notification_id)

            _update_notification_result = self.notification_db.set_notifications_status(_update_notification_filter)

            if _is_there_notifications and all(_result_notifications.values()) and _update_notification_result:
                logger('success', f"Successfully sent notification's!")

            else:
                logger('error', f"Error sending some notification's, you should take a look.")

        # SEND RESPONSES (External "P2C")
        for response_id in _to_send_responses.keys():

            destination = _to_send_responses[response_id]['destination']
            content = _to_send_responses[response_id]['content']
            template_id = _to_send_responses[response_id]['template_id']

            try:
                logger('info', f"Sending Response {str(response_id)} to {str(destination)} and content: {str(content)}")
                try:
                    _request = NewRequest(
                        message=content,
                        cellphone=destination
                    )
                    _request.skill.result = content

                    _this_user = self.user_db.query({"_id": ObjectId(destination)})
                    _request.cellphone = _this_user['cellphone']

                    if template_id is not None:
                        _template = Templates(str(destination), template_id)

                    else:
                        _selector_human_attendance_update = {"$and": [{"_id": ObjectId(_this_user["_id"])}, {
                            "$or": [{"role": {"$exists": False}}, {"role": {"$nin": constants.internal_roles}},
                                    {"admin": {"$ne": True}}]}]}
                        _result_pipeline_under_human_attendance = self.user_db.update(_selector_human_attendance_update,
                                                                                      {"is_human_attendance": True})

                    self.send_message(_request)
                    _result_responses[response_id] = True
                except:
                    _result_responses[response_id] = False

            except Exception as e:
                logger('alert',
                       f"Failed to Send Response {str(response_id)} to {str(destination)} and content: {str(content)}.\nBecause of exception: {str(e)}")
                pass

        # UPDATE THE RESPONSES DATABASE
        if _result_responses.values() and _is_there_responses:
            logger('info', f"Updating Responses Information")

            _update_responses_filter = []

            for response_id in _result_responses:
                if _result_responses[response_id]:
                    _update_responses_filter.append(response_id)

            _update_responses_result = self.notification_db.set_responses_status(_update_responses_filter)

            if _is_there_responses and all(_result_responses.values()) and _update_responses_result:
                logger('success', f"Successfully sent Responses!")

            else:
                logger('error', f"Error sending some Responses, you should take a look.")

        logger('conversation', f"Notifications Processed Successfully", new_own='notification')
        return _result_notifications, _result_responses

    def hang_on_function(self):
        logger('info', f"Hanging on...", new_own="conversation")

        def check_for_new_messages(stop_waiting):
            while True:
                logger('info', f"Waiting...", new_own="new-conversation-monitor")
                try:
                    WebDriverWait(self._b, 0.5).until(
                        expected_conditions.presence_of_element_located((By.CLASS_NAME, "_199zF._3j691._1KV7I"))
                    )
                    stop_waiting()
                    return True
                except:
                    return None

        def delete_message(cellphone):
            actionChains = ActionChains(self._b)
            if cellphone:
                current_contact = self._b.find_element(By.XPATH,
                                                       f"//span[@dir='auto' and @title='{cellphone}']")
                actionChains.context_click(current_contact).perform()
                try:
                    delete_conversation_button = WebDriverWait(self._b, 10).until(
                        expected_conditions.visibility_of_element_located(
                            (By.XPATH, """//*[@id="app"]/div/span[4]/div/ul/div/li[3]""")))
                    sleep(0.5)
                    delete_conversation_button.click()
                    confirm_button = WebDriverWait(self._b, 10).until(expected_conditions.visibility_of_element_located(
                        (By.XPATH,
                         "//button[@class='emrlamx0 aiput80m h1a80dm5 sta02ykp g0rxnol2 l7jjieqr hnx8ox4h f8jlpxt4 l1l4so3b le5p0ye3 m2gb0jvt rfxpxord gwd8mfxi mnh9o63b qmy7ya1v dcuuyf4k swfxs4et bgr8sfoe a6r886iw fx1ldmn8 orxa12fk bkifpc9x rpz5dbxo bn27j4ou oixtjehm hjo1mxmu snayiamo szmswy5k']")))
                    sleep(0.2)
                    confirm_button.click()

                except TimeoutException:
                    pass

        def read_conversation(contact_title):

            _today_messages_elements = self._b.find_elements(By.XPATH,
                                                             "//div[@tabindex='-1' and @class='n5hs2j7m oq31bsqd gx1rr48f qh5tioqs']//div[@role='row']//div[contains(@class,'CzM4m _2zFLj') and contains(@data-id, 'false_')]")
            _incoming_messages = []
            for _message in _today_messages_elements:
                try:
                    income = _message.find_element(By.XPATH, ".//div[contains (@class, 'message-in')]")
                    income.get_attribute('class')
                    _incoming_messages.append(_message)
                except WebDriverException as e:
                    pass

            if len(_incoming_messages):
                logger('info', f"Reading {contact_title} conversation...", new_own="conversation")

                _last_message = _incoming_messages[-1].get_attribute('data-id')

                cache_processed_messages_ids = [_already_processed_message['msg_id'] for _already_processed_message in
                                         self._cache]

                logger('info', f"Checking if Last Message is Already Processed...", new_own="conversation")
                if _last_message not in cache_processed_messages_ids:
                    selected_contact_cellphone = re.search(r'_(\d+)@', [message.get_attribute('data-id') for message in
                                                                        _incoming_messages][0])

                    if selected_contact_cellphone:
                        selected_contact_cellphone = f"+{selected_contact_cellphone.group(1)}"
                    else:
                        raise Exception(f'Cannot Read Contact Cellphone Number. In {str(_incoming_messages)}')

                    data_ids_to_exclude = [msg['msg_id'] for msg in
                                           self.wpp_db.query({"cellphone": selected_contact_cellphone})]

                    not_processed_messages_ids = [message.get_attribute('data-id') for message in
                                                  _incoming_messages if
                                                  message.get_attribute(
                                                      'data-id') not in data_ids_to_exclude and message.get_attribute(
                                                      'data-id') is not None]

                    if len(not_processed_messages_ids):
                        logger('info',
                               f'Processing {len(not_processed_messages_ids)} Pending Messages: {not_processed_messages_ids}')
                        cellphone = selected_contact_cellphone
                        complete_content = ""

                        for not_processed_id in not_processed_messages_ids:
                            x_sel_not_processed_message = f"//div[@data-id='{not_processed_id}']//span[@dir='ltr']//span"
                            self._cache.append(not_processed_id)

                            try:
                                logger('info',
                                       f'Validating if message is already processed, with selector: {x_sel_not_processed_message}')
                                not_processed_ = self._b.find_element(By.XPATH, x_sel_not_processed_message)
                            except:
                                continue

                            complete_content += f"{not_processed_.text}\n"

                            _doc = {'msg_id': str(not_processed_id), 'cellphone': str(cellphone)}

                            logger('info',
                                   f'Attempting to process message: {not_processed_id}')
                            if self.wpp_db.add(_doc):
                                logger('info',
                                       f'Processing message: id {not_processed_id}, contact {cellphone}, message {not_processed_.text}')

                            else:
                                logger('error',
                                       f'Message {not_processed_id} cannot be saved to database.')

                        user = self.user_db.query(selector={"cellphone": cellphone})

                        if user is None:
                            user = UserRequestModel()
                            user.language = self.get_lang_from_country_code(cellphone)
                            user.cellphone = cellphone
                            _user_dict = user.model_dump()
                            user.id = str(self.user_db.add(_user_dict)['_id'])
                        else:
                            user["id"] = str(user["_id"])
                            user = UserRequestModel(**user)

                        processable_text = self.translate_input(message=complete_content,
                                                                language=user.language)

                        try:
                            processable_text, quoted_content = extract_and_remove_quoted_content(
                                processable_text)
                        except:
                            quoted_content = []

                        if user.is_human_attendance:

                            try:

                                _pipeline_attendant_waiting_for_response = [
                                    {
                                        '$match': {"$and": [{"customer_id": str(user.get_id())},
                                                            {"responser_id": {'$exists': True}}]}
                                    },
                                    {
                                        '$sort': {
                                            'creation_date': 1
                                        }
                                    }
                                ]

                                _agg = self.notification_db.collection.aggregate(
                                    _pipeline_attendant_waiting_for_response)

                                _current_protocol = next(_agg)

                                _current_attendant = self.user_db.query(
                                    {"_id": ObjectId(_current_protocol['responser_id'])})

                                _attendant_request = NewRequest(
                                    message='',
                                    cellphone=_current_attendant['cellphone']
                                )

                                _requester_title = cellphone

                                if user.name is not None:
                                    _requester_title += f" - {user.name}"

                                _attendant_request_content = f"Protocol: \n{str(_current_protocol['_id'])}\n[{_requester_title}] "

                                _attendant_request_content += f"{complete_content}"

                                _attendant_request.skill.result = _attendant_request_content

                                self.send_message(_attendant_request)

                            except:

                                self.user_db.update({"_id": ObjectId(user.id)}, {"is_human_attendance": False})
                                user.is_human_attendance = False

                        if not user.is_human_attendance:

                            _brainiac_request = NewRequest(
                                message=processable_text,
                                cellphone=cellphone,
                                user=user
                            )

                            _brainiac_request.quoted_content = quoted_content
                            _brainiac_request.last_subject = user.last_subject

                            try:

                                _brainiac_request.skill.result = self.brainiac.process_message(
                                    _brainiac_request
                                )

                            except Unauthorized as er:

                                print("Raised Unauthorized")

                                _brainiac_request.skill.result = str(er)

                            except (InvalidOption, Error) as er:

                                print("Raised InvalidOption")

                                if user.last_subject and user.last_subject is not None:
                                    processable_text += f"\n{str(user.last_subject)}"

                                    _brainiac_request = NewRequest(
                                        message=processable_text,
                                        cellphone=cellphone,
                                        user=user,
                                        quoted_content=quoted_content
                                    )

                                    _brainiac_request.skill.result = self.brainiac.process_message(
                                        _brainiac_request
                                    )

                                else:
                                    _brainiac_request.skill.result = str(er)

                            _brainiac_request.skill.result = self.translate_output(
                                _brainiac_request.skill.result, user.language)

                            self.send_message(_brainiac_request)
                            if self.smooth:
                                sleep(self.smooth_timer)


                    else:
                        logger('alert',
                               f'No Pending Messages Found, skipping...')

                else:
                    logger('alert', f"Last Message Already Processed", new_own="conversation")

            body = self._b.find_element(By.TAG_NAME, "body")

            for i in range(3):
                body.send_keys(Keys.ESCAPE)

        @self._clock.limiter_decorator('30/hour', enable_sleep=True)
        def limited_read_conversation(contact_title):
            read_conversation(contact_title)

        if not self.notifications_only:
            logger('info', f"Processing messages", new_own="conversation")
            conversations = []
            self._cache = []

            try:
                load_side_bar = WebDriverWait(self._b, 10).until(
                    expected_conditions.presence_of_element_located((By.CLASS_NAME, "lhggkp7q.ln8gz9je.rx9719la"))
                )
            except:
                load_side_bar = False

            if load_side_bar:
                try:
                    WebDriverWait(self._b, 0.5).until(
                        expected_conditions.presence_of_element_located((By.CLASS_NAME, "_199zF._3j691._1KV7I"))
                    )
                    conversations = self._b.find_elements(By.CLASS_NAME, "_199zF._3j691._1KV7I")
                except:
                    pass

                # Process new messages
                if conversations:
                    _new_owner = "new-messages"

                    logger('conversation', f"Conversations Found!", new_own=_new_owner)
                    for conversation in conversations:
                        conversation.click()
                        contact_title = self.get_selected_conversation()
                        logger('info', f"New BrainiacRequest Received from {contact_title}", new_own=_new_owner)
                        read_conversation(contact_title)
                    logger('success', "New messages processed successfully.", new_own=_new_owner)

                # Process old messages
                else:
                    _cancel_waiting_thread = threading.Thread(target=check_for_new_messages, args=[self._clock.stop_waiting])
                    _cancel_waiting_thread.start()
                    _new_owner = "old-messages"

                    logger('info', "No new messages, searching for old ones that are not processed.", new_own=_new_owner)
                    old_conversations = self._b.find_elements(By.XPATH, """//div[contains(@class, "_3YS_f")]//div[contains(@class, '_199zF')]""")

                    logger('info', f"Old conversations found: {old_conversations}", new_own=_new_owner)
                    for each_conversation in old_conversations:
                        try:
                            each_conversation.click()
                            try:
                                limited_read_conversation(self.get_selected_conversation(old=True))
                            except self._clock.ExceptionStopWaiting:
                                _cancel_waiting_thread.join()
                                return True

                        except:
                            pass

                    _cancel_waiting_thread.join()
                    logger('success', "Old messages processed successfully.")

            else:
                logger('conversation', "No available conversations to hang on, as soon you receive a message, I will be working on!")
                pass

        self.verify_notifications()

        logger('conversation', f"Waiting for next execution...")


    def infinity_loop(self):
        while self.is_browser_enabled() or (self.notifications_only and ADB().check()):
            self.hang_on_function()

        if not self.is_browser_enabled():
            self.restart()

    def restart(self):
        logger('alert', 'Browser must be reinitialized')
        sleep(60)

        if not self.is_browser_enabled():
            self.browser()
            logger('success', "Browser Restarted Successfully")

        if self.is_browser_enabled():
            self.connect()
            logger('success', "Whatsapp Connected Successfully")
            self.hang_on()

        while not self.is_browser_enabled():
            try:
                WebDriverWait(self._b, 2000)
            except Exception as e:
                self.restart()

        if self.is_browser_enabled():
            self.infinity_loop()

    def hang_on(self):

        while True:
            try:
                sleep(2)
                self.infinity_loop()
                logger('fatal-error', 'Hang on loop unexpectedly quit')

            except WebDriverException:
                pass

    def start(self):

        try:
            logger('start', 'Initializing')
            if not self.notifications_only:
                sleep(5)
                self.browser()
                logger('info', "Prompting for Whatsapp Connection")
                self.connect()

            if self._adb:
                ADB().check()

            logger('success', "Whatsapp Connected!")
            self.hang_on()

        except WebDriverException or NoSuchWindowException:
            self.restart()
