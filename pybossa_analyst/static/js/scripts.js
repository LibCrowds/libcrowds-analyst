/** Show next/previous page. */
$('.change-page').on('click', function(evt) {
    const page   = $(this).data('page'),
          nextId = '#page-' + page;
    $('.page').hide();
    $(nextId).show();
    populateFinalAnswer();
    evt.preventDefault();
});


/** Populate value of final answer fields. */
function populateFinalAnswer() {
    $('.answer-group').each(function() {
        const key    = $(this).data('key'),
              answer = $('input[name="' + key + '-option"]:checked').val();
        $('input[name="' + key + '"]').val(answer);
    });
}


/** Populate oclc option fields. */
$('label input[name="oclc-option"]').each(function() {
    const oclcNum = $(this).val(),
          query   = '(1,12)=' + oclcNum;
    let def = $.Deferred();
    z3950Search(query, def);
    def.done(function(result) {
        handleResult(result, oclcNum);
    }).catch(function(err) {
        notify('Z3950 ERROR: ' + err.status + ' ' + err.statusText, 'danger');
    });
});


/** Return a link to a WorldCat record. */
function getWorldCatLink(oclcNumber) {
    const url = 'https://www.worldcat.org/title/apis/oclc/' + oclcNumber;
    return '<a href="' + url + '" target="_blank">View Full Record</a><br/>';
}


/** Handle the results of a Z3950 search. */
function handleResult(results, oclcNumber) {
    let parser = new DOMParser(),
        html   = '<html>' + results + '</html>',
        doc    = parser.parseFromString(html, "text/xml"),
        record = $(doc).find('#' + oclcNumber + ' p')[0],
        link   = getWorldCatLink(oclcNumber);
    $('#oclc-' + oclcNumber).append(record);
    $('#oclc-' + oclcNumber).append(link);
}


/** Perform a Z39.50 search. */
function z3950Search(query, deferred) {
    $.ajax({
        type: 'GET',
        url: '/z3950/search/oclc/html',
        data: {query: query},
        success: function(result) {
            deferred.resolve(result);
        }, error: function(err) {
            deferred.reject(err);
        }
    });
}
