$(document).ready(function() {
	
	$("#id_username").keypress(function(evt){
		return acceptUsernameInput(this,evt);
	});

	$("#rad_rol").buttonset().change(function() {
		id = $('#rad_rol :checked').attr('id');
		if(id == 'rad_ver') {
			div_show_hide('div_ver', 'div_crear')
		} else if(id == 'rad_crear') {
			div_show_hide('div_crear', 'div_ver')
		}
	});

	$("#btn_new_user").click(function() {
		username = $('#username').val();
		password = $('#password').val();
		rol = $('#rol').val();
		email = $('#email').val();
		data = {
			'username' : username,
			'password' : password,
			'email' : email,
			'rol' : rol
		};

		ajax("/add_rol/", data, function(data) {
			if(data.status) {
				cadena = "<tr>" + data.id;
				cadena += "<td><button id='" + data.id + "' class='btn_transparent' onclick='javascript:edit('div_add','div_main',this)' title='Editar'><img src='/site_media/img/tool_add16.png'></button></td>';"
				cadena += "<td>" + username + "</td>";
				cadena += "<td>" + rol + "</td>";
				cadena += "<td><center><input id='' type='checkbox' /></center></td>";
				cadena += "</tr>";
				$("#grid").append(cadena);
			}
		}, 'div_add', 'div_ajax');
	});

	$("#btn_trash").click(function() {
		darray = "";
		array = new Array();
		$('#grid input:checked').each(function() {
			darray += $(this).attr('id') + ',';
			array.push($(this).attr('id'));

		});
		data = {
			'array' : darray
		};

		ajax("/del_rol/", data, function(data) {
			if(data.status) {
				for(i in array) {
					id = array[i];
					$("#" + id).remove();
				}

			}
		}, 'div_main', 'div_ajax');
	});
}); 



/**
 * Permite ingresar solamente letras minúsculas y números
 * 
 */
function acceptUsernameInput(input,evt){
	evt = (evt) ? evt : window.event;
	var charCode = (evt.which) ? evt.which : evt.keyCode;
	// Permite: letras 97: a, 122: z
	// Permite: números 48: 0, 57: 9 
	// Permite: borrar 8l, delete: 46
	// Permite: LeftArrownot Shift + : 37
	// Permite: RightArrow: 39 and .
	// Permite: TAB: 9
	if((charCode>=48 && charCode<=57) || (charCode>=97 && charCode<=122) 
		|| charCode==8 || charCode==46 || (!evt.shiftKey && charCode==37) 
		|| charCode==39 || charCode==9)
		return true;		
	return false;	  	
}
/*
 * Muestra el div para editar un usuario
 */
function displayEditUser(userId,userName,firstName,lastName,email){
	$("#_userId").val(userId);
	$("#_id_username").val(userName);
	$("#_id_first_name").val(firstName);
	$("#_id_last_name").val(lastName);
	$("#_id_email").val(email);
	$("#_userForm").show();
} 
/**
 * Update user data
 * @param {Object} csrf_token
 */
function updateUser(csrf_token){
	postData = new Object();
	postData.first_name = $.trim($("#_id_first_name").val());
	postData.last_name = $.trim($("#_id_last_name").val());
	postData.email = $.trim($("#_id_email").val());
	postData.charge = "";
	postData.company = "";	
	postData.password1 = $.trim($("#_id_password1").val());
	postData.password2 = $.trim($("#_id_password2").val());
	postData.id = $.trim($("#_userId").val());
	postData.csrfmiddlewaretoken = csrf_token;
	//@@Validate data
	var empty = false;
	var passwordWrong = false;
	if(isEmpty(postData.first_name) || isEmpty(postData.last_name) || isEmpty(postData.email)
		 ){
		empty = true;
	}
	if(!isEmpty(postData.password1) || !isEmpty(postData.password2)){
		// validate password
		if(postData.password1!=postData.password2){
			passwordWrong = true;
		}
		
	}
	//clean errors
	$("#erros_updateuser").html("");
	if(empty||passwordWrong){
		if(empty)		
			$("#erros_updateuser").html("Por favor llene los campos requeridos");
		else if(passwordWrong)	
			$("#erros_updateuser").html("Contrse&ntilde;as no coinciden");
		return;
	}
	
	
	blockScreen();
	//post data
	$.ajax({
		url:"/ecologia/updateuser/",
		data:postData,
		type:"POST",
		dataType:"json",
		success:function (data,textstatus,jqXHR){
			// update table data
			if(data.status=="ok"){
				$("#firstname_"+data.data.id).html(data.data.first_name);
				$("#lastname_"+data.data.id).html(data.data.last_name);
				$("#email_"+data.data.id).html(data.data.email);
			}
			cleanAndCloseUserForm();
			unBlockScreen();
		}
	});
	
}

function blockScreen(){
	$.blockUI({message:"<h2><img src='/site_media/img/waiting.gif' /> Espere... </h2>"});
}
function unBlockScreen(){
	$.unblockUI();	 
}
function isEmpty(str){
	return $.trim(str)=="";
}
/**
 * Clear and close the user form
 */
function cleanAndCloseUserForm(){
	$("#_userId").val("");
	$("#_id_username").val("");
	$("#_id_first_name").val("");
	$("#_id_last_name").val("");
	$("#_id_email").val("");
	$("#_id_password1").val("");
	$("#_id_password2").val("");
	$("#_userForm").hide();
}
