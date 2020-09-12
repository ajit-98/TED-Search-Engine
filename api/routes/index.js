var express = require('express');
var router = express.Router();
var ctrlSearch = require('../controllers/search.controller');


router
    .route('/search')
    .get(ctrlSearch.getSearchResults);

router
    .route('/search/:query')
    .get(ctrlSearch.dispSearchResults);
module.exports = router