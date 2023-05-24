from sms_ir import SmsIr

from app.core.config import settings


def send_verify_sms(receptor, code, template_id):
    sms_ir = SmsIr(
        api_key=settings.SMS_IR_API_KEY, linenumber=str(settings.SMS_IR_LINE_NUMBER)
    )
    res = sms_ir.send_verify_code(
        number=receptor,
        template_id=template_id,
        parameters=[{'name': 'CODE', 'value': str(code)}],
    )
    print(res.json())
    return res.status_code
