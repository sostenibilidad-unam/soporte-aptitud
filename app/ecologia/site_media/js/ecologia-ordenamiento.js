var max_fun = 0;
var min_fun = 0;

sector_name = '';
sector_id = '';

$(document).ready(function() {

	$(".app").height("790px");
	//$("#str_mapa_valor_fvalor").hide();

	$('#terminal_grass').terminal(function(command, term) {
		if(command != '') {
			term.echo(command);
		}
	}, {
		greetings : "          __________  ___   __________    _______________ " + "\n" + "         / ____/ __ \\/   | / ___/ ___/   / ____/  _/ ___/ " + "\n" + "        / / __/ /_/ / /| | \\__ \\\\_  \\   / / __ / / \\__ \\ " + "\n" + "       / /_/ / _, _/ ___ |___/ /__/ /  / /_/ // / ___/ /  " + "\n" + "       \\____/_/ |_/_/  |_/____/____/   \\____/___//____/   " + "\n" + " \n",
		name : 'grass64',
		height : 470,
		prompt : 'GRASS:~ > ',

		keypress : function(e, term) {
			return b_terminal;
		},
		keydown : function(e, term) {
			return b_terminal;
		}
	});

	/*
	 * ACORDION
	 */

	$("#accordion").accordion({
		autoHeight : false,
		navigation : true,
		change : function(event, ui) {
			active = $('#accordion').accordion('option', 'active');
			cleanWorkArea(active);
		}
	});

	/*
	 * tool-preview
	 */
	$("#rad_preview").buttonset({
		create : function(event, ui) {
			$('#rad_vista').attr('checked', 'true');
		}
	}).change(function() {
		id = $('#rad_preview :checked').attr('id');
		if(id == 'rad_info') {
			div_show_hide('div_info', 'div_img_capa')
		} else if(id == 'rad_vista') {
			div_show_hide('div_img_capa', 'div_info')
		}
	});

	$("#id_zoom").button({
		icons : {
			primary : "ui-icon ui-icon-zoomin"
		}
	}).click(function() {

		var options;

		if($(this).text() === "Imagen") {
			setZoom(false);
		} else {
			setZoom(true);
		}
		/*
		 // si es un operador ejecutar la función
		 if($("#_rol_").val()=="Qwr05")
		 $(this).button("option", options);
		 */
	}).hide();

	$("#btn_del_capa").button({
		icons : {
			primary : "ui-icon-trash"
		}
	}).click(function() {
		accordion = $("#accordion").accordion("option", "active");
		id_ups = $('#id_sector').val();
		capa = $("#name_capa").val();

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

					$(this).dialog("close");
				}
			}
		}).dialog("open");
	}).hide();

	/*
	 * Submenu preparacion de capa
	 */
	$("#rad_preparacion").buttonset({
		create : function(event, ui) {
			$('#rad_operacion').attr('checked', 'true');
			$('#div_operacion').show();
		}
	}).change(function() {
		id = $('#rad_preparacion :checked').attr('id');

		$('#div_calculadora').hide();
		$('#div_operacion').hide();
		$('#terminal_grass').hide();
		b_terminal = false;
		if(id == 'rad_calculadora') {
			div_show('div_calculadora')
		} else if(id == 'rad_operacion') {
			div_show('div_operacion', 'div_info')
		} else if(id == 'rad_terminal') {
			b_terminal = true;
			div_show_hide('terminal_grass')
		}
	});
	/*
	 * TABS
	 */

	$("#tbs_capa").tabs({

		select : function(event, ui) {
			// show sector tools: sector, actividad, atributo, peso
			showSectorTools();
			t = ui.tab.hash;

			$('#tbl_mapa_valor tbody').remove();

			//clic en el tab 'función continua
			if(t == '#continua') {
				nameCapa = $("#name_capa").text();
				if(nameCapa != "") {
					var min = $("#min").text();
					var max = $("#max").text();
					$("#graph_name_capa_val").text(nameCapa);
					$("#graph_values_capa_val").text("Mín(" + min + ") Máx(" + max + ")");
					max_fun = max;
					min_fun = min;

				} else {
					$("#graph_name_capa_val").text("");
					$("#graph_values_capa_val").text("");
				}
			}
			if(t == '#discreta') {
				//alert(sector_name + '   ' + sector_id);
				hideAndCleanFunDiscretas();
				$("#id_capa_exportar").val("");

			}
			if(t == '#preparacion') {
				b_grass = true;
				// escondiendo atributo y peso
				hideAtributoPeso(true);
			} else {
				b_grass = false;
				b_terminal = false;
			}

			if(t == '#aptitud') {
				// escondiendo campos actividad, atributo, peso
				hideAtributoPeso(true);
				hideActividad(true);
				id = $('#id_sector').val();
				data = {
					'typ' : 0,
					'id_ups' : id
				};

				ajax("/ecolgoia/select/subsector/", data, function(data) {
					//tabla de mapa funcion valor para aptitud

					$.each(data.tbl_mapa_valor, function(id, val) {
						newTr = $('<tr></tr>');
						_id = 0;
						$.each(val, function(id, val) {
							if(id != 0) {
								newTd = $('<td></td>').val('').html(val);
								newTr.append(newTd);
							} else {
								_id = val;
							}
						});
						newTd = $('<td></td>').val('').html("<input type='checkbox' name='analisis_aptitud' value='" + _id + "'></input>");
						newTr.append(newTd);

						$('#tbl_mapa_valor').append(newTr);
					});

					$('#tbl_mapa_valor tbody').find('tr').each(function() {
						td = $($(this).find('td')[1]).text()

						if(td != $('#id_actividad option:selected').text()) {
							$(this).hide();
						} else {
							$(this).fadeIn();
						}
					});
				});
			}

		}
	}).height(650);

	/*
	 * Actividad
	 */
	$("#btn_subsector button:first").button({
		icons : {
			primary : "ui-icon ui-icon-plusthick"
		},
		text : false
	}).click(function() {

		$('#div_actividad tr').each(function(index) {
			if(index > 0) {
				$(this).remove();
			}
		});
		$("#dlg_actividad input[id='id_actividad']").removeAttr("disabled");
		$("#dlg_actividad input[id='atributo']").removeAttr("disabled");
		$("#dlg_actividad input[id='peso']").removeAttr("disabled");
		//
		// Valor del sector actualmente seleccionado
		var sectorId = $("#id_sector").val();
		// Colocando el mismo valor de sector para la modal
		$("#dlg_actividad select[id='id_sector']").val(sectorId)
		// Primer validación: Checar si la suma de los pesos de los atributos
		// de una actividad ya es 1, de ser así ya no puede agregar más.
		var actividadLength = $("#id_actividad option").length;
		$('#dlg_actividad').dialog("open");
		// Para que no pase y cargue en automático los valores ya cargados
		// @@TODO: manejar esto de las actividades y atributos
		actividadLength = -100;

		if(actividadLength > 0) {

			//Ya se tiene una actividad seleccionada, entonces sí debemos relizar
			// la primer validación
			var actividad = $("#id_actividad option:selected").text();
			var actividad_id = $("#id_actividad option:selected").val();
			$("#dlg_actividad input[id='id_actividad']").val(actividad);
			// Ahora voy por los atributos y pesos
			var postData = new Object();
			postData.actividad_id = actividad_id;

			ajax_sync('/ecologia/actividad/atributos/', postData, function(response) {
				var atributos = response.atributos;
				if(atributos.length > 0) {
					for(var i = 0; i < atributos.length; i++) {
						var atributo = atributos[i];
						if(i == 0) {
							$("#dlg_actividad input[id='atributo']").val(atributo.atributo);
							$("#dlg_actividad input[id='peso']").val(atributo.peso);
							$("#dlg_actividad input[id='atributo']").attr("disabled", "true");

							$("#dlg_actividad input[id='peso']").attr("disabled", "true");

						} else {
							createAtributeRow(atributo.atributo, atributo.peso, 'div_actividad', true);
						}
					}

					// Si tiene atributos entonces ya los tiene completos
					// deshabilitamos
					$("#dlg_actividad input[id='id_actividad']").attr("disabled", "true");
					$("#dlg_actividad input[id='id_sector']").attr("disabled", "true");
				}

			});
		}

		$("#atributo:first").attr("maxlength", "100");
		//
		//$('#dlg_actividad').dialog("open");
		return false;
	}).next().button({
		icons : {
			primary : "ui-icon ui-icon-pencil"
		},
		text : false
	}).click(function() {
		return false;
	}).next().button({
		icons : {
			primary : "ui-icon ui-icon-trash"
		},
		text : false
	}).click(function() {
		return false;
	});

	$("#dlg_actividad").dialog({
		autoOpen : false,
		height : 500,
		width : 465,
		show : "fade",
		hide : "fade",
		resizable : false,
		draggable : false,
		modal : true,

		buttons : {
			"Cancelar" : function() {
				$(this).dialog("close");
			}
		}
	});

	/*
	* FORM
	*/

	//Crear actividad
	$("#factividad input[type=submit]").click(function() {
		$('#dlg_actividad p').text("");

		// validaciones
		var actividad = $.trim($("#factividad input[id='id_actividad']").val());
		// actividad
		if(actividad == "") {
			$('#dlg_actividad p').text("Campo Actividad es obligatorio");
			return false;
		}

		// atrributo
		var emptyAtributo = false;
		$("#factividad input[id='atributo']").each(function(index) {
			var atributo = $.trim($(this).val());
			if(atributo == "")
				emptyAtributo = true;
		});
		if(emptyAtributo) {
			$('#dlg_actividad p').text("Campo atributo no puede estar en blanco");
			return false;
		}
		// peso
		var emptyPeso = false;
		var sumaPesos = 0;
		$("#factividad input[id='peso']").each(function(index) {
			var peso = $.trim($(this).val());
			if(peso == "")
				emptyPeso = true;
			else
				sumaPesos = sumaPesos + Number(peso);
		});
		if(emptyPeso) {
			$('#dlg_actividad p').text("Campo peso no puede estar en blanco");
			return false;
		}
		if(sumaPesos != 1) {
			$('#dlg_actividad p').text("La sumatoria de los pesos debe ser igual a 1");
			return false;
		}

		$("#dlg_actividad").dialog("close");

		var postData = new Object();
		postData.actividad = $.trim($("#factividad input[id='id_actividad']").val());
		postData.atributo = new Array();
		postData.peso = new Array();
		postData = $('#factividad').formSerialize()
		postData.csrfmiddlewaretoken = $("#ord_csrf_token").val();
		show_overlay();
		$.ajax({
			url : "/ecologia/set/actividad/",
			data : postData,
			type : "POST",
			dataType : "json",
			success : function(data, textstatusjqXHR) {
				if(data.success) {
					$('#id_actividad').empty();
					$('#id_atributo').empty();
					//actividad
					$.each(data.actividad, function(id, val) {
						str = "<option value=" + val[0] + ">" + val[1] + "</option>"
						$('#id_actividad').append(str);
					});
					//atributo
					$.each(data.atributo, function(id, val) {
						str = "<option value=" + val[0] + ">" + val[1] + "</option>"
						$('#id_atributo').append(str);
					});
					//peso
					$('#id_peso').text(data.peso[0][1]);

				} else {
					$("#dlg_actividad").dialog("open");

					$("#dlg_actividad input[id='id_actividad']").val(data.actividad);
					$('#dlg_actividad p').text(String(data.error));

				}
				hide_overlay();

			}
		});
		//***************************************

	});

	$("#btn_actividad button:first").button({
		icons : {
			primary : "ui-icon ui-icon-plusthick"
		}
	}).click(function() {
		createAtributeRow(null, null, 'div_actividad', false);
		return false;
	}).next().button({
		icons : {
			primary : "ui-icon ui-icon-trash"
		}
	}).click(function() {
		if($('#div_actividad tr').size() > 1) {
			$('#div_actividad tr:last').fadeOut(function() {
				$(this).remove();
			});
		}
		return false;
	}).next().button({
		icons : {
			primary : "ui-icon ui-icon-document"
		}
	}).click(function() {

		return false;
	});
	/*
	 * Tool subsector Ajax
	 */

	$('#id_sector').val($('options:first', $('#id_sector')).val());
	$('#id_sector').change(function() {
		sector = $('#id_sector option:selected').text().toLowerCase();
		$('#sector').text(sector);

		$('#id_actividad').empty();
		$('#id_atributo').empty();

		$('#id_mapa_valor').empty();
		$('#id_mapa_sector').empty()
		$('#id_mapa_aptitud').empty()

		$('#tbl_mapa_valor tbody').remove();

		$('#id_peso').text('');
		id = $('#id_sector').val();
		sector_name = sector;
		sector_id = id;
		data = {
			//actividad
			'typ' : 0,
			'id_ups' : id
		};

		ajax("/ecolgoia/select/subsector/", data, function(data) {

			if(data.success) {

				//actividad
				$.each(data.actividad, function(id, val) {
					str = "<option value=" + val[0] + ">" + val[1] + "</option>"
					$('#id_actividad').append(str);
				});
				//atributo
				$.each(data.atributo, function(id, val) {
					str = "<option value=" + val[0] + ">" + val[1] + "</option>"
					$('#id_atributo').append(str);
				});
				//peso

				if(data.peso.length > 0) {
					pesos = {};
					$.each(data.peso, function(id, val) {
						pesos[data.peso[id][0]] = data.peso[id][1]
					});
					$('#id_peso').text(pesos[data.atributo[0][0]]);
				}
				/*
				if(data.peso.length > 0) {
				$('#id_peso').text(data.peso[0][1]);
				}
				*/

				//mapset funcion valor
				$.each(data.mapa_valor, function(id, val) {
					$('#id_mapa_valor').append($('<option></option>').val(val[0]).html(val[1]));
				});

				//select de operaciones basicas
				$($('#id_capa_in optgroup')[0]).empty();
				$($('#id_capa_in optgroup')[0]).attr('label', 'BD cartográfica ' + sector);

				//mapset sector
				$.each(data.mapa_sector, function(id, val) {
					$('#id_mapa_sector').append($('<option></option>').val(val[0]).html(val[1]));
					$($('#id_capa_in optgroup')[0]).append($('<option></option>').val(val[0]).html(val[1]));
				});
				//mapset funcion APTITUD
				$.each(data.mapa_aptitud, function(id, val) {
					$('#id_mapa_aptitud').append($('<option></option>').val(val[0]).html(val[1]));
				});

				$('#id_capa_in').val($('options:first', $('#id_sector')).val());

				//tabla de mapa funcion valor para aptitud
				$.each(data.tbl_mapa_valor, function(id, val) {
					newTr = $('<tr></tr>');
					_id = 0;
					$.each(val, function(id, val) {
						if(id != 0) {
							newTd = $('<td></td>').val('').html(val);
							newTr.append(newTd);
						} else {
							_id = val;
						}
					});
					newTd = $('<td></td>').val('').html("<input type='checkbox' name='analisis_aptitud' value='" + _id + "'></input>");
					newTr.append(newTd);

					$('#tbl_mapa_valor').append(newTr);
				});
				//refresh espacio de trabajo
				$("#accordion").accordion("option", "active", 0);
				$("#tbs_capa").tabs("option", "selected", 0);
				$("#name_capa").empty();

				$('.cloud-zoom').attr("href", "");
				$('#img_capa').attr("src", "");
				$("#img_tabla_color").attr("src", "");
				$("#btn_del_capa").hide();

			}
		});
	});

	$('#id_actividad').val($('options:first', $('#id_actividad')).val());

	$('#id_actividad').change(function() {

		$('#id_atributo').empty();
		$('#id_peso').text('');
		id = $('#id_sector').val();
		idd = $('#id_actividad option:selected').val();
		data = {
			//atributo
			'typ' : 1,
			'id_ups' : idd
		};

		ajax("/ecolgoia/select/subsector/", data, function(data) {
			//atributo

			$.each(data.atributo, function(id, val) {
				str = "<option value=" + val[0] + ">" + val[1] + "</option>"
				$('#id_atributo').append(str);
			});
			//peso

			pesos = {};
			$.each(data.peso, function(id, val) {
				pesos[data.peso[id][0]] = data.peso[id][1]
			});
			$('#id_peso').text(pesos[data.atributo[0][0]]);

			$('#tbl_mapa_valor tbody').find('tr').each(function() {
				td = $($(this).find('td')[1]).text();
				if(td != $('#id_actividad option:selected').text()) {
					$(this).hide();
				} else {
					$(this).fadeIn();
				}
			});
		});
	});

	$('#id_atributo').val($('options:first', $('#id_atributo')).val());
	$('#id_atributo').change(function() {
		$('#id_peso').text('');
		id = $('#id_sector').val();
		data = {
			//peso
			'typ' : 2,
			'id_ups' : id,
			'atributo_id' : $(this).val()
		};
		ajax("/ecolgoia/select/subsector/", data, function(data) {
			//peso
			$('#id_peso').text(data.peso);
		});
	});
	/*
	 * Mapas Sector name
	 */
	$('#sector').text($('#id_sector option:selected').text().toLowerCase());

	/*
	 * Select capas
	 */

	$('#id_cartografica').change(function() {
		/* tab: BD Cartográfica general*/
		setZoom(false);
		setDelete(false);
		if($(this).val().length == 1) {
			type = String($(this).val()).substr(0, 1);
			capa = String($(this).val()).substr(1);
			tbs = $("#tbs_capa").tabs('option', 'selected');
			id_ups = $('#id_sector').val();

			$('#name_capa').text(capa);
			data = {
				'ups_id' : id_ups,
				'capa' : capa,
				'type' : type
			};

			ajax("/grass/permanent/", data, function(data) {

				$("#div_info span").each(function() {
					t = $(this);
					id = t.attr('id');
					if(type == 'r') {
						t.text(data[id]);
					} else if(type == 'v') {

					}
				});
				setImagePreview(data);
				setMapName(capa);
				$("#tbs_capa").tabs("option", "selected", 0);
				$("#image_title").html(data.title);
			});
		}
	});

	$('#id_mapa_sector').change(function() {
		/*tab: BD cartográfica sector X*/
		setZoom(false);
		if($(this).val().length == 1) {
			capa = String($('#id_mapa_sector option:selected').text())
			tbs = $("#tbs_capa").tabs('option', 'selected');
			ups_id = $('#id_sector').val();
			$('#name_capa').text(capa);
			data = {
				'capa' : capa,
				'ups_id' : ups_id,
			};

			ajax("/grass/mapset/", data, function(data) {
				$("#div_info span").each(function() {
					t = $(this);
					id = t.attr('id');
					t.text(data[id]);
				});
				setImagePreview(data);
				setMapName(capa);
				setDelete(true);
				//$("#btn_del_capa").show();
				$("#tbs_capa").tabs("option", "selected", 0);
				$("#image_title").html(data.title);
			});
		}
	});

	$('#id_mapa_valor').change(function() {
		/*tab: Mapas. función valor*/
		setZoom(false);
		setDelete(true);
		if($(this).val().length == 1) {
			capa = String($('#id_mapa_valor option:selected').text());
			id_mapa = String($('#id_mapa_valor').val());
			tbs = $("#tbs_capa").tabs('option', 'selected');
			id = String($('#id_sector').val());
			$('#name_capa').text(capa);
			data = {
				'capa' : capa,
				'usp' : id,
				'sector' : $("#id_sector option:selected").val(),
				'id_mapa' : id_mapa,
			};

			ajax("/grass/mapset/valor/", data, function(data) {

				$("#div_info span").each(function() {
					t = $(this);
					id = t.attr('id');
					t.text(data[id]);
				});
				setImagePreview(data);
				//$('#img_tabla_color').attr("src", "/site_media/img/tabla_color.png");
				fv = data['fv'];
				$('#id_actividad').val(fv.id_actividad);

				$('#id_atributo').empty();
				$.each(fv.atributo, function(id, val) {
					$('#id_atributo').append($('<option></option>').val(val[0]).html(val[1]));
				});
				$('#id_atributo').val(fv.id_atributo);
				$('#id_peso').text(fv.id_peso);
				setMapName(capa);
				$("#image_title").html(data.title);
				/*
				 * Grafica
				 */
				if($("#_rol_").val() == "Qwr05") {
					//Esto se hace cuando el rol es un operador
					min = fv.sld_min_max[0];
					max = fv.sld_min_max[1];
					switch(parseInt(data.typ_fun)) {
						case JSPLOT.CRECIENTE_CX:
						case JSPLOT.DECRECIENTE_CX:
						case JSPLOT.DECRECIENTE_CV:
						case JSPLOT.CRECIENTE_CV:
							satu = fv.sld_saturacion;
							break;

						case JSPLOT.CAMPANA:
							ampl = fv.sld_amplitud;
							xmax = fv.sld_xmax;
							break;

						case JSPLOT.CAMPANA_INV:
							ampl = fv.sld_amplitud;
							xmin = fv.sld_xmin;
							break;

						case JSPLOT.DIFUSA:
							break;

					}
					$("#tbs_capa").tabs("option", "selected", 1);
					show_jqplot2(data.typ_fun);
					$("#tbs_capa").tabs("option", "selected", 0);
				}

				//$("#btn_del_capa").show();
			});
		}
	});

	$('#id_mapa_aptitud').change(function() {
		/*tab: Mapas: aptitud*/
		setZoom(false);
		setDelete(true);
		if($(this).val().length == 1) {
			capa = String($('#id_mapa_aptitud option:selected').text());
			id_aptitud = String($('#id_mapa_aptitud').val());
			ups_id = String($('#id_sector').val());

			$('#name_capa').text(capa);
			data = {
				'capa' : capa,
				'ups_id' : ups_id,
				'id_aptitud' : id_aptitud
			};

			ajax("/grass/mapset/aptitud/", data, function(data) {

				if(data.aprobado == true) {
					$("#txt_aprobado").show();					
					$("#txt_no_aprobado").hide();
					
					$("#btn_aceptar_aptitud").hide();
					$("#btn_desaprobar_aptitud").show();
				} else {
					$("#txt_aprobado").hide();					
					$("#txt_no_aprobado").show();
					$("#btn_aceptar_aptitud").show();
					$("#btn_desaprobar_aptitud").hide();

				}

				$("#div_info span").each(function() {
					t = $(this);
					id = t.attr('id');
					t.text(data[id]);
				});
				setImagePreview(data);
				//$('#img_tabla_color').attr("src", "/site_media/img/tabla_color.png");
				setMapName(capa);
				//$("#btn_del_capa").show();
				//$("#btn_aceptar_aptitud").show();
			});
		}
	});
	/*
	 * MAPA VALOR
	 */

	$('#btn_mapa_valor').button().click(function() {
		capa = String($('#name_capa').text());
		actividad = $('#id_actividad option:selected').text()

		$("#dlg").dialog({
			title : "Mapa función de valor",
			autoOpen : false,
			height : 150,
			width : 350,
			show : "fade",
			hide : "fade",
			resizable : false,
			draggable : false,
			modal : true,
			buttons : {
				"Aceptar" : function() {
					$(this).dialog("close");
				}
			}
		});

		if(capa == "" || actividad == "") {
			str = ""
			if(capa == "") {
				str = "Por favor seleccione una capa de \"BD Cartográfica\" ";
			} else {
				str = "Es necesario tener una actividad"
			}
			$('#dlg p').text(str);
			$('#dlg').dialog("open");
			b = false;
		} else {
			$("#dlg_mapa_valor").dialog("option", "height", 150);
			$('#dlg_mapa_valor').dialog("open");
			atributo = $('#id_atributo option:selected').text()
			peso = $('#id_peso').text()
			$('#msg_mapa_valor').text("Actividad: " + actividad + " Atributo: " + atributo + " Peso: " + peso);
		}

		return false;
	});

	$("#dlg_mapa_valor").dialog({
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
				capa = String($('#name_capa').text());
				id = String($('#id_sector').val());
				nombre = $.trim(String($('#str_mapa_valor').val()));
				atributo = String($('#id_atributo').val());
				data = {
					'typ_db' : 1,
					'capa' : nombre,
					'id_sector' : id,
				}

				$(this).dialog("close");
				$(".ui-dialog").hide();
				status = false;

				ajax_sync("/grass/syntax/", data, function(data) {
					status = data.status;
					if(!data.status) {
						$("#dlg_mapa_valor").dialog("option", "height", 200);
						$("#dlg_mapa_valor").dialog("open");
						$("#dlg_mapa_valor p").text(data.error);
					}
				});
				if(status) {
					//alert("---->>" + function_min_val + "---" +function_max_val);
					data = {
						'type_fun' : String(jplot_grafica),
						'capa' : capa,
						'mapa' : nombre,
						'id' : id,
						'sector' : $("#id_sector option:selected").val(),
						'atributo' : atributo,
						'min' : String(min),
						'max' : String(max),
						'min_func' : String(function_min_val),
						'max_func' : String(function_max_val),
					};

					switch(jplot_grafica) {
						case JSPLOT.CRECIENTE_CX:
						case JSPLOT.DECRECIENTE_CX:
						case JSPLOT.DECRECIENTE_CV:
						case JSPLOT.CRECIENTE_CV:
							data['parm_control'] = String(parm_control);
							data['saturacion'] = String(satu)
							break;

						case JSPLOT.CAMPANA:
							data['x'] = String(xmax);
							data['ampl'] = String(ampl);
							break;

						case JSPLOT.CAMPANA_INV:
							data['x'] = String(xmin);
							data['ampl'] = String(ampl);
							break;

						case JSPLOT.DIFUSA:
							data['a'] = $("#sld_difusa_a").slider("value");
							data['b'] = $("#sld_difusa_b").slider("value");
							data['c'] = $("#sld_difusa_c").slider("value");
							data['d'] = $("#sld_difusa_d").slider("value");
							break;
					}

					$(this).dialog("close");

					$("#accordion").accordion("option", "active", 2);
					ajax("/grass/continua/", data, function(data) {
						if(data.status) {

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

							$("#id_capa_in > optgroup:first").append('<option value="r' + data.mapa_name + '">' + data.mapa_name + '</option>');

							//$("#id_capa_exportar > optgroup:first").append('<option value="r'+data.mapa_name+'">'+data.mapa_name+'</option>');
							//<option value="lagos_1_oper1_5**alpha1_gra_temp">alpha1_gra_temp</option>

						} else {

							$("#dlg_mapa_valor").dialog("open");
							$("#dlg_mapa_valor p").text(data.error);
						}
					});
				}
			},
			"Cancelar" : function() {
				$(this).dialog("close");

			}
		}
	});

	/*
	 * MAPA APTITUD
	 */

	$("#btn_aceptar_aptitud").button().click(function() {
		data = {
			'id_aptitud' : $('#id_mapa_aptitud option:selected').val(),
		};

		ajax("/grass/aptitud/aprobar/", data, function(data) {
			if(data.status) {
				$('#btn_desaprobar_aptitud').show();
				$('#btn_aceptar_aptitud').hide();
				$("#txt_aprobado").show();									
				$("#txt_no_aprobado").hide();
			}
		});
	}).hide();

	$("#btn_desaprobar_aptitud").button().click(function() {
		data = {
			'id_aptitud' : $('#id_mapa_aptitud option:selected').val(),
		};

		ajax("/grass/aptitud/aprobar/", data, function(data) {
			if(data.status) {
				$('#btn_desaprobar_aptitud').hide();
				$('#btn_aceptar_aptitud').show();
				$("#txt_aprobado").hide();							
				$("#txt_no_aprobado").show();
			}
		});
	}).hide();

	$('#btn_mapa_aptitud').button().click(function() {
		array = new Array();
		$('#tbl_mapa_valor  input:checked').each(function() {
			array.push($(this).val());
		});
		if(array.length == 0) {
			$('#dlg >p').text("Por favor selecciona los mapa de valor  ");
			$('#dlg').dialog("open");
		} else {
			$('#dlg_mapa_aptitud').dialog("open");
		}
	});

	$("#dlg_mapa_aptitud").dialog({
		autoOpen : false,
		height : 220,
		width : 400,
		show : "fade",
		hide : "fade",
		resizable : false,
		draggable : false,
		modal : true,

		buttons : {
			"Mapa aptitud" : function() {
				array = new Array();
				$('#tbl_mapa_valor  input:checked').each(function() {
					array.push($(this).val());
				});
				ups_id = $('#id_sector').val();
				nombre_aptitud = $('#str_mapa_aptitud').val();
				data = {
					'typ_db' : 2,
					'capa' : nombre_aptitud,
					'id_sector' : ups_id,
					'id_mapa_valor' : '[' + String(array) + ']',
				}

				$(this).dialog("close");
				$(".ui-dialog").hide();
				status = false;

				ajax_sync("/grass/syntax/", data, function(data) {
					status = data.status;
					if(!data.status) {

						$("#dlg_mapa_aptitud").dialog("open");
						$("#dlg_mapa_aptitud p").text(data.error);
					}
				});
				if(status) {
					data = {
						'ups_id' : ups_id,
						'id_mapa_valor' : '[' + String(array) + ']',
						'sector' : $("#id_sector option:selected").val(),
						'nombre_aptitud' : nombre_aptitud
					};

					$("#accordion").accordion("option", "active", 3);
					$(this).dialog("close");

					ajax("/grass/aptitud/", data, function(data) {
						if(data.status) {

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

							$('#id_mapa_aptitud option:selected').removeAttr("selected");

							//$('#id_mapa_aptitud').append($('<option></option>').val(data.id).html(nombre_aptitud));
							$('#id_mapa_aptitud').append($('<option></option>').val(data.id).html(data.mapa_name));
							$('#id_mapa_aptitud option[value=' + data.id + ']').attr('selected', true);
							//$('#name_capa').text(nombre_aptitud);
							$('#name_capa').text(data.mapa_name);
							setMapName(data.mapa_name);
							$("#btn_aceptar_aptitud").show();

							$("#id_capa_in > optgroup:first").append('<option value="r' + data.mapa_name + '">' + data.mapa_name + '</option>');

						}
					});
				}
			},
			"Cancelar" : function() {
				$(this).dialog("close");
			}
		}
	});

	/*
	 * Comandos
	 */

	$("label[for='id_formato']").hide();
	$("label[for='id_setnull']").hide();
	$("label[for='id_categoria']").hide();
	$('#id_comando').change(function() {
		str = $(this).val();

		$('#id_estadistica').empty();
		$("label[for='id_formato']").hide();
		$('#id_formato').hide();
		$("label[for='id_setnull']").hide();
		$('#id_setnull').hide();
		$("label[for='id_categoria']").hide();
		$('#id_categoria').hide();
		id = parseInt(str);

		if(id == CMD_GRASS.NULOS || id == CMD_GRASS.MASCARA) {

			$("#id_capa_in optgroup").last().hide();
			$("#id_capa_in optgroup").last().show();

		} else {
			$("#id_capa_in optgroup").last().show();
		}

		switch (parseInt(str)) {
			case CMD_GRASS.DESAGRUPAR:
				msg = "Recategoriza un mapa raster separando áreas adyacentes y asignandoles una categoría única";
				break;
			case CMD_GRASS.DISTANCIA:
				msg = " Crea una nueva capa calculando distancias a algún punto, línea o polígono.";
				break;
			case CMD_GRASS.PENDIENTE:
				msg = "Genera mapas de pendientes, en grados o en porcentaje, la opción por omisión es grados.";
				$("label[for='id_formato']").show();
				$('#id_formato').show();
				break;
			case CMD_GRASS.MASCARA:
				msg = "Crea una máscara que limita las operaciones de raster." + "</br>" + "(las categorías para enmascarar pueden ser varias separdas por coma, generalmente es 1)";
				$("label[for='id_categoria']").show();
				$('#id_categoria').show();
				break;
			case CMD_GRASS.NULOS:
				msg = "Adminstra los valores nulos de un raster.";
				$("label[for='id_setnull']").show();
				$('#id_setnull').show();
				break;
			case CMD_GRASS.ESTADISTICA:
				msg = "Genera estadísticas de capas raster.";
				break;
		}

		$('#txt_cmd').html(msg);
	});

	$('#id_evaluar_cmd').button().click(function() {
		str = $('#id_comando').val();

		switch (parseInt(str)) {
			case CMD_GRASS.DESAGRUPAR:
			case CMD_GRASS.DISTANCIA:
			case CMD_GRASS.PENDIENTE:
				$('#dlg_cmd').dialog("open");
				break;
			case CMD_GRASS.MASCARA:
				no_input_operation();
				break;
			case CMD_GRASS.NULOS:
				$('#dlg_cmd').dialog("open");
				break;
			case CMD_GRASS.ESTADISTICA:
				cmd = String($('#id_comando').val());
				type = String($('#id_capa_in').val()).substr(0, 1);
				capa_in = String($('#id_capa_in').val()).substr(1);
				id_sector = String($('#id_sector').val());
				data = {
					'cmd' : cmd,
					'type_capa' : type,
					'capa_in' : capa_in,
					'id_sector' : id_sector,
				}

				ajax("/grass/cmd/", data, function(data) {

					if(data.status) {

						$('#id_estadistica').empty();
						//$('#id_estadistica').append("<thead><tr><th><td style='color:#81017E'>ID</td><td style='color:#81017E'>Nombre</td><td style='color:#81017E'>Metros cuadrados</td></th></tr></thead>");
						$('#id_estadistica').append("<tr><th>").html("<td style='color:#81017E'>ID</td><td style='color:#81017E'>Nombre</td><td style='color:#81017E'>Area en m<sup>2</sup></td></th></tr>");
						for( i = 0; i < data.estadistica.length; i++) {
							td = "";
							for( j = 0; j < data.estadistica[0].length; j++) {
								td += "<td>" + data.estadistica[i][j] + "</td>"
							}
							$('#id_estadistica').append($('<tr></tr>').html(td));
						}

					}

				});
				break;
		}
		return false;
	});

	$("#dlg_cmd").dialog({
		autoOpen : false,
		height : 200,
		width : 300,
		show : "fade",
		hide : "fade",
		resizable : false,
		draggable : false,
		modal : true,
		buttons : {
			"Evaluar" : function() {
				cmd = String($('#id_comando').val());
				capa_in = String($('#id_capa_in').val()).substr(1);
				capa_out = String($('#id_capa_out').val());
				type = String($('#id_capa_in').val()).substr(0, 1);
				id_sector = String($('#id_sector').val());
				format = String($('#id_formato').val());
				maskcats = String($('#id_categoria').val());
				setnull = String($('#id_setnull').val());
				data = {
					'typ_db' : 0,
					'capa' : capa_out,
					'id_sector' : id_sector,
				}

				$(this).dialog("close");
				$(".ui-dialog").hide();
				status = false;

				ajax_sync("/grass/syntax/", data, function(data) {
					status = data.status;
					if(!data.status) {
						$("#dlg_cmd").dialog("open");
						$("#dlg_cmd p").text(data.error);
					}
				});
				if(status) {
					data = {
						'type_capa' : type,
						'cmd' : cmd,
						'capa_in' : capa_in,
						'id_sector' : id_sector,
						'capa_out' : capa_out,
						'format' : format,
						'maskcats' : maskcats,
						'setnull' : setnull,
					}

					$("#accordion").accordion("option", "active", 0);
					$(this).dialog("close");

					ajax("/grass/cmd/", data, function(data) {

						if(data.status) {
							setZoom(false);
							setImagePreview(data);
							$("#tbs_capa").tabs("option", "selected", 0);
							$('#id_mapa_sector option:selected').removeAttr("selected");
							$('#id_mapa_sector').append($('<option></option>').val('r' + capa_out).html(capa_out));
							$('#id_mapa_sector option[value=r' + capa_out + ']').attr('selected', true);
							$('#name_capa').text(capa_out);
							setMapName(capa_out);
							//$("#graph_values_capa_val").text("Mín(" + data.min_val + ") Máx(" + data.max_val + ")");

							//Add the created layer to the options in layer preparation
							$("#id_capa_in > optgroup:first").append('<option value="r' + capa_out + '">' + capa_out + '</option>');

							$("#minmax_mapa").html('Mínimo: ' + data.min + '; Máximo:' + data.max);

							$("#min").text(data.min);
							$("#max").text(data.max);

							$("#image_title").html(data.title);

						}
					});
				}
			},
			"Cancelar" : function() {
				$(this).dialog("close");
			}
		}
	});

	/*
	* Clean
	*/

	//dialog
	$(".ui-dialog").bind("dialogopen", function(event, ui) {
		$(this).find(':input').each(function() {
			if(this.type == 'text') {
				$(this).val('');
			}
		});
		$(this).find('p').text("");
	});
});
/*
 * Funciones Util
 */

