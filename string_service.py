from service import *

def return_register_text(user_id):
    return session.query(LocalizationString).filter(LocalizationString.code == Subscriber.language)
