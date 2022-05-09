from twilio.rest import Client
from constant import twilio_account_sid, twilio_auth_token, page_email, twilio_phone_number, my_cell_phone_number
import smtplib
from email.message import EmailMessage

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
client = Client(twilio_account_sid, twilio_auth_token)

def send_message(earlier_date):
    message = client.messages.create(
             body='New us visa appointment available: {earlier_date}. Book it now!'.format(earlier_date=earlier_date),
             from_=twilio_phone_number,
             to=my_cell_phone_number
         )
    print(message.sid)

def send_email(earlier_date):
    msg = EmailMessage()
    msg['Subject'] = 'New us visa appointment available: {earlier_date}'.format(earlier_date=earlier_date)
    msg['To'] = page_email
    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.send_message(msg)
        print("Successfully sent email")
        smtpObj.quit()
    except Exception:
        print("Error: unable to send email")


if __name__ == "__main__":
    # Testing
    print('Sending a test message.')
    # response = send_message('2022-11-01')
    response = send_email('2022-11-01')
