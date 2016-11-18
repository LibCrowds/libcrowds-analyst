/** Populate value of radio buttons linked to text fields. */
$('#answer-form').on('submit', function() {
    $('.radio-text-group').each(function() {
        var text = $(this).find('input[type=text]').val();
        $(this).find('input[type=radio]').val(text);
    });
});


/** Handle rejection of form. */
$('.reject-btn').on('click', function(evt) {
    $('.radio-text-group input[type=text]').val('');
    $('.radio-text-group input[type=radio]').val('');
    $('.radio-text-group input[type=radio]').prop('checked', true);
    $('#answer-form').submit();
    evt.preventDefault();
});


/** Handle click of a free text field. */
$('.radio-text-group input[type=text]').on('click', function(evt) {
    $(this).siblings('.input-group-addon')
           .find('input[type=radio]')
           .first()
           .prop('checked', true);
});


/** Add a record to the form. */
function addRecordToForm(recordElem) {
    console.log(recordElem);
    $(recordElem.children('div')[1]).remove();
    var oclcNum = $(recordElem.children('div')[0]).context.id;
    var baseUrl = 'https://www.worldcat.org/title/apis/oclc';
    $(recordElem.find('.title')[0]).wrapInner(`<a href="${baseUrl}/${oclcNum}" target="_blank" />`);
    var html = $(recordElem).html().replace('col-xs-8', '');
    $('input[value="'+ oclcNum +'"]').each(function() {
        $($(this).parents('.radio')[0]).append(html);
    });
}


/** Handle the results of a Z3950 search. */
function handleResults(results) {
    let parser = new DOMParser(),
        doc    = parser.parseFromString(`<html>${results}</html>`, "text/xml");
    $(doc).find('.z3950-record').each(function() {
        addRecordToForm($(this));
    });
}


/** Perform a Z39.50 search. */
function z3950Search(query) {
    if (query.length === 0) {
        return;
    }
    $.ajax({
        type: 'GET',
        url: '/z3950/search/oclc/html',
        data: {query: query},
        success: function(results) {
            handleResults(results);
        }, error: function(err) {
            alert(`Z3950 ERROR: ${err.status} ${err.statusText}`);
        }
    });
}


$(document).ready(function() {
    let query = $('label input[name="oclc"]').map(function(){
        return `(1,12)="${$(this).val()}"`;
    }).get().join('or');
    z3950Search(query);
});
