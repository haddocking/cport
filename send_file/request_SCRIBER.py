import time
import regex as re
import mechanicalsoup as ms
from urllib import request

scriber_url = "http://biomine.cs.vcu.edu/servers/SCRIBER/"
# placeholder FASTA code for 1PPE chain E
FASTA_identifier = ">1PPE_1|Chain A[auth E]|TRYPSIN|Bos taurus (9913)"
FASTA_code = "IVGGYTCGANTVPYQVSLNSGYHFCGGSLINSQWVVSAAHCYKSGIQVRLGEDNINVVEGNEQFISASKSIVHPSYNSNTLNNDIMLIKLKSAASLNSRVASISLPTSCASAGTQCLISGWGNTKSSGTSYPDVLKCLKAPILSDSSCKSAYPGQITSNMFCAGYLEGGKDSCQGDSGGPVVCSGKLQGIVSWGSGCAQKNKPGVYTKVCNYVSWIKQTIASN"
mail_address = "a.a.w.vandennieuwendijk@students.uu.nl"  # should be changed to a specially created mail

# to allow for multiple requests, a list should be implemented as input, but server only allows for 10 at a time
# so should split the list in subsets of 10 and check if the list is empty after every run, if not add new subset to queue

FASTA_comb = FASTA_identifier + "\n" + FASTA_code
error_msg = True

browser = ms.StatefulBrowser()
browser.open(scriber_url)
form_FASTA = browser.select_form(nr=0)
form_FASTA.set(name="seq", value=FASTA_comb)
form_FASTA.set(name="email1", value=mail_address)
browser.submit_selected(btnName="Button1")

# this section is to allow for browser.refresh without continually sending the same request
links = browser.links()
new_url = re.search(
    r"(http:.*)\"", str(links)
)  # selects first link, which directs to result page
print(
    "Run URL: " + new_url[1]
)  # selects first match group, as the whole match contains a final " in the url
browser.open(new_url[1])

sleep = 0
while (
    sleep < 600
):  # SCRIBER is rather fast so runs should take no longer than 10 minutes for single entries, re-evaluate for multiple requests
    if (
        re.search(r"(http:.*csv)", str(browser.page)) != None
    ):  # checks for the .csv download link, only there if the run is finished
        sleep = 700
        print("Results are ready")
        error_msg = False
    else:
        time.sleep(10)  # server only refreshes every 10 seconds
        sleep += 10
        print("Waiting for ", sleep, " seconds")
        browser.refresh()  # without the refresh it does not detect the new .csv when its added

if error_msg:
    print("Expected server time-out due to time it takes for results to be available")

download_link = re.search(r"(http:.*csv)", str(browser.page))[0]
print(download_link)


# replace path to be functional on local machine
# had to use request instead of mechanicalsoup due to link issues
request.urlretrieve(
    url=download_link,
    filename="/Users/aldovandennieuwendijk/Documents/CPORT/test_output_requests/test_SCRIBER.csv",
)

# at this location the check for the empty request list should be implemented

browser.close()
