require([
    "jquery", "jhapi",
], function (
    $,
    JHAPI,
) {
    "use strict";

    var base_url = window.jhdata.base_url;
    var api = new JHAPI(base_url);

    $('.example-card button').click(function () {
        var el = $(this);
        var card = el.closest(".example-card");
        var image_name = card.find(".image-name").val().trim();
        var repo_url = card.find(".repo-url").val().trim();
        var path = card.find(".image-path").val().trim();
        var view_type = el.hasClass("btn-notebook") ? "notebook" : "voila";

        el.prop("disabled", true);

        $.post(base_url + "gallery", {
            image_name: image_name,
            repo_url: repo_url,
            path: path,
            view_type: view_type
        }, function (data) {
            console.log(data);
            window.location.replace(data.redirect);
        });
    });

    console.log(base_url);

});
