import psycopg2
from config import config
import requests

def get_urls(includelist,excludelist,showrecord,all):
    """ query parts from the parts table """
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("SELECT description, url FROM main.myurls where status=1")
        rows = cur.fetchall()
        print("The number of parts: ", cur.rowcount)
        mystr =""
        for eachkey in includelist:
            mystr += eachkey + "_"
        f = open("m3u_final\\Custom_" + mystr + "File.m3u","w+")
        for row in rows:
            wolf1 = True
            wolf = False
            for eachinc in includelist:
                if (not eachinc.lower() in str(row[0]).lower()):
                    wolf1 = False
            if wolf1 :
                for eachexc in excludelist:
                    if (eachexc.lower() in str(row[0]).lower()):
                        wolf = True
                if not wolf :
                    f.write(str(row[0]).strip()+"\n")
                    f.write(str(row[1]).strip() + "\n")
                    if showrecord:
                        print(str(row[0]).strip() + " " + str(row[1]).strip())
        f.flush()
        f.close()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

1
2
if __name__ == '__main__':
    #get_urls(["lig","tv","tr"],[],True,False) #Lig tv
    #get_urls(["tv8","tr"], ["MTV","IT","PARAGUAY","TV8.5"],True,False) #TV8
    #get_urls([],[],False,True) # For backup all records

    get_urls(["lt"],[],True,False) # bein fr 2
    #get_urls(["cartoon","tr"],["IT","ES:","FR","GR:","South","|AR|","DE:","NL-","PL:","|PT|","Kidzinia"],True,False)
    get_urls(["bein","sports"],[],True,False)
    get_urls(["bein", "sports","tr"], [], True, False)
    get_urls(["sky", "sports"], [], True, False)
    get_urls(["bt", "sports"], [], True, False)
    get_urls(["fox", "sports"], [], True, False)
    get_urls(["eurosport"], [], True, False)
