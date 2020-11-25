#
# Automatic Reporting for System Engineers (A.R.S.E)
# by Michal Minarik (mminarik@vmware.com)
# version 1.0
#

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import pandas as pd
import getpass

dateFormat = "%d.%m.%Y"

df = pd.read_excel('input.xlsx')

print('\nTasks to be reported:')
print('\n-----------------------------------------------')
print(df)
print('-----------------------------------------------\n')

username = getpass.getuser()
print('Your VMware username: ' + username)
password = getpass.getpass()

print('\n')
print('Your SFDC date format (default: ' + dateFormat +'):')
newDateFormat = input()

if newDateFormat != "":
	dateFormat = newDateFormat

# Open Firefox and start login to SFDC
browser = webdriver.Firefox()
wait = WebDriverWait(browser, 30)
browser.get('https://vmware.my.salesforce.com')

ssoButton = browser.find_element_by_xpath("//div[@id='idp_section_buttons']/button[2]")
ssoButton.click()

# Sign in using username/password to Workspace ONE
wait.until(EC.presence_of_element_located((By.ID, "username")))

usernameField = browser.find_element_by_id("username")
usernameField.send_keys(username)
passwordField = browser.find_element_by_id("password")
passwordField.send_keys(password)

signInButton = browser.find_element_by_id("signIn")
signInButton.click()

# Wait for complete SSO login to SFDC
wait.until(EC.title_is("Salesforce - Unlimited Edition"))

lightningNotificationDismissed = False

for index, row in df.iterrows():

	print("Processing task [" + str(index + 1) + "/" + str(len(df)) + "]")

	# Go to "non-lightning" new task creation form
	browser.get('https://vmware.my.salesforce.com/00T/e?retURL=%2Fapex%2FSFA_SEActivitiesTab&RecordType=01234000000QF7y&ent=Task')

	# Dismiss the SFDC switch to Lighning notification. The dialog popup blocks screen and automatic select does not work.
	if lightningNotificationDismissed is False:

		wait.until(EC.presence_of_element_located((By.ID, "lexNoThanks")))
		
		lightningNotificationQuestionButton = browser.find_element_by_id("lexNoThanks")
		lightningNotificationQuestionButton.click()

		wait.until(EC.presence_of_element_located((By.ID, "lexSubmit")))
		
		lightningNotificationCloseButton = browser.find_element_by_id("lexSubmit")
		lightningNotificationCloseButton.click()

		lightningNotificationDismissed = True

	# Fill the form
	usernameField = browser.find_element_by_id("tsk5")
	usernameField.send_keys(row.summary)

	usernameField = browser.find_element_by_id("tsk4")
	usernameField.send_keys(row.date.strftime("%d.%m.%Y"))

	linkToField = browser.find_element_by_id("tsk3")
	linkToField.send_keys(row.link_to)

	activityTypeSelect = Select(browser.find_element_by_id('00N80000004k1L2'))
	activityTypeSelect.select_by_value(row.type)

	statusSelect = Select(browser.find_element_by_id('tsk12'))
	statusSelect.select_by_value(row.status)

	workHoursField = browser.find_element_by_id("00N80000004k1Mo")
	workHoursField.send_keys(row.hours)

	# Submit
	submitButton = browser.find_element_by_xpath("/html/body/div[1]/div[3]/table/tbody/tr/td[2]/form/div/div[3]/table/tbody/tr/td[2]/input[1]")
	submitButton.click()

	# Wait for the form to be fully submited (TODO: Create some condition and remove the explicit wait)
	browser.implicitly_wait(10) # seconds

print("\nReporting in done!")