function setZoom(on_off) {
	//ON
	if(on_off) {
		$("#id_zoom").button("option", {
			label : "Imagen",
			icons : {
				primary : "ui-icon ui-icon-image"
			}
		});

		$('.cloud-zoom').CloudZoom();
		$('.cloud-zoom').show();
		$('#img_capa2').hide();
	}
	//OFF
	else {
		$("#id_zoom").button("option", {
			label : "Zoom",
			icons : {
				primary : "ui-icon ui-icon-zoomin"
			}
		});
		$(".mousetrap").hide();
		$('.cloud-zoom').hide();
		$('#img_capa2').show();
	}
	$('#img_capa').css("padding-left", "31px");

}

function setDelete(on_off) {
	//on
	if(on_off) {
		$("#id_del_mapa").show();
	} else {
		$("#id_del_mapa").hide();

	}
}

function setImagePreview(data) {
	$("#id_zoom").show();
	path64 = "data:image/png;base64,";

	$('.cloud-zoom').attr("href", path64 + data.img_zoom);
	$('#img_capa').attr("src", path64 + data.img_view);
	$('#img_capa2').attr("src", path64 + data.img_view);

	$('#rad_vista').attr('checked', 'true');
	$("label[for='rad_vista']").removeClass();
	$("label[for='rad_info']").removeClass();
	$("label[for='rad_vista']").addClass("ui-button ui-widget ui-state-default ui-button-text-only ui-corner-left ui-state-active");
	$("label[for='rad_info']").addClass("ui-button ui-widget ui-state-default ui-button-text-only ui-corner-right");
	$('#div_info').hide();
	$('#div_img_capa').fadeIn();

}

