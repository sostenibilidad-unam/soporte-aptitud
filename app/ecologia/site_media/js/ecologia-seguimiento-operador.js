function activaOperador(operId,active,csrfmiddlewaretoken){
	var postData = new Object();
	postData.operation = active
	postData.operId = operId;
	postData.csrfmiddlewaretoken = csrfmiddlewaretoken;
	show_overlay();
	//post data
	$.ajax({
		url:"/ecologia/activacion_operador/",
		data:postData,
		type:"POST",
		dataType:"json",
		success:function (data,textstatus,jqXHR){
			// update table data
			if(data.status=="ok"){
				var ACTIVO = 1;
				if(data.activo == ACTIVO){
					$("#desactive_oper_"+postData.operId).show();
					$("#active_oper_"+postData.operId).hide();					
				}else{
					$("#active_oper_"+postData.operId).show();
					$("#desactive_oper_"+postData.operId).hide();					
				}
			}			
			hide_overlay();
		}
	});
	
}
