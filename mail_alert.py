#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 16:56:38 2019

@author: laetitia
"""
import sys
import smtplib


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
    sendemail(from_addr='lcd44@cam.ac.uk',
              to_addr_list=['lcd44@cam.ac.uk'],
              cc_addr_list=[],
              subject=str("Issue with transfer of files to ESO archive for " + telescope),
              message=str(num_bad_files + " files were not transferred to ESO archive for " + telescope),
              login='lcd44',
              password='noelia207')