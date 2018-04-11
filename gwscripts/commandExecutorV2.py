import os,sys,getopt
sys.path.insert(1, "/home/d4017080/pyproject/pexpect-2.4")
import threading
import pxssh
import pexpect
import getpass
import time
import subprocess
import shlex

if sys.version_info[0]<3:
    import ConfigParser as configparser
else:
    import configparser

def correctOutput(fulltext,commandname):
	fulltext=fulltext.splitlines()
	cmdoutput=[]
	for line in reversed(fulltext):
		cmdoutput.append(line)
		if (commandname in line):
			break
	return reversed(cmdoutput)

def prepareVariables(mylist):
	myvars = []
	temp1 = mylist[1:-1]
	temp2 = temp1.split(",")
	for eachvar in temp2 :
		temp3 = eachvar.split("=")
		myvar = {temp3[0]:temp3[1]}
		myvars.append(myvar)
	return myvars
	
def convertCommand(varlist,command):
	newcommand = command
	for eachvar in varlist:
		for k,v in eachvar.iteritems():
			newcommand = newcommand.replace("@@"+k+"@@",v)
	return newcommand
	
		

def LCE(commandList):
	print("localCommandExecute : ")
	mycommand = "; ".join(commandList)
	os.system(mycommand[2:])
		
	
	
def LCEMgr(commandFile):
	config=configparser.RawConfigParser()
	config.read(commandFile)
	commandList=str(config.get("commands","commandlist")).splitlines()
	LCE(commandList)

def FCTR(hostname,username,userpass,src,dest):
	print("\t\tfileCopyToRemote")
	print("\t\tCopy file from ( " + src + " ) to ( " + dest + " ) on " + hostname )
	var_command="scp -r "+ src +" "+username+"@"+hostname+":"+ dest
	var_child = pexpect.spawn(var_command)
	i = var_child.expect(["assword:", pexpect.EOF],timeout=60)
	if i==0: # send password
		var_child.sendline(userpass)
		var_child.expect(pexpect.EOF,timeout=60)
		print("Successful")
	elif i==1:
		print("Got the key or connection timeout")
		pass	

def FCTRMgr(multithread,commandFile,hostFile,seperatorchar):
	config=configparser.RawConfigParser()
	config.read(commandFile)
	src = config.get("file","src")
	dest = config.get("file","dest")
	usr = config.get("file","user")
	origsrc = src
	origdest = dest	
	hostlist = [line.rstrip('\n') for line in open(hostFile)]
	if multithread=="True":
		threadlist=[]
		for line in hostlist:
			hostparams=line.split(seperatorchar)
			hostname=hostparams[0]
			userpass=hostparams[1]
			rootpass=hostparams[2]
			myvarlist=[]
			if (len(hostparams)>3):
				myvars=hostparams[3].strip()
				myvarlist = prepareVariables(myvars)	
			src = convertCommand(myvarlist,origsrc)	
			dest = convertCommand(myvarlist,origdest)				
			print("\tHostname = " + hostname )
			t = ThreadClassV2("FileCopyToRemote",hostname=hostname,username=usr,userpass=userpass,src=src,dest=dest)
			t.start()
			threadlist.append(t)
		for eachthread in threadlist:
			eachthread.join()		
	elif multithread=="False":
		for line in hostlist:
			hostparams=line.split(seperatorchar)
			hostname=hostparams[0]
			userpass=hostparams[1]
			rootpass=hostparams[2]
			myvarlist=[]
			if (len(hostparams)>3):
				myvars=hostparams[3].strip()
				myvarlist = prepareVariables(myvars)	
			src = convertCommand(myvarlist,origsrc)	
			dest = convertCommand(myvarlist,origdest)				
			print("\tHostname = " + hostname )
			FCTR(hostname,usr,userpass,src,dest)		
	

def RCE(commandList,hostname,myvarlist,username,userpass,rootpass,passworduse,longRunningList,longrunningtimeout):
	print("remoteCommandExecute")
	try:
		print("Login started")
		s = pxssh.pxssh()
		if passworduse=="True":
			s.login (hostname, username, userpass)
		elif passworduse=="False":
			s.login (hostname, username)
		print("Login successful")
	except pxssh.ExceptionPxssh, e:
		print "pxssh failed on login."
		print str(e)
		
	for command in commandList:
		if command=="su -":
			s.sendline(command)
			i = s.expect("assword:",timeout=1)
			if i==0:
				s.sendline(rootpass)
		else:
			origcommand=command
			command = convertCommand(myvarlist,command)
			s.sendline(command)
			if (command in longRunningList):
				s.prompt(timeout=float(longrunningtimeout))
			else:
				s.prompt(timeout=1)			
			cmdout=correctOutput(s.before,command)
			for line in cmdout:
				print(line)
	s.logout()	

