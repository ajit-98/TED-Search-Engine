var mongoose = require('mongoose');
var Transcripts = mongoose.model('Transcript');
var md5 = require('md5');
const {spawn} = require('child_process');
const queryEval = spawn('python',['./api/python-scripts/search.py'],{stdio:'inherit'});
var amqp = require('amqplib/callback_api');
const { query, response } = require('express');
const { sleep } = require('sleep');
var ch = null;
var searchResultsCache = {};
amqp.connect('amqp://localhost',function(err0,connection){
    if(err0){
        throw err0;
    }
    connection.createChannel(function(err1,channel){
        if(err1){
            throw err1;
        } 
        ch = channel;
        ch.assertExchange('ProcQuery',"direct",{
            durable:false
        });
        ch.assertQueue("Query",{
            durable:false
        });
        ch.assertQueue("DocList",{
            durable:false
        });
        ch.bindQueue("Query",'ProcQuery','Send');
        ch.bindQueue("DocList","ProcQuery",'Recieve');
        ch.consume('DocList',function(doclist){
            console.log("Recieved data from Python")
            var searchResult = JSON.parse(stringFromUTF8Array(doclist.content))
            var query = md5(searchResult["query"]);
            console.log(query);
            if(Object.keys(searchResultsCache).length == 200){
              searchResultsCache = {}
            } 
            searchResultsCache[query] = searchResult["docList"];
          
        });
    });
});

function stringFromUTF8Array(data)
{
  const extraByteMap = [ 1, 1, 1, 1, 2, 2, 3, 0 ];
  var count = data.length;
  var str = "";
  
  for (var index = 0;index < count;)
  {
    var ch = data[index++];
    if (ch & 0x80)
    {
      var extra = extraByteMap[(ch >> 3) & 0x07];
      if (!(ch & 0x40) || !extra || ((index + extra) > count))
        return null;
      
      ch = ch & (0x3F >> extra);
      for (;extra > 0;extra -= 1)
      {
        var chx = data[index++];
        if ((chx & 0xC0) != 0x80)
          return null;
        
        ch = (ch << 6) | (chx & 0x3F);
      }
    }
    str += String.fromCharCode(ch);
}

return str;
};



module.exports.getSearchResults = function(req,res){
    if(!Object.keys(searchResultsCache).includes(md5(req.query.q))){
      ch.publish("ProcQuery",'Send',Buffer.from(req.query.q));
      console.log('Node sent message to Python');
      res.status(200).json({"repeatRequest":'1',"Query":md5(req.query.q)});
    }
    else{
      var query=md5(req.query.q);
      var docIDs = [] 
      var len = searchResultsCache[query].length;
      if(len == 0){
        res.status(200).json({"repeatRequest":"0","searchResults":[]})
      }
      else{
        for(i=0;i<len;i++){
          docIDs.push(mongoose.Types.ObjectId(searchResultsCache[query][i]));
        }
        Transcripts.aggregate([
          {$match: {"_id": {$in: docIDs}}},
          {"$addFields" : { "__order" : { "$indexOfArray" : [docIDs, "$_id" ]}}},
          { "$sort" : { "__order" : 1 }}

         ]).exec(function(err,docs){
           if(err){
            res.status(500).json("Could not find documents related to search");
           }
           else{
             res.status(200).json({"repeatRequest":'0',"searchResults":docs})
           }
         });
      }

    }

}



module.exports.dispSearchResults = function(req,res){
  var query = req.params.query;
  var docIDs = [] 
  var len = searchResultsCache[query].length;
  for(i=0;i<len;i++){
    docIDs.push(mongoose.Types.ObjectId(searchResultsCache[query][i]));
  }
  Transcripts.aggregate([
    {$match: {"_id": {$in: docIDs}}}
   ]).exec(function(err,docs){
     if(err){
      res.status(500).json("Error Finding Hotels");
     }
     else{
       res.status(200).json(docs)
     }
   });


};