function notify(msg, category){
    let title = category.charAt(0).toUpperCase() + category.slice(1);
    if (title === 'Danger') {
        title = 'Error';
    }

    let html = $(`<div class="alert alert-${category} fade">
                 <a class="close" data-dismiss="alert" href="#">&times;</a>
                 <h4>${title}</h4>
                 <p>${msg}</p>
                 </div>`);
    $('#alert-messages').append(html);

    window.setTimeout(function () {
        html.addClass("in");
    }, 300);
}