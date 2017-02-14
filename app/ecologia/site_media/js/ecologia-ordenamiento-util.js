function showSectorTools() {
	hideActividad(false);
	hideAtributoPeso(false);
}

function hideSectorTools() {
	hideActividad(true);
	hideAtributoPeso(true);
}

function hideAtributoPeso(hide) {
	if(hide == true) {
		$("#id_peso, label[for='id_peso']").hide();
		$("#id_atributo, label[for='id_atributo']").hide();
	} else {
		$("#id_peso, label[for='id_peso']").show();
		$("#id_atributo, label[for='id_atributo']").show();
	}
}

function hideActividad(hide) {
	if(hide == true) {
		$("#id_actividad, label[for='id_actividad']").hide();
	} else {
		$("#id_actividad, label[for='id_actividad']").show();
	}
}

function setMapName(name) {
	$("#name_mapa_fnValor").text("Nombre: " + name);
	var text = "Mínimo: " + $("#min").text() + "; Máximo: " + $("#max").text();
	$("#minmax_mapa").text(text);
}

function clearMapName() {
	$("#name_mapa_fnValor").text("");
	$("#minmax_mapa").text("");
}

/**
 * Eliminar mapa/capa
 */
function deleteMapa() {
	// es la capa, qué hay de un mapa recién creado?

	//var nameCapa = $("#name_capa").text();
	var nameCapa = $.trim($("#name_mapa_fnValor").text().replace("Nombre: ", ""));
	var sectorId = $("#id_sector option:selected").val();
	var accordion = $("#accordion").accordion("option", "active");
	var mapavalorId = $("#id_mapa_valor option:selected").val();
	var mapaaptitudId = $("#id_mapa_aptitud option:selected").val();
	var postData = new Object();

	postData.nameCapa = nameCapa;
	postData.sectorId = sectorId;
	postData.mapavalorId = mapavalorId;
	postData.mapaaptitudId = mapaaptitudId;

	$.ajax({
		url : "/ecologia/delcapa/",
		data : postData,
		type : "GET",
		dataType : "json",
		success : function(data, textstatus, jqXHR) {
			if(data.status == "ok") {
				var TAB_CARTOGRAFICA_SECTOR = 0;
				var TAB_CARTOGRAFICA_GENERAL = 1;
				var TAB_MAPAS_FUNCION_VALOR = 2;
				var TAB_MAPAS_FUNCION_APTITUD = 3;
				switch(accordion) {
					case TAB_CARTOGRAFICA_SECTOR:
						optionSelected = $('#id_mapa_sector').val();
						$("#id_mapa_sector option[value='" + optionSelected + "']").remove();
						cleanWorkArea(accordion);
						break;
					case TAB_CARTOGRAFICA_GENERAL:
						break;
					case TAB_MAPAS_FUNCION_VALOR:
						optionSelected = $('#id_mapa_valor').val();
						$("#id_mapa_valor option[value='" + optionSelected + "']").remove();
						cleanWorkArea(accordion);
						break;
					case TAB_MAPAS_FUNCION_APTITUD:
						optionSelected = $('#id_mapa_aptitud').val();
						$("#id_mapa_aptitud option[value='" + optionSelected + "']").remove();
						cleanWorkArea(accordion);
						break;
				}
				$("#dlg").dialog("close");
			} else if(data.status == "fail") {
				$("#dlg").dialog("close");
				alert(data.errorDescription);
			}

		}
	});
}


$(document).ready(function() {
	$("#peso").keypress(function(evt) {
		return acceptDecimalsInput(this, evt);
	});

	$("#id_del_mapa").click(function() {
		var accordion = $("#accordion").accordion("option", "active");
		var TAB_CARTOGRAFICA_GENERAL = 1;
		if(accordion == TAB_CARTOGRAFICA_GENERAL) {
			alert("No puedes borrar del permanent");
			return;
		}

		$("#dlg p").text("¿Está seguro de que desea eliminar la capa " + $("#name_capa").text() + "?");

		$("#dlg").dialog({
			title : "Eliminar capa",
			autoOpen : false,
			height : 150,
			width : 350,
			show : "fade",
			hide : "fade",
			resizable : false,
			draggable : false,
			modal : true,
			buttons : {
				"Cancelar" : function() {
					$(this).dialog("close");
				},
				"Aceptar" : function() {
					deleteMapa();
				}
			}
		}).dialog("open");
	});
});

/**
 * Permite ingresar solamente números decimales
 *
 */
function acceptDecimalsInput(_this, evt) {
	evt = (evt) ? evt : window.event;
	var charCode = (evt.which) ? evt.which : evt.keyCode;
	if(charCode == 37 || charCode == 39) {
		return true;
	}
	if(_this.value.length == 0) {
		// Permite numeros[0-9], el punto y el Tab
		if(charCode >= 48 && charCode <= 57 || charCode == 8 || charCode == 9) {
			return true;
		} else {
			return false;
		}
	} else {
		// Controlo que no haya ya un punto ingresado
		if(_this.value.indexOf('.') >= 1 && charCode == 46) {
			return false;
		} else {
			// Permite numeros[0-9], el punto y el Tab
			if(charCode >= 48 && charCode <= 57 || charCode == 8 || charCode == 46 || charCode == 9) {
				return true;
			} else {
				return false;
			}
		}
	}

}
function createAtributeRow(atributoValue,pesoValue,idParentTable,disabled){
	var tr = document.createElement("tr");
	var td = document.createElement("td");
	var label = document.createElement("label");
	$(label).attr("for","atributo")
	$(label).text("Atributo: ");
	var input = document.createElement("input");
	// atributo
	$(input).attr("id","atributo");
	$(input).attr("type","text");
	$(input).attr("maxlength","100");
	$(input).attr("name","atributo");
	if(atributoValue!=null)
		$(input).val(atributoValue);
	if(disabled==true)	
		$(input).attr("disabled","true");
	$(td).append(label);
	$(td).append(input);
	$(tr).append(td);
	// peso
	td = document.createElement("td");
	label = document.createElement("label");
	$(label).attr("for","peso")
	$(label).text("Peso: ");
	input = document.createElement("input");
	// atributo
	$(input).attr("id","peso");
	$(input).attr("type","text");
	$(input).css("width","50px");	
	$(input).attr("maxlength","5");		
	$(input).attr("name","peso");	
	if(atributoValue!=null)
		$(input).val(pesoValue);	
	if(disabled==true)	
		$(input).attr("disabled","true");
	$(input).keypress(function(evt) {
		return acceptDecimalsInput(this, evt);
	});		
	$(td).append(label);
	$(td).append(input);
	$(tr).append(td);
	$('#'+idParentTable).append(tr)
}
