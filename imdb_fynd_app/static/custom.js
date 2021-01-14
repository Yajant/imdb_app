$(document).ready(function(e) {

	// ----------
	// ----------
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
    

	// ----------
	// ----------    
	// var clicked;
	// $(".favorite").click(function(){
	// clicked = $(this).attr("name");

	// $.ajax({
	// 	  type : 'POST',
	// 	  url : "{{url_for('test')}}",
	// 	  contentType: 'application/json;charset=UTF-8',
	// 	  data : {'data':clicked}
	// 	});
	
	// });	

    // ----------
	// ----------
	// $('button').click(function(){
	// $('form').on('submit', function(event) {
	// 	var email = $('#email').val();
	// 	var pass = $('#password').val();

	// 	$.ajax({
	// 		// url: "/api/user/register",
	// 		url: "/register_enduser",
	// 		data: $('form').serialize(),
	// 		type: 'POST',
	// 		success: function(response){
	// 			console.log(response);
	// 			// window.location.href = "/register_enduser";
	// 			// event.preventDefault();
	// 			window.location.reload();
	// 		},
	// 		error: function(error){
				
	// 		}
	// 	});

	// ----------
	// ----------		
	// $("#SubmitMovie").click(function (event) {    		    	          			
	// 	var form = $('#movie_form');
	// 	var formData = new FormData(document.getElementById(form));

	// 	$.ajax({
	// 		url: '/movies', // point to server-side URL
	// 		dataType: 'json', // what to expect back from server
	// 		cache: false,
	// 		contentType: false,
	// 		processData: false,
	// 		data: formData,
	// 		type: 'post',
	// 		success: function (response) { // display success response				
	// 			// no need to parse the flask obj, as we are already sending pared data from jsonify
	// 			// var response = JSON.parse(response) 				
	// 			if (response.is_valid)
	// 			{										
	// 			console.log(response);
	// 			// window.location.href = "/movies";
	// 			}
	// 			else{					
	// 				$('#flash').append(flashMessage(response));
	// 				return;
	// 			}	
	// 		}, //end success function				
	// 	}); //end ajax call
	// 	return false;

	// }); //close jquery #uploadfilefunction	
		

}); //end jquery