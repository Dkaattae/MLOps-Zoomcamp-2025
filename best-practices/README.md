# best-practices
### step 1, refactoring
wrap code in functions, each function just does one job.     
if global variable are needed, put in environment variables, warpped in class

### step 2, unit test
install pytest, config vscode.   
write unit tests to test each function.   
if connecting to any serive, those connection should be put in callback functions   
for example, if the pipeline need to read data from database,   
database location should be a callback function. 
if in test, it is a mock database path. if in production, it is the real path. 
unit test should be in test_*.py or *_test.py inside tests/unit_test folder. 

### step 3, mocking cloud service
as mentioned above, any cloud services should be mocked to avoid any cost.   
using mock service in docker-compose file, export test api keys.   

### step 4, change callback functions
replace directly connection to callback logic in original code   

### step 5, integration test
create sample data inside mock database, and sample artifacts if used.
write result to mock database, and then read it from integration test   
according to step 4 logic, in test mode, pipeline should read sample data from mock database. 

### step 6, orchestrate using sh
write shell script to orchestrate above steps. 
making sure dockerized code could access mock database if needed. 
making sure environment variables are pass to docker containers. 

### step 7, linting and formatting 

### step 8, CI/CD