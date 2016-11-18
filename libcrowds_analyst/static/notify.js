function notify(msg){
    let html = $(`<div class="alert alert-${category} fade">
                 <a class="close" data-dismiss="alert" href="#">&times;</a>${msg}
                 </div>`);
    $('#alert-messages').append(html);

    window.setTimeout(function () {
        html.addClass("in");
    }, 300);
}