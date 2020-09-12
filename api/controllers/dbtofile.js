require('../data/db-connector');
const fs = require('fs');
var path = require('path');
var mongoose = require('mongoose');
var Transcripts = mongoose.model('Transcript');

Transcripts.find().exec(function(err,transcripts){
    if(err){
        console.log("Error getting transcripts");
        res.status(500).json(err);
    }
    else{
        console.log("Found Transcripts",transcripts.length);
        let data = JSON.stringify(transcripts);
        fs.writeFileSync(path.join(__dirname,'../data/transcript_data.json'),data);
    }
})
