import glob
import requests
import os
import time
import psycopg2
from config import config

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def get_urls(myurl):
    retval = False
    """ query data from the vendors table """
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("SELECT description, url FROM main.myurls WHERE url = %s",(myurl,))
        #print("The number of urls: ", cur.rowcount)
        row = cur.fetchone()

        while row is not None:
            #print(row)
            retval = True
            row = cur.fetchone()

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return retval


def insert_url(info,url):
    """ insert a new vendor into the vendors table """
    sql = """INSERT INTO main.myurls (description,url)
             VALUES(%s,%s);"""
    conn = None
    vendor_id = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql, (info,url,))
        # get the generated id back
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def iteratemyfiles():
    myfilelist = []
    for filename in glob.glob('Z:\\*.m3u'):
        with open(filename) as f:
            print(filename)
            lines = f.read().splitlines()
            streambegin = False
            urlreceived = False
            for eachline in lines:
                if "EXTINF" in eachline:
                    streambegin = True
                    streaminfo = eachline
                    continue
                if streambegin and ("http" in eachline):
                    streamurl = eachline
                    streambegin = False
                    urlreceived = True
                    continue
                if urlreceived and not streambegin:

                    #time.sleep(10)
                    #try:
                    #    r = requests.get(streamurl)
                    #except Exception as e:
                    #    print(e)
                    #    print(r.status_code)
                    #if (r.status_code==200):
                        doesurlexist = get_urls(streamurl)
                        if doesurlexist:
                            print("Record already there!!!")
                        elif not doesurlexist:
                            print("Inserting new url")
                            insert_url(streaminfo,streamurl)
                     #   print(streaminfo + " " + streamurl + " Status : 200 ")
        os.remove(filename)

def main():
    iteratemyfiles()

if __name__ == '__main__':
    main()
