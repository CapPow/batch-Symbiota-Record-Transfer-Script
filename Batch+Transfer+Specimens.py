
# coding: utf-8

# ## A batch record transfer script for Symbiota portals using Python 3, Selenium, and ChromeDriver.
# - This script was created to facilitate a bulk transfer of records from one collection to another. 
# - The existing process expects user interaction for each record, which might be considered excessive beyond 50 records. 
# - This was created when a group of records was accidently accessioned under the wrong collection but it would also be useful when records are exchanged from one collection to another.
# - It could certinly be improved, but functions as of the date of creation (12/18/2017).
# - If it 'breaks' I expect the "Xpaths" are fragile with respect to changes in Symbiota. This could be improved with more refined element identification techniques. 
# - There are specific expected inputs explained below.
# 
# Calebadampowell@gmail.com

# In[1]:


import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import time


# ## Expected input:
# 
# This script expects a .CSV file formatted as the example below.
# 
# - Such a .CSV can be created at the time a transfer is recieved by using a HID barcode scanner and a spreadsheet program. 
# - The workflow may be such: scan the old code, tab into the next column, place the new code on top of the old one and scan it into the adjacent field.
# - Collection codes ("Doner\_Collection\_#", and "Reciever\_Collection\_#") are unique to the portal, if you don't know the codes you can contact your web master or I can help.
# - Once obtained, collection codes can be copied down the column (don't type this in for each entry!)

# In[6]:


failedToFind = pd.DataFrame()      #build a Dataframe for possible "failure" report
xferList = pd.read_csv('transferList.csv')
xferList.head(5)


# ## Chrome webdriver settings
# 
# Some values must be adjusted for this script to function on your computer. Look for the comments in the code to see which 3 need adjusted.

# In[3]:


#This path needs altered for the location of chrome's executable.
w = webdriver.Chrome(executable_path="C:/Users/JohnSmith/AppData/Local/Programs/Python/Python36/selenium/webdriver/chrome/chromedriver.exe")

url = 'http://sernecportal.org/portal/profile/index.php?refurl=/portal/index.php?'
w.get(url)
w.implicitly_wait(5)
username = w.find_element_by_id('login') #keep these here, they locate the appropriate fields
password = w.find_element_by_id("password")

#These need altered for the sign in credentials of an administrator of BOTH collections intending to transfer from and to.
username.send_keys('*******')  #username here instead of the *********
password.send_keys('*************') #Password here instead of the *************

w.find_element_by_name('action').click()
time.sleep(2)#this wait may not be necessary, but it seems wise to give chrome a moment to 'wake up' before giving it commmands.


# ## The business end:
# 
# This is the business end function of the script, I've attempted to comment at each important step so the process is clear and can be improved with minimum effort.

# In[4]:


def makeTransfer(row):
    donerCollNum = xferList.ix[row,'Doner_Collection_#']
    donerCatalogNumber = xferList.ix[row,'Doner_Cat_#']
    recieverCollNum = xferList.ix[row,'Reciever_Collection_#']
    recieverCatalogNumber = xferList.ix[row,'Reciever_Cat_#']
    
    try:   
        firstURL = 'http://sernecportal.org/portal/collections/list.php?db={}&catnum={}&page=1#'.format(donerCollNum,donerCatalogNumber)
        w.get(firstURL)
        w.implicitly_wait(2)
#Load record using the catalog number and collection id value
        occAddress = w.find_element_by_xpath('//*[@id="omlisttable"]/tbody/tr[2]/td[2]/div[1]/a').get_attribute('href')
#use occurence id (aka: coreid, id) to load the occurence editor window
        w.get(occAddress)
#click on "admin" tab
        w.find_element_by_xpath('//*[@id="ui-id-5"]').click()
        wait = WebDriverWait(w, 3)
        
        transferButtonXpath = '//*[@id="admindiv"]/fieldset[1]/form/div[2]/input[3]'
        wait.until(EC.element_to_be_clickable((By.XPATH,transferButtonXpath)))
#Set the transfer options (which collection it is going to and NOT to keep the record also in the doner collection)
        select = Select(w.find_element_by_name('transfercollid'))
        select.select_by_value(str(recieverCollNum))
        w.find_element_by_name('remainoncoll').click()
#click trnasfer
        w.find_element_by_xpath(transferButtonXpath).click()

#Swap to the new tab that was created
        w.switch_to.window(w.window_handles[1])
        w.implicitly_wait(2)     # I'm not sure if this wait must be called each time, or if it is a setting.
#identify the catalognumber field        
        catNumField = w.find_element_by_id('catalognumber')
#select all existing text
        catNumField.send_keys(Keys.CONTROL + "a")        
#replace it
        catNumField.send_keys(recieverCatalogNumber)
#click an arbitrary field to coerce the "save edits" button to enable.
        w.find_element_by_name('verbatimeventdate').click()
#scroll to bottom of page
        w.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#identify the save edits button.
        saveEditsButtonXpath = '//*[@id="editButtonDiv"]/input[1]'
#wait until it's clickable
        wait.until(EC.element_to_be_clickable((By.XPATH,saveEditsButtonXpath)))
#click it.
        w.find_element_by_xpath(saveEditsButtonXpath).click()
        w.implicitly_wait(2)
#destroy extra tab that was generated
        time.sleep(1)  #testing feature to be removed.
        w.find_element_by_name('verbatimeventdate').send_keys(Keys.CONTROL +'w')
        w.switch_to.window(w.window_handles[0])
        return 'Successfully Transfered {} to {}'.format(donerCatalogNumber,recieverCatalogNumber)
    except NoSuchElementException:       
        return 'Failed to Transfer {} to {}'.format(donerCatalogNumber,recieverCatalogNumber)


# ## Process handler and clean up:
# 
# This calls the makeTransfer function on each record in the CSV file and writes a report if any fail.

# In[5]:


for row in range(xferList.shape[0]):
    attempt = makeTransfer(row)
    print(attempt)
    if attempt.split(' ')[0] == 'Failed':
        failedToFind = failedToFind.append(xferList.iloc[[row]], ignore_index=True)

if failedToFind.shape[0] > 0:
    failedToFind.to_csv('Failed_To_Transfer_Report.csv',encoding='utf-8', index=False)

w.close()

