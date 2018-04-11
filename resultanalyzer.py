import psycopg2
from config import config
# This method for deleting uncommon file extensions

def get_urls():
    """ query parts from the parts table """
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("SELECT description, url FROM main.myurls ")
        rows = cur.fetchall()
        print("The number of parts: ", cur.rowcount)
        extensionarr = {}
        extensiongreater10 = []
        for row in rows:
            myurl = str(row[1]).strip()
            ext = myurl[myurl.rfind('.'):]
            if not ext in extensionarr.keys():
                extensionarr.update({ext:1})
            else:
                extensionarr[ext]+=1
        for eachkey,eachval in extensionarr.items():
            if eachval>10:
                extensiongreater10.append(eachkey)
        cur.execute("SELECT description, url FROM main.myurls ")
        rows = cur.fetchall()
        print("The number of parts: ", cur.rowcount)
        delcnt = 0
        for row in rows:
            myurl = str(row[1]).strip()
            ext = myurl[myurl.rfind('.'):]
            if (not ext in extensiongreater10):
                delcnt +=1
                #print("deleting url : " + myurl)
                cur.execute("DELETE FROM main.myurls WHERE url = %s", (myurl,))
                conn.commit()
        print("Delete count = " + str(delcnt))
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

1
2
if __name__ == '__main__':
    get_urls()
