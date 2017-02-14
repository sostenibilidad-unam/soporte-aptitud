$(document).ready(function() {
	$("#id_nombre_capa").keypress(function(evt){
		return acceptInputStr(this,evt);
	});
	
});
function submitExportarCapa(){
	var submit = true;
	var capaExportar = $("#id_capa_exportar").val();
	$("#error_export").text("");
	//show_overlay();
	if(capaExportar==""){
		submit = false
		$("#error_export").text("Seleccione capa a exportar");
		//hide_overlay();
		
	}	
	
	return submit;
}

function submitImportarCapa(){
	capaName = cleanString($.trim($("#id_nombre_capa").val()));
	$("#id_nombre_capa").val(capaName);
	if(capaName==""){
		$("#error_import").text("El campo es requerido");
		return false;
	}
	
	
	show_overlay();
	var submit = true;
	$("#error_import").text("");
	var postData = new Object();
	postData.capaName = capaName;
	$.ajax({
		url:"/ecologia/imp_exist_capa/",
		async:false,
		data:postData,
		type:"GET",
		dataType:"json",
		success:function (data,textstatus,jqXHR){
			// update table data
			if(data.error==true){
				submit = false;
				$("#error_import").text(data.error_description);
				//hide_overlay();
				
			}
			//unBlockScreen();
		}
	});
	hide_overlay();
	return submit;
	
}
