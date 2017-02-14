$(document).ready(function() {
	$("#asociarBtn").click(function() {
		asociarOperadorSector()
	});
	$("#sectorForm input[id='id_nombre']").keypress(function(evt) {
		return acceptSectornameInput(this, evt);
	});
});
/**
 * Permite ingresar solamente letras minúsculas y números
 *
 */
function acceptSectornameInput(input, evt) {
	evt = (evt) ? evt : window.event;
	var charCode = (evt.which) ? evt.which : evt.keyCode;
	// Permite: letras 97: a, 122: z
	// Permite: números 48: 0, 57: 9
	// Permite: borrar 8l, delete: 46
	// Permite: LeftArrownot Shift + : 37
	// Permite: RightArrow: 39 and .
	// Permite: TAB: 9
	if((evt.shiftKey && (charCode >= 97 && charCode <= 122)) || (charCode >= 48 && charCode <= 57) || (charCode >= 97 && charCode <= 122) || charCode == 8 || charCode == 46 || (!evt.shiftKey && charCode == 37) || charCode == 39 || charCode == 9)
		return true;
	return false;
}

/**
 * Elimina caracteres como acentos de
 */
function clearSectorInputs() {
	var nombre = $("#sectorForm input[id='id_nombre']").val();
	var prefijo = $("#sectorForm input[id='id_prefijo_mapas']").val();
	nombre = nombre.replace("á", "a");
	nombre = nombre.replace("é", "e");
	nombre = nombre.replace("í", "i");
	nombre = nombre.replace("ó", "o");
	nombre = nombre.replace("ú", "u");
	nombre = nombre.replace("ñ", "n");

	prefijo = prefijo.replace("á", "a");
	prefijo = prefijo.replace("é", "e");
	prefijo = prefijo.replace("í", "i");
	prefijo = prefijo.replace("ó", "o");
	prefijo = prefijo.replace("ú", "u");
	prefijo = prefijo.replace("ñ", "n");

	$("#sectorForm input[id='id_nombre']").val(nombre);
	$("#sectorForm input[id='id_prefijo_mapas']").val(prefijo);

	return true;
}

function asociarOperadorSector() {
	var postData = new Object();
	postData.operadorId = $("#id_operadores option:selected").val();
	postData.sectorId = $("#id_sectores option:selected").val();
	postData.csrfmiddlewaretoken = $("#csrf").val();
	clearMessages();
	blockScreen();
	$.ajax({
		url : "/ecologia/asociar_operador_sector/",
		data : postData,
		type : "POST",
		dataType : "json",
		success : function(data, textstatusjqXHR) {
			if(data.status == "fail") {
				$("#error_content").html(data.description);
			} else {
				$("#success_content").html("Relaci&oacute;n creada");
				var tr = document.createElement("tr");
				var td = document.createElement("td");
				$(td).html(data.data.userName)
				$(tr).append(td);
				td = document.createElement("td");
				$(td).html(data.data.sectorName);
				$(tr).append(td);
				$("#tbl_relacion").append(tr);
				//alert(data.data.relacionId + "@" + data.data.sectorName + "@" + data.data.programName);
			}
			unBlockScreen();
		}
	});
}

function clearMessages() {
	$("#error_content").html("");
	$("#success_content").html("");
	$("#error_deleting").hide();
	
	$("#id_nombre").val('');
	$("#id_prefijo_mapas").val('');
	
}

function blockScreen() {
	$.blockUI({
		message : "<h2><img src='/site_media/img/waiting.gif' /> Espere... </h2>"
	});
}

function unBlockScreen() {
	$.unblockUI();
}

function isEmpty(str) {
	return $.trim(str) == "";
}

function deleteSector(id) {

	$("#body-app > div > center > p").html('');
	$("table.rol  > tbody > tr > td > ul.errorlist").hide();
	blockScreen();
	clearMessages();
	
	data = {
		'ups_id' : '1',
		'sector_id' :id		
	};
	ajax("/ecologia/borrar_sector/", data, function(data) {			
			if(data.status == "fail") {
				$("#error_deleting").html(data.description+"<br/>").show();				
			} else {
				$("#error_deleting").html(data.description).hide();
				$("#body-app > div > center > p").html(data.description);
				$("#tbl_rol > tbody > tr#" + id).html('');
			}
			unBlockScreen();
	});


}
