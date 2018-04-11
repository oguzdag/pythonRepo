import os,sys,getopt
sys.path.insert(1, "/home/o17080/pyproject/pexpect-2.4")
import threading
import pxssh
import pexpect
import getpass
import time

if sys.version_info[0]<3:
    import ConfigParser as configparser
else:
    import configparser

def doOneHost(line,transferfiles,filestocopy,usertouse,destination,commandrun,passtouse,commandList,longRunningList,longrunningtimeout,seperatorchar):
	start_of_host_time=time.time()
	hostpass=line.split(seperatorchar)
	try:
		os.remove("output/"+hostpass[0]+".txt")
	except OSError:
		pass
	outputfile = open("output/"+hostpass[0]+".txt","w")
	print("HOST = "+hostpass[0])
	print("--------------------------------")
	outputfile.write("OPERATION for "+hostpass[0]+"\n")
	outputfile.write("--------------------------------\n")	
	if transferfiles=="True":
		print("File copy:")
		outputfile.write("File copy:\n")
		var_command="scp -r "+ filestocopy +" "+usertouse+"@"+hostpass[0]+":"+ destination
		print(var_command)
		outputfile.write(var_command+"\n")
		var_child = pexpect.spawn(var_command)
		i = var_child.expect(["assword:", pexpect.EOF],timeout=-1)
		if i==0: # send password
			var_child.sendline(hostpass[1])
			var_child.expect(pexpect.EOF,timeout=-1)
			print("Successful")
			outputfile.write("Successful")
		elif i==1:
			outputfile.write("Got the key or connection timeout")
			print("Got the key or connection timeout")
			pass
	if commandrun=="True":
		try:
			print("Login started")
			s = pxssh.pxssh()
			if passtouse=="True":
				s.login (hostpass[0], usertouse, hostpass[1])
			else:
				s.login (hostpass[0], usertouse)
			print("Login successful")
		except pxssh.ExceptionPxssh, e:
			print "pxssh failed on login."
			print str(e)
			
		for command in commandList:
			if command=="su -":
				print(command)
				s.sendline(command)
				i = s.expect("assword:",timeout=1)
				if i==0:
					s.sendline(hostpass[2])
			else:
				print(command)
				s.sendline(command)
				outputfile.write(command+"\n")
				if (command in longRunningList):
					s.prompt(timeout=float(longrunningtimeout))
				else:
					s.prompt(timeout=1)
				outputfile.write(s.before+"\n")
				print(s.before)	
		s.logout()
		print("--- %s seconds for host (%s) ---" % (time.time() - start_of_host_time,hostpass[0]))

	
class ThreadClass(threading.Thread):
    def __init__(self,line,transferfiles,filestocopy,usertouse,destination,commandrun,passtouse,commandList,longRunningList,longrunningtimeout,seperatorchar):
        super(ThreadClass, self).__init__()
        self.hostline = line
        self.transferfiles=transferfiles
        self.filestocopy=filestocopy
        self.usertouse=usertouse
        self.destination=destination 
        self.commandrun=commandrun
        self.passtouse=passtouse
        self.commandList=commandList
        self.longRunningList=longRunningList
        self.longrunningtimeout=longrunningtimeout
        self.seperatorchar=seperatorchar


    def run(self):
		doOneHost(self.hostline,self.transferfiles,self.filestocopy,self.usertouse,self.destination,self.commandrun,self.passtouse,self.commandList,self.longRunningList,self.longrunningtimeout,self.seperatorchar)
			
			
def main(argv):
        start_of_code_time=time.time()
        serverfile = ''
        commandfile = ''
    
        try:
                opts, args = getopt.getopt(argv,"hs:c:",["serverfile=","commandfile="])
        except getopt.GetoptError:
                print('commandExecutor.py -s <serverfile> -c <commandfile>')
                sys.exit(2)
        for opt, arg in opts:
                if opt == '-h':
                        print('commandExecutor.py -s <serverfile> -c <commandfile>')
                        sys.exit()
                elif opt in ("-s", "--serverfile"):
                        serverfile = arg
                elif opt in ("-c", "--commandfile"):
                        commandfile = arg
        if serverfile=="" or commandfile=="":
                print("Usage:")
                print('commandExecutor.py -s <serverfile> -c <commandfile>')
                sys.exit(2)
        config=configparser.RawConfigParser()
        config.read(commandfile)
        usertouse=config.get("general","user")
        passtouse=config.get("general","usepassword")
        multithread=config.get("general","multithread")
        seperatorchar=config.get("general","seperatorChar")
        longrunningtimeout=config.get("commands","longRunningTimeout")
        transferfiles=config.get("files","transfer")
        filestocopy=""
        destination=""
        if transferfiles=="True":
                filestocopy=config.get("files","filetocopy")
                destination=config.get("files","destination")
        commandrun=config.get("commands","commandrun")
        commandList=str(config.get("commands","commandlist")).splitlines()
        longRunningList=str(config.get("commands","longRunningCommandList")).splitlines()
		
        hostlist = [line.rstrip('\n') for line in open(serverfile)]
        if not os.path.exists("output"):
                os.mkdir("output")
	if multithread=="True":
		for line in hostlist:
			t = ThreadClass(line,transferfiles,filestocopy,usertouse,destination,commandrun,passtouse,commandList,longRunningList,longrunningtimeout,seperatorchar)
			t.start()
	else:
		for line in hostlist:
			doOneHost(line,transferfiles,filestocopy,usertouse,destination,commandrun,passtouse,commandList,longRunningList,longrunningtimeout,seperatorchar)
	print("--- %s seconds for code ---" % (time.time() - start_of_code_time))
if __name__ == "__main__":
        main(sys.argv[1:])
