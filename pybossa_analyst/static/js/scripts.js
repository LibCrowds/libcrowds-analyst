/** Show next/previous page. */
$('.change-page').on('click', function(evt) {
    let page = $(this).data('page');
    $('.page').hide();
    $(`#page-${page}`).show();
    populateFinalAnswer();
    evt.preventDefault();
});


/** Populate value of final answer fields. */
function populateFinalAnswer() {
    $('.answer-group').each(function() {
        let key    = $(this).data('key'),
            answer = $(`input[name="${key}-option"]:checked`).val();
        $(`input[name="${key}"]`).val(answer);
    });
}


/** Populate oclc option fields. */
$('label input[name="oclc-option"]').each(function() {
    let oclcNum = $(this).val(),
        query   = `(1,12)=${oclcNum}`;
    z3950Search(query).then(function(result) {
        handleResult(result, oclcNum);
    }).catch(function(err) {
        notify(`Z3950 ERROR: ${err.status} ${err.statusText}`, 'danger');
    });
});


/** Add a record to the form. */
function addWorldCatLink(oclcNumber) {
    let baseUrl = 'https://www.worldcat.org/title/apis/oclc',
        oclcUrl = `<a href="${baseUrl}/${oclcNumber}" target="_blank" />`;
    $(`#oclc-${oclcNumber}`).find('.title').wrapInner(oclcUrl);
}


/** Handle the results of a Z3950 search. */
function handleResult(results, oclcNumber) {
    let parser = new DOMParser(),
        doc    = parser.parseFromString(`<html>${results}</html>`, "text/xml"),
        record = $(doc).find(`#${oclcNumber} p`)[0];
    $(`#oclc-${oclcNumber}`).append(record);
    addWorldCatLink(oclcNumber);
}


/** Perform a Z39.50 search. */
function z3950Search(query) {
    return new Promise(function(resolve, reject) {
        $.ajax({
            type: 'GET',
            url: '/z3950/search/oclc/html',
            data: {query: query},
            success: function(result) {
                resolve(result);
            }, error: function(err) {
                reject(err);
            }
        });
    });
}
