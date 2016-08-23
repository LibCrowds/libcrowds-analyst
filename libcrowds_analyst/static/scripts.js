/** Prettify JSON. */
function prettifyJSON() {
    $.each( $('.prettify-json'), function() {
        var ugly = $(this).val();
        var obj = JSON.parse(ugly);
        var pretty = JSON.stringify(obj, undefined, 4);
        $(this).val(pretty);
    });
}


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


/** Perform a Z39.50 search. */
function z3950Search(baseUrl, query, callback) {
    var url = (baseUrl + '/html').replace('//', '/');
    if (query.length === 0) {
        return;
    }
    $.ajax({
        type: 'GET',
        url: url,
        data: {query: query},
        success: function(results) {
            callback(results);
        }, error: function(err) {
            alert('Z3950 ERROR: ' + err.status + " " + err.statusText);
        }
    });
}
