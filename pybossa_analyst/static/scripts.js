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
            notify(`Z3950 ERROR: ${err.status} ${err.statusText}`, 'danger');
        }
    });
}


/** Check if a file is ready to download. */
function checkDownload(short_name, filename) {
    let url = `/${short_name}/download/${filename}/check`;
    $.ajax({
        url: url,
        dataType: "json",
        success: function(data) {
            if (data.download_ready) {
                $('#dl-btn').removeClass('btn-disabled');
                $('#dl-btn').addClass('btn-success');
                $('#dl-btn').removeProp('disabled');
                $('#loading-icon').hide();
                $('#loading-text').html('Download ready!');
            } else {
                setTimeout(function(){
                    checkDownload();
                }, 2000);
            }
        },
        error: function(err) {
            $('#loading-text').html('');
            $('#loading-icon').hide();
            notify(`DOWNLOAD ERROR: ${err.status} ${err.statusText}`, 'danger');
        }
    });
}


if ($('#dl-btn').length) {
    let short_name = $('#dl-btn').data('short_name'),
        filename   = $('#dl-btn').data('filename');
    checkDownload(short_name, filename);
}


if ($('label input[name="oclc"]').length) {
    let query = $('label input[name="oclc"]').map(function(){
        return `(1,12)="${$(this).val()}"`;
    }).get().join('or');
    z3950Search(query);
}
