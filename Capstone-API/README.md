# Commercial Building Energy Forecasting API

This projects aims to build a commercial building energy forecasting API. This will use data provided by NREL,
and try to forecast energy for a specified commercial building.

## API Introduction

The API used a model developed based on NREL commerical building data. It will post data to a mongo database hosted at port 27081.
Note that the mongo database installed must be Mongo 5 and plus, since timeseries db are used to store data. User can take a look at the "Forecast Test.postman_collection.json" file in test folder for the testing done in postman.  

The following are a set of request supported in the api:

- General:
	- ../: just to return welcome message for testing the api connection.  
 
- POST:
	- ../test: This will import the prepared dataset into mongo for testing purpose.  
	- ../historical : This will import the data in mongo directly. An example will be:  
		127.0.0.1:81/historical?is_batch=0	  
  	 	--param is_batch: Integer(1 or 0). The flag to differentiate if the imported will come in batch.
            	The expected body will be include the fields below with :  
                 		- time  
                 		- kW  
                 		- temperature  
                 		- humidity  
                 		- building_id  
                 		- county  
            if it is 1, the expected body should have the fields as an array. If it is 0, the expected value should be individual item.

	- ../historical/csv : This will import the data using csv file with a specified format. User can take a look at the files in test folder for the expected csv format. An example of the post will be:  
           127.0.0.1:81/historical/csv?file_type=0  
   		--param file_type: Even though for this command, all expecetd files are csv, however, the csv file may contain different informations.  
             For file_type=0, the expected csv file should contain energy information with timestamp and building id.  
             For file_type=1, the expected csv file should contain county and building relationship  
             For file_type=2, the expected csv file should contain county and weather information.  
- GET:
	- /county_building: This will get the expected county building relationship in mongodb. An example will be:  
		127.0.0.1:81/county_building  
	- /forecast: This will forecast building energy based on specified building and expected forecast days. An example will be:  
		127.0.0.1:81/forecast?buildList=[1447,25065,42606 ]&days_in_future=3&use_center=True  
  		 --param buildList: A list of building ids to forecast on.  
   		 --param days_in_future: Integer. The expected forecast days.  
   		 --param use_center: Boolean. It indicates if the use_center approach will be used. If False, it will be simply use default prophet package for forecasting. If True, it will first try to locate the cluster it belongs to, and use the center data to do forecast, which enables seasonality since the center data has a year's content, and could be repeated for multiple years for a overfitting approach.  

- DELETE:  
	- /cleardb: This is for testing purpose. It will delete everything in database. An example will be:  
		127.0.0.1:81/cleardb  


