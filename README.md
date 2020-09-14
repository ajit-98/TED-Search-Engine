# TED-Search-Engine
<h1> What is it? </h1>
<p> A full text search engine to find TED talks, built using Python and MEAN Stack.</p>

<img src="gifs/frontend.gif" width="500">

<h1> How to use it </h1>
<ul>
  <li> Clone this repo and install all dependencies (listed below) </li>
  <li> cd to project directory and run the following commands </li>
  
  ```
  npm install #install all dependencies listed in package.json
  cd api/python-scripts 
  python createDB.py #insert video transcripts into mongoDB 
  ```
  <li> Open another command prompt and start a rabbitmq server </li>
  
  ```
  rabbitmq-server
  
  ```
  <li> Start the application with nodemon </li>
</ul>
 


