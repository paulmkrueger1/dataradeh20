
# Knowledge Base V0.1

## Data Locations and Info:

### Events

Events are everything a user does, from opening the app to receiving a push notification to selecting a screenshot to shop.  Easily our largest dataset, we send the data to two databases:
 * **Amplitude**: Contains all event data for the app.
     * Useful for Dashboards that Mark and Molly track.  Console can be found <a href="https://analytics.amplitude.com/screenshop/">here</a>.
     * We (thanks jake!) load the data into a Google BigQuery table found <a href="https://bigquery.cloud.google.com/table/manymoons-215635">here</a>.
 * **Appsee**: Contains all event data for the app.  
     * They have an API.
         * For example, the sessions endpoint is: https://api.appsee.com/sessions. 
         * Documentation can be found here: https://www.appsee.com/docs/serverapi.
 * The same event data is sent to both Amplitude and Appsee.  Appsee is slightly more real-time than Amplitude.  The data is sent using <a href="https://bitbucket.org/craze_app/screenshotter/src/08.04/screenshot/Singletons/Analytics.swift">this script</a>. 
 * We have some functions to access both Appsee and Amplitude events <a href="https://github.com/ScreenShopIt/dataradeh20/blob/jake_dev/dataradeh/io/readers.py">here</a>.
 
 Each event has a unique name that has an associated .yaml file, which includes a description of the event, <a href="https://bitbucket.org/craze_app/analytics-client/src/master/events/">here</a>.
 
 
 
### Products
Our current product feed is located in the **Porsche** MySQL database that can be found on AWS at http://porsche.cjg1qmasgmy9.us-east-1.rds.amazonaws.com/.  We receive our product feed from 3 affiliates:
 * CJ
 * Linkshare
 * Awin
 * Each merchant only partners with one affiliate, the combination of merchant id and affiliate id is unique.
     * Documentation for the downloaders for the above three merchants can be found <a href="https://bitbucket.org/craze_app/porsche/src/master/downloaders/">here</a>. 
     * A cron job runs 4 times a day to check all three affiliates to see if there are any new products available, any changes to existing prices, any old products to delete etc.
 
 DynamoDB: [TODO]
 
### Users

We additionally use Google **FireBase** database and storage:
 * The  <a href="https://console.firebase.google.com/u/1/project/screenshop-73386/database">database</a> is a real-time snapshot of current users with their current screenshots and other timely data.
 * The <a href="https://console.firebase.google.com/u/1/project/screenshop-73386/storage/screenshop-73386.appspot.com/files">storage</a> part of firebase stores all historical user screenshots by user_id. 
 
We currently **do not** cache the product results of sending a screenshot/natural image to Syte.  The next priority will be hitting syte with all historical screenshots and storing the results.
