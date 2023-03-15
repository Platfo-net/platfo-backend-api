import requests

from app.core.config import settings


def send_verify_sms(receptor, code, template):
    url = "{}/{}/verify/lookup.json".format(
        settings.KAVE_NEGAR_BASE_URL,
        settings.KAVE_NEGAR_API_KEY
    )
    body = {
        "receptor": receptor,
        "token": code,
        "template": template
    }
    res = requests.post(url, json=body)
    return res.status_code
