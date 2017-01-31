#!/usr/bin/python
#!/usr/bin/env python
# This is the daemon for the mith-ren project
# Requires: python-daemon
#

import os
import subprocess
import sys
import emailagent
import logging
import yaml

class MithrendFrontend():

    def __init__(self, email_agent):
        # This is the daemon which runs each module
        self.install_location = '/usr/share/mith-ren/app'
        self.capture_file='correlation.txt'
        self.email_agent = email_agent


    def display_start_menu(self):
        os.system("clear")
        print " "
        print "==               ,  ,,     ` `                     =="
        print "==           '  ||  ||     , ,                     =="
        print "== \\\/\\\/\\\ \\\ =||= ||/\\\  /'\\\ ,._-_  _-_  \\\/\\\  =="
        print "== || || || ||  ||  || || || ||  ||   || \\\ || ||  =="
        print "== || || || ||  ||  || || || ||  ||   ||/   || ||  =="
        print "== \\\ \\\ \\\ \\\  \\\, \\\ |/ \\\,/   \\\,  \\\,/  \\\ \\\  =="
        print "==             `      _/                           =="
        print ""
        print('Please enter the number of which action you wish Mithoren to perform.')
        print("[1] Start")
        print("[2] Stop")
        print("[3] Status")
        print("[4] View Logged Packets")
        print("[5] Follow Daemon")
        print("[6] Edit Config file")
        print("[7] Send a Report")
        print("[8] Exit\n\n\n\n\n")
        command = self.get_input()
        return command

    def display_prompt(self):
        # Different Functions of Mithrend.py
        print("\nMithren Menu:\n[1] Start [2] Stop [3] Status [4] View Logged Packets [5] Follow Daemon\n" \
              "[6] Edit Config file [7] Send a Report [8] Exit\n\n")
        command = self.get_input()
        return command

    def get_input(self):
        command = raw_input("> ")
        return command

    def gather_data_from_daemon(self):
        return "Here ya go, boss"

    def getDaemonStatus(self):
        daemon_status = "Unknown"
        try:
            daemon = subprocess.Popen(["systemctl", "is-active",  "mithren"], stdout=subprocess.PIPE, stderr= subprocess.PIPE)
            daemon_status, daemon_fail = daemon.communicate()
        except e:
            logger.debug('Could not retrieve status from system')
        return daemon_status


    def getDaemonPid(self):
        daemon_pid = "Unknown"
        daemon = subprocess.Popen(['systemctl show mithren --property="MainPID"'], shell=True, stdout=subprocess.PIPE, stderr= subprocess.PIPE)
        daemon_pid, daemon_pid_fail = daemon.communicate()
        return daemon_pid.split("=")[1]

    def startDaemon(self):
        status = self.getDaemonStatus()
        pid = "Unknown"
        if "active" in status:
            daemon = subprocess.Popen(["systemctl", "start",  "mithren"],stdout=subprocess.PIPE, stderr= subprocess.PIPE)
            daemon_start, daemon_fail = daemon.communicate()
            pid = self.getDaemonPid()
            print "Daemon started as pid %s" % pid
            logging.info('Daemon started, pid: %s')
        else:
            pid = self.getDaemonPid()
            print "Daemon is already running: PID is %s" % pid

    def stopDaemon(self):
        status = self.getDaemonStatus()
        if "inactive" in status:
            print "Daemon has already been already stopped"
        else:
            daemon = subprocess.Popen(["systemctl", "stop",  "mithren"],stdout=subprocess.PIPE, stderr= subprocess.PIPE)
            daemon_stop, daemon_fail = daemon.communicate()
            print "Daemon stopped"
            logging.info('Daemon stopped')


    def process_command(self, command):
        print "\n"
        # Start Daemon
        if command == "1":
            self.pid = self.startDaemon()

        # Stop Daemon
        elif command == "2":
            self.pid = self.stopDaemon()

        # Status of Daemon
        elif command == "3":
            status = self.getDaemonStatus()
            if "inactive" in status:
                print "Daemon has been stopped"
            else:
                pid = self.getDaemonPid()
                print "Daemon running as process %s" % pid


        # View Log
        elif command == "4":
            os.system("tail %s/%s" % (self.install_location,self.capture_file))

        # View Log Forever
        elif command == "5":

            print "Coming soon"
            #infinite loop of readlines()

        # Edit Config
        elif command == "6":
            try:
                os.system("vim %s/mithrend.conf" % self.install_location) ,
            except e:
                print "Oops, check the log"
                logging.error('Failed to execute config edit due to %s' % e)
            print "Make sure to restart the daemon to enable your changes"

        # Send Report
        elif command == "7":
            print "Sending email to ....."
            payload = self.gather_data_from_daemon()
            self.email_agent.set_message(payload)
            self.email_agent.send_email()

        # Exit
        elif command == "8":
            # good advice
            print "Remember to brush your teeth!"
            sys.exit()

        else:
            print('Invalid Command.')

    def run(self):
        command = self.display_start_menu()
        while True:
            self.process_command(command)
            command = self.display_prompt()





#TODO
# Deal with occaisional resource busy issue
# Move away from using files
#

if __name__ == '__main__':
    try:
        logging.basicConfig(filename='mithren-frontend.log',level=logging.DEBUG)
        logger = logging.getLogger()
    except IOError as error:
        print "Hey there, try running as root, we need some power for this baby to run"
        sys.exit()
    with open("mithrend.conf", 'r') as stream:
        try:
            config = yaml.load(stream)
            logger.debug("Successfully loaded configuration file")
        except yaml.YAMLError as exc:
            logger.warning("Could not read YAML File:%s" % exc)
            print "Please fix mithren-frontend.conf YAML file and restart the program"
            sys.exit()


    email_agent = emailagent.EmailAgent(logger, config)
    app = MithrendFrontend(email_agent)
    app.run()

#//TODO
# Make a process to follow logs
# Perhaps make it sort of nicely and slowly present information to the end user- using ...s and now sending sleeps
# Verify if dongle is attached
