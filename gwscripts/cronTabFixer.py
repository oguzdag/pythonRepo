#!/usr/bin/python
import os,subprocess,sys,getopt



def main(argv):
    serverfile = ''
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

    hostlist = [line.rstrip('\n') for line in open(serverfile)]
    if not os.path.exists("output"):
        os.mkdir("output")

    for host in hostlist:
        try:
            os.remove("output/"+host+".txt")
        except OSError:
            pass
        outputfile = open("output/"+host+".txt","w")
        sshProcess = subprocess.Popen(['ssh','username@'+host],stdin=subprocess.PIPE,stdout = subprocess.PIPE,universal_newlines=True,bufsize=0)
        sshProcess.stdin.write("su -\n")
        sshProcess.stdin.write("password\n")
        sshProcess.stdin.write("crontab -l -u username\n")
        sshProcess.stdin.close()
        for line in sshProcess.stdout:
            outputfile.write(line)
        outputfile.close()
        outputfile = open("output/"+host+".txt","r")
        crontab=[]
        origcrontab=[]
        for line in outputfile:
            if not str(line).startswith("Last login:"):
                if str(line).strip() not in origcrontab:
                    origcrontab.append(line.strip())
                    if str(line).count("+10-exec") > 0:
                        crontab.append(str(line).strip().replace("+10-exec","+11 -exec"))
                    else:
                        crontab.append(str(line).strip())
        print(host)
        for entry in crontab:
            print(entry)
        sshProcess = subprocess.Popen(['ssh','username@'+host],stdin=subprocess.PIPE,stdout = subprocess.PIPE,universal_newlines=True,bufsize=0)
        sshProcess.stdin.write("su -\n")
        sshProcess.stdin.write("password\n")
        sshProcess.stdin.write("mkdir tmp\n")
        sshProcess.stdin.write("rm -f tmp/usercron\n")
        sshProcess.stdin.write("echo '" + crontab[0] + "' > tmp/usercron\n")
        for entry in crontab[1:]:
            sshProcess.stdin.write("echo '"+entry+"' >> tmp/usercron\n")
        sshProcess.stdin.write("crontab -u muleadm tmp/usercron\n")
        sshProcess.stdin.write("grep -q -F 'username' /etc/cron.allow || echo 'username' >> /etc/cron.allow\n")
        sshProcess.stdin.close()


if __name__ == "__main__":
    main(sys.argv[1:])
