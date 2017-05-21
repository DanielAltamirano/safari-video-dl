import json
import requests
import re
import urllib

# -------------- UPDATE INFORMATION ----------------------------------------
email = "---"
password = "---"
course_url = "intermediate-python-programming/9781491954935"
# --------------------------------------------------------------------------

safari_url = "https://www.safaribooksonline.com"
course_url = safari_url + "/library/view/" + course_url

session_requests = requests.session()

login_uri = safari_url + "/accounts/login/"
initial_fetch = session_requests.get(login_uri)

token = re.search('name=\'csrfmiddlewaretoken\' value=\'([^\']+)\'', initial_fetch.content).group(1)

payload = {
    "email": email,
    "password1": password,
    "is_login_form": "true",
    "dontchange": "http://",
    "csrfmiddlewaretoken": token
}

session_requests.post(
    login_uri,
    data=payload,
    headers=dict(referer=login_uri)
)

course_main_page = session_requests.get(
    course_url,
    headers=dict(referer=course_url),
    timeout=50
)

api_url = safari_url + re.search('data-api-url="([^"]+.html)', course_main_page.content).group(1)

chapter_json = session_requests.get(
    api_url,
    headers=dict(referer=api_url)
).content

filecount = 00

chapter_json = json.loads(chapter_json)
publisher_scripts = chapter_json['publisher_scripts']
wid = re.search('"wid": *"([^"]+)"', publisher_scripts).group(1)
ui_conf = re.search('"uiconf_id": *"([^"]+)"', publisher_scripts).group(1)
referenceId = re.search('"referenceId": *"([^-]+)', publisher_scripts).group(1)
manifest_url = "http://cdnapi.kaltura.com/html5/html5lib/v2.35/mwEmbedFrame.php?&wid=" + wid + "&uiconf_id=" + ui_conf \
       + "&flashvars[referenceId]=" + referenceId
manifest = session_requests.get(
    manifest_url,
    headers=dict(referer=api_url)
).content
package_data = json.loads(re.search('window.kalturaIframePackageData = ({.+?});', manifest).group(1))
playlist = (package_data['entryResult']['meta']['playlistContent']).split(',')
partnerId = package_data['entryResult']['meta']['partnerId']

for video in playlist:
    print "http://cdnapi.kaltura.com/p/" + str(partnerId) + "/sp/" + str(partnerId) + "00/playManifest/entryId/"\
          + str(video) + "/format/download/protocol/http/flavorParamIds/0"

# Performing a HEAD on the URLs provides the filename