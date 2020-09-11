# FamPay-YoutubeSearch

To goal is to make an API to fetch latest videos sorted in reverse chronological order of their publishing date-time from YouTube for a given tag/search query in a paginated response. 

## Here is how the basic requirements are met through in the project:

(1) The web application is supported via OAuth2.0 google authentication process. So to start with the app one needs to authorize the required permissions for generating respective access and refresh tokens. The tokens and other credentials are stored in the User database so that they can be continuously used to perform fetch tasks in the background.

(2) After proper authentication and authorizations are done, the async task for youtube api call every 10 secs is carried out using celery module of python/django ecosystem. For the scheduling work celery-beat module is used. The timely ordered responses are stored in the Video database with their respective fields. Also the background tasks are carried out such that every time new and the latest videos are fetched. This is done using the published_after field whose value is set to the published datetime of latest video.

(3) Storing part is done, in addition to this the app allows GET and Search api calls using a single API component. Without the search query, paginated response of all the latest videos will be shown. While for a particular search query (if passed) substring match is carried out in the titles as well as the description to get the respective video data in latest order.

(4) The app is supported by docker and docker-compose features so that it could be executed in any environment irrespective of local dependencies. All sorts of effective measures to make the tasks more optimal are taken during the implementation.

## To execute the application follow the instructions listed below:

Firstly clone the current project directory using the command: git clone https://github.com/sajaltikariha/FamPay-YoutubeSearch.git

A. If your system has docker and docker-compose already installed run the following commands in your linux based CLI:- 
(1) Enter the project directory using: cd project_directory_name 

(2) Enter docker up after build command to get container running: sudo docker-compose up -d --build 

(3) This must create a URL that can be copied to browser to inspect the app exposed at port 8000. Now go to "http://localhost:8000". 
(This might lead to SSL_ERROR_RX_RECORD_TOO_LONG error in firefox due to long response time, try changing "https" in the current url to "http")

(4) Now this will ask for user permissions, once allowed it will redirect a callback to "http://localhost:8000/oauth-callback" which sends a request to oauth2.0 server, where authentication code is exchanged with access and refresh tokens. The received credentials are stored in local User DB and used further to carry out background YT API fetch every 10 secs and store the obtained data in local Video DB. 

(5) After doing all the storing part its time to make api calls.

(6) Use "http://localhost:8000/api/videos" to fetch all the latest videos (paginated 10 per page).

(7) Use "http://localhost:8000/api/videos?query=search_query_to_look_for_in_videos" to fetch all the videos in response to the search query.

(8) Enter docker stop to stop the container: sudo docker-compose stop 