function cleanWorkArea(active) {
	$("#image_title").html('');
	$("#txt_aprobado").hide();
	$("#txt_no_aprobado").hide();
	$("#tbs_capa").tabs("option", "selected", 0);
	$("#tbs_grass").tabs("option", "selected", 0);

	$("#tbs_capa").hide();
	$("#tbs_grass").hide();
	b_terminal = false;
	$("#btn_del_capa").hide();

	$('#img_capa').attr("src", "");
	$('#img_tabla_color').attr("src", "");
	$('#name_capa').html("");

	//limpiar
	$('#accordion select').each(function(id, val) {
		id = this.id;
		$('#' + id + ' option').attr('selected', false);
	});

	$("#btn_aceptar_aptitud").hide();
	$("#btn_desaprobar_aptitud").hide();

	//vista previa y resultado
	$("#div_info span").each(function() {
		t = $(this);
		id = t.attr('id');
		t.text("");
	});
	$('#div_img_capa').hide();

	//clean chart
	$("#chart1").html("");
	$('#mf').hide();
	$('#id_panel').hide();

	$('#' + toggle + ' img').each(function() {
		a = $(this).attr('style');
		if(a == "display: none;") {
			$(this).attr('style', '');
		} else {
			$(this).attr('style', 'display:none');
		}
	});
	toggle = 0;
	// habilitar campos escondidos
	showSectorTools();
	// limpia el nombre del mapa
	clearMapName();
	var TAB_CARTOGRAFICA_SECTOR = 0;
	var TAB_CARTOGRAFICA_GENERAL = 1;
	var TAB_MAPAS_FUNCION_VALOR = 2;
	var TAB_MAPAS_FUNCION_APTITUD = 3;
	//show
	switch(active) {
		case TAB_CARTOGRAFICA_SECTOR:
		case TAB_CARTOGRAFICA_GENERAL:
			$("#li_preview a").text("Vista previa");
			$("#tbs_capa").fadeIn('normal');
			$("#li_continua").fadeIn('normal');
			$("#li_discreta").fadeIn('normal');
			$("#li_preparacion").fadeIn('normal');
			$("#li_aptitud").hide();
			break;
		case TAB_MAPAS_FUNCION_VALOR:
			$("#li_preview a").text("Resultado");
			$("#tbs_capa").fadeIn('normal');
			$("#li_aptitud").fadeIn('normal');
			$("#li_continua").fadeIn('normal');
			$("#li_discreta").fadeIn('normal');
			$("#li_preparacion").fadeIn('normal');

			/*
			 // número  de los mapas función valor
			 var mpsFnValNbr = $('#id_mapa_valor > option').length;
			 // deshabilitamos el tab de 'anáisis de aptitud' si no
			 // tenemos al menos un maṕa función valor
			 if(mpsFnValNbr<=0){
			 //$("#li_aptitud").removeClass();
			 //$("#li_aptitud").addClass("");
			 $("#li_aptitud a").attr("href","#empty_aptitud");
			 }else{
			 $("#li_aptitud a").attr("href","#aptitud");
			 }*/
			break;
		case TAB_MAPAS_FUNCION_APTITUD:
			$("#li_preview a").text("Resultado");
			$("#tbs_capa").fadeIn('normal');
			$("#li_continua").hide();
			$("#li_discreta").hide();
			$("#li_aptitud").hide();
			$("#li_preparacion").hide();
			break
	}
}