def RCEMgr(multithread,commandFile,hostFile,seperatorchar):
	config=configparser.RawConfigParser()
	config.read(commandFile)
	print(commandFile)
	hostlist = [line.rstrip('\n') for line in open(hostFile)]	
	commandList=str(config.get("commands","commandlist")).splitlines()
	username=config.get("default","username")
	passworduse=config.get("default","passworduse")
	longrunningtimeout=config.get("commands","longRunningTimeout")
	longRunningList=str(config.get("commands","longRunningCommandList")).splitlines()
	if multithread=="True":
		threadlist=[]
		for line in hostlist:
			hostparams=line.split(seperatorchar)
			hostname=hostparams[0]
			userpass=hostparams[1]
			rootpass=hostparams[2]
			myvarlist=[]
			if (len(hostparams)>3):
				myvars=hostparams[3].strip()
				myvarlist = prepareVariables(myvars)	
			print("Hostname = " + hostname )
			t = ThreadClassV2("RemoteCommandExecute",commandList=commandList,hostname=hostname,varlist=myvarlist,username=username,userpass=userpass,rootpass=rootpass,passworduse=passworduse,longRunningList=longRunningList,longrunningtimeout=longrunningtimeout)
			t.start()
			threadlist.append(t)
		for eachthread in threadlist:
			eachthread.join()		
	elif multithread=="False":
		for line in hostlist:
			hostparams=line.split(seperatorchar)
			hostname=hostparams[0]
			userpass=hostparams[1]
			rootpass=hostparams[2]
			myvarlist=[]
			if (len(hostparams)>3):
				myvars=hostparams[3].strip()
				myvarlist = prepareVariables(myvars)			
			print("Hostname = " + hostname )
			RCE(commandList,hostname,myvarlist,username,userpass,rootpass,passworduse,longRunningList,longrunningtimeout)	
	

def FCFR(hostname,username,userpass,src,dest):
	print("fileCopyFromRemote")
	print("Copy file from ( " + hostname + " ) ( " + src + " ) to ( " + dest + " ) on localhost" )
	var_command="scp -r "+ username+"@"+hostname+":"+ src +" "+ dest
	var_child = pexpect.spawn(var_command)
	i = var_child.expect(["assword:", pexpect.EOF],timeout=60)
	if i==0: # send password
		var_child.sendline(userpass)
		var_child.expect(pexpect.EOF,timeout=60)
		print("Successful")
	elif i==1:
		print("Got the key or connection timeout")
		pass	
	
def FCFRMgr(multithread,commandFile,hostFile,seperatorchar):
	config=configparser.RawConfigParser()
	config.read(commandFile)
	print(commandFile)
	src = config.get("file","src")
	dest = config.get("file","dest")
	usr = config.get("file","user")
	origsrc = src
	origdest = dest
	hostlist = [line.rstrip('\n') for line in open(hostFile)]
	if multithread=="True":
		threadlist=[]
		for line in hostlist:
			hostparams=line.split(seperatorchar)
			hostname=hostparams[0]
			userpass=hostparams[1]
			rootpass=hostparams[2]
			myvarlist=[]
			if (len(hostparams)>3):
				myvars=hostparams[3].strip()
				myvarlist = prepareVariables(myvars)	
			src = convertCommand(myvarlist,origsrc)	
			dest = convertCommand(myvarlist,origdest)						
			print("\tHostname = " + hostname )
			t = ThreadClassV2("FileCopyFromRemote",hostname=hostname,username=usr,userpass=userpass,src=src,dest=dest)
			t.start()
			threadlist.append(t)
		for eachthread in threadlist:
			eachthread.join()		
	elif multithread=="False":
		for line in hostlist:
			hostparams=line.split(seperatorchar)
			hostname=hostparams[0]
			userpass=hostparams[1]
			rootpass=hostparams[2]
			myvarlist=[]
			if (len(hostparams)>3):
				myvars=hostparams[3].strip()
				myvarlist = prepareVariables(myvars)	
			src = convertCommand(myvarlist,origsrc)	
			dest = convertCommand(myvarlist,origdest)	
			print("\tHostname = " + hostname )
			#print("src = " + src + " , dest = " + dest)
			FCFR(hostname,usr,userpass,src,dest)	
	
