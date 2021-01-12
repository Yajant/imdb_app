$(document).ready(function(e) {

    var flashMessage = function(data) {
        html = '';
        if (data.type) {
            msg_category = data.type;
        } else {
            msg_category = "success";
        }

        html += '<div class="alert alert-' + msg_category + '"><a href="#" class="close" data-dismiss="alert">&times;</a>' + data.message + '</div>';
        return html;
    };

    $("#uploadfile").click(function() {

        var ins = document.getElementById('the-file').files.length;

        if (ins == 0) {
            $('#flash').append(flashMessage({
                'message': 'Select at least one file',
                'type': 'danger'
            }));
            return;
        }

        var fileInput = document.getElementById('the-file');
        var file = fileInput.files[0];
        var form_data = new FormData();
        form_data.append('file', file);

        $.ajax({
            url: '/upload_file/', // point to server-side URL
            dataType: 'json', // what to expect back from server
            cache: false,
            contentType: false,
            processData: false,
            data: form_data,
            type: 'post',
            success: function(response) { // display success response				
                // no need to parse the flask obj, as we are already sending pared data from jsonify
                // var response = JSON.parse(response) 				
                if (response.status) {
                    // If scrapper started show GIF loader and hide file upload content
                    $("#loading").show();
                    $("#loading_msg").show();
                    $("#loading_msg").css("display", "block");
                    $("#content").hide();

                    // Ajax view to check every X seconds if task is completed, the result of this view will determine if it should redirect or still wait for the download link.		        			        
                    $.ajax({
                        url: "/status/" + response.task_id + "/",
                        success: function(data) {
                            if ((data.state == 'SUCCESS') && (data.status == true)) {

                                console.log("SUCCESS@@@@@@@@@@@@@@@@@@@");
                                // If task complete render the download link view

                                $.ajax({
                                    url: "/render_download_link/",
                                    type: 'GET',
                                    success: function(data) {

                                        $("#loading").hide();
                                        $("#loading_msg").hide();
                                        $("#loading_msg").css("display", "none");
                                        $("#content").hide();

                                        console.log("Rendered download link");
                                        $('#download_link').html(data);
                                    },
                                });
                            } else {

                                $("#loading").hide();
                                $("#loading_msg").hide();
                                $("#loading_msg").css("display", "none");
                                // If there are some erros in scraper we display the message
                                console.log("pending-----------------------");
                                $('#flash').append(flashMessage(data));
                                return;
                            }
                        }, //end success 
                    }); //end ajax

                } else {
                    $('#flash').append(flashMessage(response));
                    return;
                }
            }, //end success function				
        }); //end ajax call
        return false;

    }); //close jquery #uploadfilefunction


    // $.ajax({
    // 	type: "post",
    //     url: '/upload_file',
    //     success: function(data) {
    //         console.log('get info');
    //         console.log(JSON.stringify(data, null, '   '));
    //         // $('#info').html(JSON.stringify(data, null, '   '));
    //         // $('#description').html(data['description']);
    //     }
    // });

}); //end jquery