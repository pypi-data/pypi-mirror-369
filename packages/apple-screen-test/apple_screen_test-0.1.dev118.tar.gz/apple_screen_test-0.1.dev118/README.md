# screen-test

**Introduction**
screen-test is intended to be a central repository for data used in UTS QA testing. This project hopes to remove the
need for hard-coded values to be used during testing and to allow for automatic refreshing of data to ensure the most
up-to-date values are being used.

The idea behind this project is that pre-created accounts can be access via a database to be loaded in for testing. The
information in these accounts like subscriptions, content, user preferences etc, is loaded in via APIs and the
refreshing of the data is done on a specific timeline. Tests use these accounts to source any data needed for test
values.

**Creating a local copy for screentest**

Database Security and Access
There are 2 Postgres Instances for the database.

1. Production
2. Development

Production is the main database to be used to pull data for testing.
Database structural changes should only be made once finalized in Development as this may cause breakage.

Development is for testing changes to the database structure like new tables and or table structure changes. If any
changes are made that you want to keep, make sure you add them to the Production database so all teams can
access the new version and update any functions that pull data to ensure the correct data is still being pulled
correctly.

**Miro Board for Current Code Structure**
This is a link to the Miro Board depicting the current code
structure: https://miro.com/app/board/uXjVIpbe5Ek=/?share_link_id=286903560339
Password : password

**Miro Board for Current Database Structure**
This is a link to the Miro Board depicting the current database
structure: https://miro.com/app/board/uXjVIperXsw=/?share_link_id=304375357206
Password: password

**Whisper Secrets**
All login information for the database access on Postgres is handled through Whisper secrets. Contact Divya Gurram to
get added to the green-room namespace and get access to the screen-test-db-credentials bucket.

1. Grab the pipeline id "aprn:apple:sdp:::rio-pipeline:...etc"
2. Go to Whisper and navigate to the green-room namespace Access tab
3. Add the pipeline address as a new access with a None role (Read Only) and don't forget to at the Bucket
   "screen-test-db-credentials" at the bottom

**How to Set Up Postico Access for Visualizing Database**
Use Postico to view the database values internally. Depending on your needs your account may have read-only access or
read and write access (if you need to overwrite the values in teh database).
Postico Installed:** Download and install Postico from: https://eggerapps.at/postico2/
After postico has downloaded, open and connect the database
Add a new server and enter the information below into the appropriate fields.
Connect to Database on PostGres

* **Host:** `screen-test-ase-uts-qa-db-song.postgres.db.aci.apple.com`
* **Port:** `5315`
* **Database:** `screentest`
* **User:** 'username' <---different depending on read or read/write access needs
* **Password:** 'password' <---different depending on read or read/write access needs
* **SSL Mode:** `Require`

Ensure the connection is successful by clicking the "test" button and then once you see a green check, click "connect"
to link the database to Postico.
You can view the tables in the database and run SQL queries from Postico.

On the top left of Postico in the SQL Query box, you can run a sample query like:

Select * from "Accounts";

This can double-check you have proper access to the database and all values are appearing normally.

**RECOMENDATION:** In the "Structure" tab on the bottom, you can view the structural information for a table (types,
column names etc). Do not change any of these values/types as it will break many elements of screen-test.

**ACCOUNTS**
Account information is currently stored in the screen-test database. Information stored includes the dsid, cid,
email, password, and protected status. Functionality is included to fetch and update each of these values for any given
account.
Accounts can also be created and written to the database using the Plato Client /Jubeo Key. Current Types of accounts
that can be created are:

- MLS MONTHLY
- MLS ANNUAL
- TV PLUS SUBSCRIBED
- TV PLUS UNSUBSCRIBED

**API Access**
APIs are used to create new accounts as needed and to pull any necessary data.
The access is handled in the AccountControl.AccountServices and plato_client files. Additional account
types/subscriptions should be added to the AccountServices file and examples for functions can be found in coffee-cake

**Automation/Data Refresh --> FUTURE GOAL**
Data from the database should be scanned on a weekly (daily?) basis prior to being used for testing. This should ensure
all accounts are active and test data is accurate. The cadence of the data refresh scan could be increased/decreased
depending on the frequency of updates. It is recommended the data refreshes be given enough time for all updates to flow
through to the database before it is used in testing.

