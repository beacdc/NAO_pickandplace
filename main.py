# -*- coding: cp1252 -*-
import portalocker
import time
import actions

def main():
    try:    
        while True:
            try: #Try to open status file
                with open('status.txt', 'w') as s: 
                    lock_flags = portalocker.LOCK_EX | portalocker.LOCK_NB
                    portalocker.lock(s, lock_flags) #Lock status file
                    try:
                        with open('comando.txt', 'r') as c: #try to open command file
                            getc = c.readline()
                            print "Reading command file"
                            print (getc) #Print command
                            if getc != None:
                                cmd = 'actions.%s' % getc
                                result = eval(cmd) #Run command
                                print (result) #Print result
                                s.write(str(result)) #Write result
                                print "Writing on status file"
                    except IOError: #If command is occupied wait 1 sec
                        time.sleep(1)
            except IOError: #If status file cannot be opened
                print "Status is busy"
                time.sleep(1)
    except KeyboardInterrupt:
        print "Interrupted by user"
        print "Stopping..."
        actions.rest()
    except Exception as e: #If any other error
        print e
        print "Stopping..."
        actions.rest()

if __name__== "__main__":
  main()
