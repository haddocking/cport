import time
import regex as re
import mechanicalsoup as ms

#replace with input
url = "https://wenmr.science.uu.nl/whiscy/"
pdb_name = "1PPE"
chain_id = "E"
align_type = "FASTA"

error_msg = True

browser = ms.StatefulBrowser()
browser.open(url)
form = browser.select_form(nr = 1)
form.set(name = "pdb_id", value = pdb_name)
form.set(name = "chain", value = chain_id)
form.set(name = "hssp_id", value = pdb_name)
form.set(name = "alignment_format", value = align_type)
browser.submit_selected(btnName = "submit")

page_text = browser.page
page_text_list = str(page_text.find_all("p"))

#https://regex101.com/r/rwcIl8/1
new_url = re.findall(r"(https:.*)\"", page_text_list)[0] 
print("Run URL: ", new_url)
browser.open(new_url)

sleep = 0
while sleep < 600:
    if browser.page.find_all(id = "active_list"):
        sleep = 700
        print("Results are ready")
        error_msg = False
    else:
        time.sleep(5)
        sleep += 5
        print("Waiting for ", sleep, " seconds")
        browser.refresh()

if error_msg: #if program gets here without having disabled error_msg something is likely wrong
    print("Expected server time-out due to time it takes for results to be available")
   
active_residues =  browser.page.find_all(id = "active_list")
passive_residues = browser.page.find_all(id = "passive_list")

browser.close()

#takes just the residue lists from the page and splits them into lists
active_residues_list = re.split(r"\,", re.search(r"\">(.*)</", str(active_residues))[1])
passive_residues_list = re.split(r"\,", re.search(r"\">(.*)</", str(passive_residues))[1])

print(active_residues_list)
print(passive_residues_list)