function no_input_operation() { {
		cmd = String($('#id_comando').val());
		capa_in = String($('#id_capa_in').val()).substr(1);
		capa_out = "not_necesary_"
		type = String($('#id_capa_in').val()).substr(0, 1);
		id_sector = String($('#id_sector').val());
		format = String($('#id_formato').val());
		maskcats = String($('#id_categoria').val());
		setnull = String($('#id_setnull').val());
		data = {
			'typ_db' : 0,
			'capa' : capa_out,
			'id_sector' : id_sector,
		}

		$(this).dialog("close");
		$(".ui-dialog").hide();
		status = false;

		ajax_sync("/grass/syntax/", data, function(data) {
			status = data.status;
			if(!data.status) {
				$("#dlg_cmd").dialog("open");
				$("#dlg_cmd p").text(data.error);
			}
		});
		if(status) {
			data = {
				'type_capa' : type,
				'cmd' : cmd,
				'capa_in' : capa_in,
				'id_sector' : id_sector,
				'capa_out' : capa_out,
				'format' : format,
				'maskcats' : maskcats,
				'setnull' : setnull,
			}

			$("#accordion").accordion("option", "active", 0);
			$(this).dialog("close");

			ajax("/grass/cmd/", data, function(data) {
				if(data.status) {
					setZoom(false);
					//setImagePreview(data);
					//$("#tbs_capa").tabs("option", "selected", 0);
					//$('#id_mapa_sector option:selected').removeAttr("selected");
					//$('#id_mapa_sector').append($('<option></option>').val('r' + capa_out).html(capa_out));
					//$('#id_mapa_sector option[value=r' + capa_out + ']').attr('selected', true);
					//$('#name_capa').text(capa_out);
					//setMapName(capa_out);
				}
			});
		}
	}
}
