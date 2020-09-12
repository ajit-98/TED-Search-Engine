require('./api/data/db-connector');
var express = require('express');
var path = require('path');
var app = express();
var routes = require('./api/routes');
var bodyParser = require('body-parser');
app.set('port',3000);
app.use(express.static(path.join(__dirname,'public')));
app.use('/node_modules',express.static(path.join(__dirname,'node_modules')));
app.use(bodyParser.urlencoded({extened : false}));
app.use(bodyParser.json());
app.use('/api',routes);

var server = app.listen(app.get('port'),function() {
    console.log("Welcome to the TED Search Engine");
});

