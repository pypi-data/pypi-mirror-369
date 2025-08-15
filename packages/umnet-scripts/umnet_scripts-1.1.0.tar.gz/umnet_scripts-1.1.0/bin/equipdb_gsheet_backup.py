from pprint import pprint
import smtplib
from email.message import EmailMessage
import traceback
import warnings
# Suppress the deprecation warning from the cryptography module.
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import cryptography

from umnet_scripts import UMGoogleSheet, UMnetequip

SS_URL="https://docs.google.com/spreadsheets/d/1QDoucpdnPCgoNFW94f7wD9rtK633wRwpEfziuheG96s/edit#gid=0"

msg = EmailMessage()
msg['From'] = "umnet-autoalert"
msg['To'] = "amylieb@umich.edu"

try:
    eq = UMnetequip()
    gs = UMGoogleSheet(SS_URL)
    all_devices = eq.get_all_devices()
    all_devices_list = [dict(d) for d in all_devices]
    gs.create_or_overwrite_worksheet("Sheet1", all_devices_list)

except Exception:

    msg = EmailMessage()
    msg['Subject'] = "Auto-alert: Nightly eqdb dump failed"
    msg.set_content(f'{traceback.format_exc()}\nLink to spreadsheet: {SS_URL}')

else:
    msg['Subject'] = "Auto-alert: Nightly eqdb dump succeded"

s = smtplib.SMTP('localhost')
s.sendmail("umnet-autoalert@umich.edu", "amylieb@umich.edu", msg.as_string())
s.quit()
