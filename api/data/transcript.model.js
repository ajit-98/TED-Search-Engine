var mongoose = require('mongoose');

var transcriptSchema = new mongoose.Schema({
    transcript: String,
    url: String
});


mongoose.model('Transcript',transcriptSchema,'transcript')
