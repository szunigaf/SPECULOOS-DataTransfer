# #!/opt/anaconda3/envs/speculoos_py3/bin/python
# For server deployment, use:
#!/home/speculoos/Programs/anaconda2/envs/speculoos_py3/bin/python
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 16:56:38 2019
Revised on Feb 17 2026

@author: laetitia
@author: Seba Zuniga-Fernandez
"""
import sys
import os
import smtplib

# Credentials are loaded from .credentials.csh by the calling shell script
# (transfer_Astra.csh / transfer_Astra_spirit.csh) before this script runs,
# so all variables are already present in os.environ — no .env file needed.


###############
def sendemail(from_addr, to_addr_list, cc_addr_list,
                  subject, message,
                  login, password,
                  smtpserver='smtp.hermes.cam.ac.uk:587'):

    # smtpserver='smtp.gmail.com:587'):
    header = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Cc: %s\n' % ','.join(cc_addr_list)
    header += 'Subject: %s\n' % subject
    message = header + "\n" + message

    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login, password)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()
###############

if __name__ == '__main__':
    telescope = str(sys.argv[1])
    num_bad_files = str(sys.argv[2])
    
    # Get credentials from environment variables
    email_from = os.getenv('EMAIL_FROM', 'lcd44@cam.ac.uk')
    email_to = os.getenv('EMAIL_TO', 'lcd44@cam.ac.uk')
    smtp_login = os.getenv('SMTP_LOGIN', 'lcd44')
    smtp_password = os.getenv('SMTP_PASSWORD', 'noelia207')
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.hermes.cam.ac.uk:587')
    
    # Parse CC recipients if provided
    email_cc_str = os.getenv('EMAIL_CC', '')
    email_cc = [email.strip() for email in email_cc_str.split(',')] if email_cc_str else []
    
    sendemail(from_addr=email_from,
              to_addr_list=[email_to],
              cc_addr_list=email_cc,
              subject=str("Issue with transfer of files to ESO archive for " + telescope),
              message=str(num_bad_files + " files were not transferred to ESO archive for " + telescope),
              login=smtp_login,
              password=smtp_password,
              smtpserver=smtp_server)