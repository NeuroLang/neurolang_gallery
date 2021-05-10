require([
    "jquery", "jhapi",
], function (
    $,
    JHAPI,
) {
    "use strict";

    var base_url = window.jhdata.base_url;
    var api = new JHAPI(base_url);

    $('.launch-item').click(function () {
        var el = $(this);
        var image_name = el.find(".image-name").val().trim();
        var repo_url = el.find(".repo-url").val().trim();
        var path = el.find(".image-path").val().trim();

        $.post(base_url + "gallery", {
            image_name: image_name,
            repo_url: repo_url,
            path: path,
        }, function(data) {
            console.log(data);
          });
    });

    console.log(base_url);

});
