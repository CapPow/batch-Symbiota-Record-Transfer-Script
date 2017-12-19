## A batch record transfer script for Symbiota portals using Python 3, Selenium, and ChromeDriver.
- Use it, Adjust it, Improve it, at your own risk.
- Included are a python version of the script, as well as the HTML output of a jupyter notebook explaining it.
- This script was created to facilitate a bulk transfer of records from one collection to another. 
- The existing process expects user interaction for each record, which might be considered excessive beyond 50 records. 
- This was created when a group of records was accidently accessioned under the wrong collection but it would also be useful when records are exchanged from one collection to another.
- It could certinly be improved, but functions as of the date of creation (12/18/2017).
- If it 'breaks' I expect the "Xpaths" are fragile with respect to changes in Symbiota. This could be improved with more refined element identification techniques. 
- There are specific expected inputs explained below.

## Expected input:

This script expects a .CSV file formatted as the example below.

- Such a .CSV can be created at the time a transfer is recieved by using a HID barcode scanner and a spreadsheet program. 
- The workflow may be such: scan the old code, tab into the next column, place the new code on top of the old one and scan it into the adjacent field.
- Collection codes ("Doner\_Collection\_#", and "Reciever\_Collection\_#") are unique to the portal, if you don't know the codes you can contact your web master or I can help.
- Once obtained, collection codes can be copied down the column (don't type this in for each entry!)

Calebadampowell@gmail.com
