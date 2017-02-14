$(document).ready(function() {
	
	$("#id_capa_exportar").change(function() {
		var idSelect = $(this).attr("id");
		getDatafDiscreta(idSelect);
	});
	$("#str_mapa_valor_fvalor").keypress(function(evt){
		return acceptInputStr(this,evt);
	});
});
function hideAndCleanFunDiscretas(){
	$("#tabla_discretas tbody tr").remove();
	$("#tabla_discretas").hide();
	$("#error_fn_continua").text("");
}
function getDatafDiscreta(idSelect) {
	var capaSeleccionada = $("#" + idSelect + " option:selected").val()
	if(capaSeleccionada != "") {
		// Primero cheamos si a esta capa se le puede aplicar la función discreta
		// Lo sabemos si en la info de la capa su dataType es igual a CELL
		var postData = new Object();
		postData.capa_nombre = capaSeleccionada;
		//var isCapaInteger = true;
		hideAndCleanFunDiscretas();
		show_overlay();
		$.ajax({
			url : "/ecologia/getfdiscretas/",
			data : postData,
			async : true,
			type : "GET",
			dataType : "json",
			success : function(data, textstatus, jqXHR) {
				if(data.isInteger == true) {
					if (data.too_much_info){
						$("#error_fn_continua").text("Esta capa tiene demasiados datos");
						hide_overlay();
						return;
					}
					
					if(data.val_discretas.length > 0) {
						for(var i = 0; i < data.val_discretas.length; i++) {
							// Objeto tiene dos elementos: id y nombre
							var discreto = data.val_discretas[i];
							var tr = $("<tr></tr>");
							var td_id = $("<td id='fdid_" + i + "' ></td>").html(discreto[0]);
							//id
							$(tr).append(td_id);
							var td_nombre = $("<td></td>").html(discreto[1]);
							//nombre
							$(tr).append(td_nombre);
							var input = $("<input id='fdnewval_" + i + "' maxlength='10'/>");
							$(input).css("width", "60px");							
							var td_newval = $("<td></td>").append(input);
							$(tr).append(td_newval);
							var td_error = $("<td style='color:red;' id='fderror_" + i + "' ></td>").html("");
							//error
							$(tr).append(td_error);
							$("#tabla_discretas tbody").append(tr);
							//$(input).val('0');
						}
						$("#tabla_discretas").show();
					}
				} else {
					$("#error_fn_continua").text("Capa no es entera (CELL). Selecciona una que sí sea.");
				}
				hide_overlay();
			}
		});
		
	}
}

function generaFuncionValor(csrf_token) {
	// Primero validamos
	var itemsLength = $("#tabla_discretas tbody tr").length;
	var PREFIX_ID = "#fdid_";
	var PREFIX_NEWVAL = "#fdnewval_";
	var PREFIX_ERROR = "#fderror_";
	var error = false;
	var queryString = "";
	for(var i = 0; i < itemsLength; i++) {
		var newval = $.trim($(PREFIX_NEWVAL + i).val());
		
		
		floatval = parseFloat(newval).toFixed(2);
		if(floatval>1.0 || floatval<0.0){			
			$(PREFIX_ERROR + i).text("debe ser un valor entre 0 y 1");
			$(PREFIX_ID + i).focus();
			return;
		}
		
		
		$(PREFIX_ERROR + i).text("");
		if(newval == "") {
			error = true;
			$(PREFIX_ERROR + i).text("Campo requerido");
		} else if(isNaN(newval)) {
			error = true;
			$(PREFIX_ERROR + i).text("Campo numérico");
		} else {
			var id = $.trim($(PREFIX_ID + i).html());
			queryString = queryString + "_" + id + "*" + newval;
		}
	}
	if(error == false) {
		queryString = queryString.substring(1);
		$("#dlg_mapa_valor_fdiscreta span").text("");
		$("#dlg_mapa_valor_fdiscreta").dialog({		
		autoOpen : false,
		height : 150,
		width : 280,
		show : "fade",
		hide : "fade",
		resizable : false,
		draggable : false,
		modal : true,
		buttons : {
			"Mapa valor" : function() {
				show_overlay();
				nombreCapa = $.trim($("#str_mapa_valor_fvalor").val());
				ups_id = $('#id_sector option:selected').val();
				id_actividad = $('#id_actividad option:selected').val();
				id_atributo = $('#id_atributo option:selected').val();				
				capa_entrada = $('#id_capa_exportar option:selected').val();
				
				var postData = new Object();
				postData.newvalues = queryString;
				postData.csrfmiddlewaretoken = csrf_token;				
				postData.nombreCapa = nombreCapa;
				postData.ups_id = ups_id;
				postData.id_actividad = id_actividad;
				postData.id_atributo = id_atributo;
				postData.capa_entrada = capa_entrada;
				
				//**************************Validar data
				
				if(postData.nombreCapa==""){
					$("#dlg_mapa_valor_fdiscreta span").text("Campo requerido");					
					hide_overlay();
					return;	
				}else if(postData.id_atributo==undefined || postData.id_atributo==""){
					$("#dlg_mapa_valor_fdiscreta span").text("Es necesario tener una actividad");					
					hide_overlay();
					return;
				}
				postData.nombreCapa = cleanString(postData.nombreCapa);
				$("#str_mapa_valor_fvalor").val(postData.nombreCapa);
				capa = String($('#name_capa').text());
				
				//**********************************
				$(this).dialog("close");
				$(".ui-dialog").hide();
				show_overlay();						
				$.ajax({
					url : "/ecologia/generafdiscreta/",
					data : postData,
					async : true,
					type : "POST",
					dataType : "json",
					success : function(data, textstatus, jqXHR) {
						$("#div_info span").each(function() {
								t = $(this);
								id = t.attr('id');
								t.text(data[id]);
						});
						setZoom(false);
						setImagePreview(data);
						//$('#img_tabla_color').attr("src", "/site_media/img/tabla_color.png");

						$("#tbs_capa").tabs("option", "selected", 1);
						show_jqplot2(jplot_grafica);
						$("#tbs_capa").tabs("option", "selected", 0);

						$('#id_mapa_valor option:selected').removeAttr("selected");
						//$('#id_mapa_valor').append($('<option></option>').val(data.id).html(nombre));
						$('#id_mapa_valor').append($('<option></option>').val(data.id).html(data.mapa_name));
						$('#id_mapa_valor option[value=' + data.id + ']').attr('selected', true);
						//nombre capa base con el que se generó el mapa función valor
						$('#name_capa').text(capa);
						// nombre del mapa recién creado
						//setMapName(nombre);
						setMapName(data.mapa_name);
						
						hide_overlay();
						
						$("#id_capa_in > optgroup:first").append('<option value="r'+data.mapa_name+'">'+data.mapa_name+'</option>');
					}
				});
				//hide_overlay();
			},
			"Cancelar" : function() {
				$(this).dialog("close");

			}
			}
		});
		$("#dlg_mapa_valor_fdiscreta input").val("");
		$("#dlg_mapa_valor_fdiscreta").dialog("open");		
		
	}
}
