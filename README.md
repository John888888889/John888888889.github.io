# Finance
#### Video Demo: https://youtu.be/OKvs3aZRL0o
#### Description:
## Purpose
The main purpose of the project was to help the user take a bank statement and develop it into a table showing the monthly expenditures in each category given.


## Upload page
The first step is to 'upload' a CSV file of your bank statement into the database through the upload page.

#### How it works
I am currently using a file select input that allows users to drag a CSV file into it. This does mean that currently with the Codespaces version of the app you will need to first move the file to the "static" folder. The file is then read by python and inserted into budget.db. To cater to my needs some data provided by the bank is left out, such as the cheque column, or whether a transaction was done with Debit or Eftpos.

#### Issues that arose
For some of the developing process I decided to work on the project locally instead of through Codespaces. It was also at this time that I got round to streamlining some of the user interactions. For the upload page I used an absolute path to my downloads folder so that I am able to drag the file directly from the web browser downloads section that pops up once something is downloaded. However when it came to making it work for Codespace so that I could submit it, I decided it would be a better use of my time to polish other areas of the project considering the time restriction.


## Home / Index page
Next step is to categorise the transactions.

#### How it works
This page will show you all the transactions that have been inserted into the database. From here you can categorise a transaction. The 'Input category' section will show all the current categories and the list shall adjust according to what you type. If you submit with the check box next to the submit button ticked, it will create a rule to categorise all the transactions with the same Memo to the category specified.


## Edit page
You are able to manually create rules here for greater control. This is also where you are able to delete rules, categories and transactions.

#### How it works
There are three sections.
The first is the rules section at the top left of the page. Here you are able to specify what you would like to search in SQLite using the like function so that you are able to 'SELECT' all the transactions with the keyword in the memo; allowing you to automatically categorise a chain with multiple locations. This is also where the list of rules will be shown and where you are able to delete them with the corresponding X button.
The second section is on the top right corner and shows you all the categories and is where you are able to delete them.
The last is at the bottom and shows you all the transactions and is where you are able to delete them.

#### Issues that arose
I did not like that I either had to remember what the memo's were or go back and forth between the home and edit page in order to make rules. So I decided to add a the tick box which makes a basic rule from the home page; not only does this mean that I could possibly avoid making rules manually, but it could also help me make more efficient rules, since I will be able to see if there are commonalities between multiple rules that I could use to replace them with one.


## Overview
Finally you will be able to see the table, which will have each month as the column headers and each category as the row headers.

#### How it works
When this page is opened it retrieves all the months and categories to be used as headers. It also uses those values as part of the SELECT query to get the monthly expenditures within each category. Using a for loop inside a for loop, it gets all the monthly expenditures for a category, stores it in a dictionary and then does the same for the next category. It then builds the table row by row again.

#### Issues that arose
I initially wanted to have the categories being the column headers since I would have been able to fit them in one screen, unlike the months which would have required 'overflow: scroll'. While not a major issue, I did not like the standard scrollbar. But I thought that the columns being varying widths, to fit all the category names and accomodate for the longer ones, looked worse. So I decided to re-code it so that the months were the column headers and styled the scrollbar to better fit in while trying to make it obvious as a scrollbar.