function editUser(idUser){
	var postData = new Object();
	postData.userId = idUser;
	$.ajax({
		url:"/ecologia/getuser/",
		data:postData,
		type:"GET",
		dataType:"json",
		success:function (data,textstatusjqXHR){
			$("#id_username").val(data.username);
			$("#id_first_name").val(data.first_name);
			$("#id_last_name").val(data.last_name);
			$("#id_email").val(data.email);
			$("#id_charge").val(data.charge);
			$("#id_company").val(data.company);
			$("#userId").val(data.id);
			
			$("#userForm").show();
		}
	});
}
function cleanAndCloseUserForm(){
	$("#id_username").val("");
	$("#id_first_name").val("");
	$("#id_last_name").val("");
	$("#id_email").val("");
	$("#id_charge").val("");
	$("#id_company").val("");
	$("#userId").val("");
	$("#userForm").hide();
}
function updateUser(csrf_token){
	postData = new Object();
	postData.first_name = $.trim($("#id_first_name").val());
	postData.last_name = $.trim($("#id_last_name").val());
	postData.email = $.trim($("#id_email").val());
	postData.charge = $.trim($("#id_charge").val());
	postData.company = $.trim($("#id_company").val());
	postData.password1 = $.trim($("#id_password1").val());
	postData.password2 = $.trim($("#id_password2").val());
	postData.id = $.trim($("#userId").val());
	postData.csrfmiddlewaretoken = csrf_token;
	//@@Validate data
	var empty = false;
	var passwordWrong = false;
	if(isEmpty(postData.first_name) || isEmpty(postData.last_name) || isEmpty(postData.email)
		|| isEmpty(postData.charge) || isEmpty(postData.company) ){
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
function viewProgram(idProgram){
	$("#id_programa_id").val(idProgram);
	$("#adminViewProgramForm").submit();
}
