/** Prettify JSON .*/
function prettifyJSON() {
    $.each( $('.prettify-json'), function() {
        var ugly = $(this).val();
        var obj = JSON.parse(ugly);
        var pretty = JSON.stringify(obj, undefined, 4);
        $(this).val(pretty);
        console.log(pretty);
    });
}


/** Populate value of radio buttons linked to text fields.*/
$('#answer-form').on('submit', function() {
    $('.radio-text-group').each(function() {
        var text = $(this).find('input[type=text]').val();
        $(this).find('input[type=radio]').val(text);
    });
});


$(document).ready(function() {
    prettifyJSON();
});