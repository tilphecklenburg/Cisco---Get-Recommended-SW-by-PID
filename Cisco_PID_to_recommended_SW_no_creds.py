import requests
import json
import sqlite3

'''references

https://apiconsole.cisco.com/oauth#clientcredentials

https://developer.byu.edu/docs/consume-api/use-api/oauth-20/oauth-20-python-sample-code

'''
#initialize variables and database connection
swsuggestionbaseurl='https://api.cisco.com/software/suggestion/v2/suggestions/software/productIds/'
pidlist = open("pid_list.txt")
pidlist=pidlist.read()
pidlist = pidlist.split("\n")
#c.execute("SELECT * FROM cmdb WHERE pid='N9K-C9336C-FX2-B2'")
#print(c.fetchone())

#pid=input("enter base pid for suggested version (examples: CISCO2811, N9K-C9336C-FX2-B2): ")

def generate_access_token():
	#generates and returns access token for API calls, using client_credentials oauth2 grant type
	token_url='https://cloudsso.cisco.com/as/token.oauth2'
	data = {'grant_type': 'client_credentials'}
	client_id='<ADD CLIENT ID FROM CISCO API CONSOLE HERE'
	client_secret='<ADD CLIENT SECRET FROM CISCO API CONSOLE HERE'
	access_token_response = requests.post(token_url, data=data, verify=True, allow_redirects=False, auth=(client_id, client_secret))
	tokens = json.loads(access_token_response.text)
	token = tokens['access_token']
	return token

def get_suggested_sw_by_pid(pid,access_token):
	#returns suggested software for pid provided, as well as full image file name
	conn = sqlite3.connect('cmdb.db')
	c = conn.cursor()
	pid=pid
	access_token=access_token
	url=swsuggestionbaseurl + str(pid)
	querystring = {"pageIndex":"1"}
	payload = ""
	headers = {
		'Authorization': "Bearer %s" % str(access_token),
		'cache-control': "no-cache",
		'Postman-Token': "01fafbd3-9b5f-411a-96b1-4972b1ff87b5"
		}
	response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
	versioninfo=json.loads(response.text)
	suggestedversion=(versioninfo["productList"][0]['suggestions'][0]['releaseFormat1'])
	#imagefilename=(versioninfo["productList"][0]['suggestions'][0]['images'][0]['imageName'])
	if suggestedversion != '':
		dbquerystring="INSERT INTO suggestedverbyplatform VALUES " +  "(" + "'" + pid + "'" + "," + "'" + suggestedversion + "'"  + ")"
		c.execute(dbquerystring)
		conn.commit()
		conn.close()
		print('queried Cisco for suggested software version and updated database with latest data on pid %s' % pid)
		return suggestedversion
	#else:
	#	print('unable to find suggested software version for PID specified (%s)' % pid)
		
def create_new_cmdb():
	conn = sqlite3.connect('cmdb.db')
	c = conn.cursor()
	c.execute("""CREATE TABLE suggestedverbyplatform (
				pid text,
				suggestedver text
				)""")
	
create_new_cmdb()
	
token=generate_access_token()

print("generating database of PID-to-suggested-software entries")

for pid in pidlist:
	get_suggested_sw_by_pid(pid,token)
	
print("database table 'suggestedverbyplatform' generated")