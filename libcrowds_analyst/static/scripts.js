/** Prettify JSON .*/
function prettifyJSON() {
    $.each( $('.prettify-json'), function() {
        var ugly = $(this).val();
        var obj = JSON.parse(ugly);
        var pretty = JSON.stringify(obj, undefined, 4);
        $(this).val(pretty);
    });
}


/** Populate value of radio buttons linked to text fields.*/
$('#answer-form').on('submit', function() {
    $('.radio-text-group').each(function() {
        var text = $(this).find('input[type=text]').val();
        $(this).find('input[type=radio]').val(text);
    });
});


/** Perform a Z39.50 search.*/
function z3950Search(query, callback) {
    if (query.length === 0) {
        return;
    }
    $.ajax({
        type: 'GET',
        url: '/z3950/search/oclc/html',
        data: {query: query},
        success: function(results) {
            callback(results);
        }, error: function(err) {
            alert('Z3950 ERROR: ' + err.status + " " + err.statusText);
        }
    });
}


$(document).ready(function() {
    prettifyJSON();
});