class ThreadClassV2(threading.Thread):
	def __init__(self,stepName, **kwargs):
		super(ThreadClassV2, self).__init__()
		self.stepName=stepName
		self.commandFile=""
		self.hostname=""
		self.userpass=""
		self.rootpass=""
		self.src=""
		self.dest=""
		self.username=""
		self.rootpass=""
		self.commandList=""
		self.passworduse=""
		self.longRunningList=""
		self.longrunningtimeout=""
		self.varlist = []
		for key,value in kwargs.iteritems():
			if key=="src":
				self.src=value
			elif key=="dest":
				self.dest=value
			elif key=="hostname":
				self.hostname=value
			elif key=="userpass":
				self.userpass=value
			elif key=="username":
				self.username=value	
			elif key=="rootpass":
				self.rootpass=value			
			elif key=="commandlist":
				self.commandList=value								
			elif key=="passworduse":
				self.passworduse=value	
			elif key=="longRunningList":
				self.longRunningList=value								
			elif key=="longrunningtimeout":
				self.longrunningtimeout=value	
			elif key=="varlist":
				self.varlist = value
						
	def run(self):
		print("\tRunning Multithreaded")
		print("\tThread Started")
		time.sleep(3)
		if self.stepName=="FileCopyToRemote":
			FCTR(self.hostname,self.username,self.userpass,self.src,self.dest)
		elif self.stepName=="RemoteCommandExecute":
			RCE(self.commandList,self.hostname,self.varlist,self.username,self.userpass,self.rootpass,self.passworduse,self.longRunningList,self.longrunningtimeout)
		elif self.stepName=="FileCopyFromRemote":
			FCFR(self.hostname,self.username,self.userpass,self.src,self.dest)
		print("\tThread Finished") 

		
		
def runScenarioStep(stepName,stepNum,multithread,commandFile,hostFile,seperatorchar):
	print("---------------------------------------------------------")
	print("Running Scenario Step ( " + stepNum + " ) : " + stepName )
	print("---------------------------------------------------------")
	print("MultiThread = " + multithread)
	if stepName=="LocalCommandExecute":
		LCEMgr(commandFile)
	elif stepName=="RemoteCommandExecute":
		RCEMgr(multithread,commandFile,hostFile,seperatorchar)
	elif stepName=="FileCopyToRemote":
		FCTRMgr(multithread,commandFile,hostFile,seperatorchar)
	elif stepName=="FileCopyFromRemote":
		FCFRMgr(multithread,commandFile,hostFile,seperatorchar)


def main(argv):
	scenariofile = ''
	dryrun=False
	promptexists=False
	try:
		opts, args = getopt.getopt(argv,"hs:",["dry-run","prompt"])
	except getopt.GetoptError:
		print('GetOpt Error : commandExecutorV2.py -s <scenarioFile> [--prompt] [--dry-run]')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('Help : commandExecutorV2.py -s <scenarioFile> [--prompt] [--dry-run]')
			sys.exit()
		elif opt=="-s":
			scenariofile = arg
		if opt=="--dry-run":
			print("I am running a dry-run with file " + scenariofile)
			dryrun=True
			sys.exit()
		if opt=="--prompt":
			promptexists=True
	if scenariofile=="":
		print("Usage:")
		print('commandExecutorV2.py -s <scenarioFile> [--prompt] [--dry-run]')
		sys.exit(2)		
	config=configparser.ConfigParser()
	config.read(scenariofile)
	configsections=sorted(config.sections(), key=str.lower)
	print("Starting Scenario")
	seperatorchar=config.get("default","seperator")
	for eachsection in configsections:
		if eachsection=="default":
			configsections.remove(eachsection)	
	for eachsection in configsections:
		stepNum=eachsection[5:7]
		multithread = ""
		commandFile = ""
		hostFile = ""
		enabled = "" 
		stepName = ""
		description = ""
		for (eachkey,eachval) in config.items(eachsection):
			if eachkey=="multithread":
				multithread = eachval
			elif eachkey=="commandfile":
				commandFile=eachval
			elif eachkey=="hostfile":
				hostFile = eachval
			elif eachkey=="enabled":
				enabled = eachval		
			elif eachkey=="name":
				stepName =eachval
			elif eachkey=="description":
				description =eachval				
		if enabled=="True":	
			if promptexists :
				ans = True
				while ans:
					print("( STEP " + stepNum + " - " + stepName + " ) " + description)
					myans = raw_input("Do you want to continue to run ? [ y (yes) / N (Continue to Next Step) / X (Terminate) ] : ")
					if myans == "y" :
						runScenarioStep(stepName,stepNum,multithread,commandFile,hostFile,seperatorchar)
						ans = False
					elif myans == "X" :
						print("Terminating process!!!")
						sys.exit()
					elif myans == "N" :
						print("Skipped ( STEP " + stepNum + " - " + stepName + " ) now continue to next one")
						ans = False
					else :
						print("Please enter a valid option")
			else :
				runScenarioStep(stepName,stepNum,multithread,commandFile,hostFile,seperatorchar)
		
		
if __name__ == "__main__":
        main(sys.argv[1:])


