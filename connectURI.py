import requests
import sys
import json


def loginToAnypoint(url1,username,password):
    r = requests.post(url1,json={"username":username,"password":password},verify=False)
    print(r.status_code)
    jsoncontent=r.json()
    token_type=jsoncontent['token_type']
    access_token=jsoncontent['access_token']
    print("Token Type=%s, Access Token=%s"%(token_type,access_token))
    return token_type,access_token

def getTheOrgs(url2,tt,at,org1):
    r = requests.get(url2,headers={'Authorization': tt+" "+at},verify=False)
    jsoncontent=r.json()
    memorgs=jsoncontent['user']['memberOfOrganizations']
    orgid=""
    for member in memorgs:
        if (member['name']==org1):
            orgid=member['id']
    print("Organisation ID=%s"%(orgid))
    return orgid

def getTheEnv(url3,tt,at,env1):
    r = requests.get(url3,headers={'Authorization': tt+" "+at},verify=False)
    jsoncontent=r.json()
    envdata=jsoncontent['data']
    envid=""
    for env in envdata:
        if (env['name']==env1):
            envid=env['id']
    print("Environment ID=%s"%(envid))
    return envid

def getTheRegToken(url4,tt,at,envid,orgid):
    r = requests.get(url4,headers={'Authorization': tt+" "+at,'X-ANYPNT-ENV-ID':envid,'X-ANYPNT-ORG-ID':orgid},verify=False)
    jsoncontent=r.json()
    regtoken=jsoncontent['data']
    print("Registration Token=%s"%(regtoken))
    return regtoken

def main(argv):
    mainurl='https://xxxx.xxxx.xxxx.xxxx'
    url1=mainurl+'/accounts/login'
    url2=mainurl+'/accounts/api/me'
    username="xxxx"
    password="xxxx"
    orgname="xxxx"
    envname="xxxx"
    tt,at = loginToAnypoint(url1,username,password)
    myorgid=getTheOrgs(url2,tt,at,orgname)
    url3=mainurl+'/accounts/api/organizations/'+myorgid+'/environments'
    myenvid=getTheEnv(url3,tt,at,envname)
    url4=mainurl+'/hybrid/api/v1/servers/registrationToken'
    getTheRegToken(url4,tt,at,myenvid,myorgid)


    return 0

if __name__ == "__main__":
        main(sys.argv[1:])
