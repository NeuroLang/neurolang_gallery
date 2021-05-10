require([
    "jquery", "jhapi",
  ], function(
    $,
    JHAPI,
  ) {
    "use strict";
  
    var base_url = window.jhdata.base_url;
    var api = new JHAPI(base_url);

    $('.launch-item').click(function() {
        var el = $(this);
        var image_name = el.find(".image_name").val().trim();
        var repo_url = el.find(".image_repo_url").val().trim();
        var path = el.find(".image_path").val().trim();
        console.log(image_name);
        console.log(repo_url);
        console.log(path);
        api.api_request("environments", {
            type: "POST",
            data: JSON.stringify({
              repo: repo,
              ref: ref,
              name: name,
              memory: memory,
              cpu: cpu,
              username: username,
              password: password,
            }),
            success: function() {
              window.location.reload();
            },
          });
    });
  
    console.log(base_url);
  
  });
  