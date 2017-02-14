var hyst_data;
var current_map_id;
var cut_value;
var curr_final;

function checkStatus() {

	data = {
		'ups_id' : '1',
		'node_id' : '1'
	};
	ajax('/ecolgoia/check_maps_status/', data, function(data) {
		if(data.estado == 'changed') {
			$("#change_advice").show();
		}
	});
}

function removeAll() {

	$("#dialog_delete_all").dialog({
		buttons : {
			"Confirmar" : function() {
				$(this).dialog("close");
				data = {
					'ups_id' : '1',
					'node_id' : '1'
				};
				ajax('/ecolgoia/eliminate_all/', data, function(data) {
					$("#dialog_delete_success").dialog({
						buttons : {
							"Aceptar" : function() {
								$(this).dialog("close");
								window.location.reload();
								return;
							}
						}
					});
					$("#dialog_delete_success").dialog("open");
				});
			},
			"Cancelar" : function() {
				$(this).dialog("close");
				return;
			}
		}
	});
	$("#dialog_delete_all").dialog("open");

}

function showImage() {
	$("#div_residuales").hide();
	$("#div_preview").show();
}

function createLegendTable(map_names) {
	var colors = ['rgb(237,194,64)', 'rgb(175,216,248)', 'rgb(203,75,75)', 'rgb(77,167,77)', 'rgb(148,64,237)', 'rgb(189,155,51)', 'rgb(140,172,198)', 'rgb(162,60,60)', 'rgb(61,133,61)', 'rgb(118,51,189)', 'rgb(255,232,76)', 'rgb(210,255,255)', 'rgb(243,90,90)', 'rgb(92,200,92)', 'rgb(177,76,255)', 'rgb(142,116,38)', 'rgb(105,129,148)', 'rgb(121,45,45)', 'rgb(46,100,46)', 'rgb(88,38,142)', 'rgb(255,255,89)', 'rgb(244,255,255)', 'rgb(255,105,105)', 'rgb(107,233,107)', 'rgb(207,89,255)', 'rgb(94,77,25)', 'rgb(69,86,99)', 'rgb(81,29,29)', 'rgb(30,66,30)', 'rgb(59,25,94)', 'rgb(255,255,102)', 'rgb(255,255,255)', 'rgb(255,120,120)', 'rgb(123,255,123)', 'rgb(236,102,255)', 'rgb(47,38,12)', 'rgb(34,43,49)', 'rgb(40,14,14)', 'rgb(15,33,15)', 'rgb(29,12,47)', 'rgb(255,255,115)', 'rgb(255,255,255)', 'rgb(255,135,135)', 'rgb(138,255,138)', 'rgb(255,115,255)', 'rgb(0,0,0)', 'rgb(0,0,0)', 'rgb(0,0,0)', 'rgb(0,0,0)'];
	$("#maps_legend").html('');
	for( i = 0; i < map_names.length; i++) {
		row = '<tr><td class="legendColorBox"><div style="border:1px solid #ccc;padding:1px"><div style="width:4px;height:0;border:5px solid ' + colors[i] + ';overflow:hidden"></div></div></td><td class="legendLabel" style="font-size: 18px;">' + map_names[i] + '</td></tr>';
		$("#maps_legend").append(row);
	}
}

function showResiduales() {

	$("#div_preview").hide();
	$("#div_residuales").show();
	data = {
		'ups_id' : '1',
		'node_id' : '1'
	};
	ajax('/ecolgoia/get_residuals/', data, function(data) {

		if(data.residuals == 'missing_maps') {
			$("#dialog_missing").dialog({
				buttons : {
					"Aceptar" : function() {
						$(this).dialog("close");
						return;
					}
				}
			});
			$("#dialog_missing").dialog("open");
			return;
		}

		if(data.residuals == 'missing_approved') {
			$("#dialog_missing_approved").dialog({
				buttons : {
					"Aceptar" : function() {
						$(this).dialog("close");
						return;
					}
				}
			});
			$("#dialog_missing_approved").dialog("open");
			return;
		}

		$("#gower_container").html("");
		map_names = data.maps;
		createLegendTable(map_names)
		$.each(data.residuals, function(index, value) {
			curr_id = "grupo_" + index;
			$("#gower_container").append('<div style="float: left;" align="center"><span class="">Grupo ' + value.nombre + '</span><div id="' + curr_id + '" style="width:240px;height:150px;"></div></div>');
			all_data = [];
			$.each(value.data, function(ind, val) {
				curr_data = [];
				curr_data.push([ind, val]);
				all_data.push(curr_data);
			});
			plotGower(curr_id, all_data);
			$("#export_buttons").show();
			setImageGroupsLink();

			if(data.type != "db") {
				$("#success_dialog").dialog({
					buttons : {
						"Aceptar" : function() {
							$(this).dialog("close");
							return;
						}
					}
				});
				$("#success_message").html("Residuales generados exitosamente");
				$("#success_dialog").dialog("open");
			}

		});
	});
}

function plotGower(placeholder, data) {
	placeholder = "#" + placeholder;

	var p = $.plot($(placeholder), data, {
		series : {
			lines : {
				show : false,
				fill : true,
				steps : true
			},
			bars : {
				show : true,
				barWidth : 1
			}
		},
		grid : {
			hoverable : true
		}
	});

}

function getValues(values) {
	var d1 = [];
	for(var i = 0; i < values.length; i++) {
		d1.push([i, values[i]]);
	}
	return d1;
}

function viewGroupsMap() {
	url = "/grass/mapa/grupos/";
	setZoom(false);
	ups_id = 1;
	data = {
		'ups_id' : ups_id,
	};
	ajax(url, data, function(data) {
		$('#img_capa').width("640px");
		$('#img_capa2').width("640px");
		$('#img_capa').height("480px");
		$('#img_capa2').height("480px");
		$('#img_capa').hide();
		setImagePreview(data);
		showImage();
		$("#map_title").html('Mapa de Grupos').show();
		$("#hyst_container").hide();
		$("#podar").hide();
		$("#ejecutar").hide();
		$("#groups_message").html(data.mensaje).show();
	});
}

function setImageGroupsLink() {
	url = "/grass/mapa/grupos_img/";
	setZoom(false);
	ups_id = 1;
	data = {
		'ups_id' : ups_id,
	};
	ajax(url, data, function(data) {
		if(data.imagen_grupo) {
			$("#groups_link").show();
		} else {
			$("#groups_link").hide();
		}
	});
}

function plotWithOptions(low) {
	var p = $.plot($("#placeholder"), [low], {
		series : {
			lines : {
				show : false,
				fill : true,
				steps : true
			},
			bars : {
				show : true,
				barWidth : 1
			},
			threshold : {
				above : {
					limit : cut_value,
					color : '#92278F'
				},
				below : {
					limit : cut_value,
					color : '#CBD422'
				}
			}
		},
		grid : {
			hoverable : true,
			clickable : true
		}
	});

	$.each(p.getData()[0].data, function(i, el) {
		var o = p.pointOffset({
			x : el[0],
			y : el[1]
		});
		$('<div class="data-point-label"> <a href="javascript:;" onclick="changeCut(\'' + el[0] + '\');">' + el[1] + '</a></div>').css({
			position : 'absolute',
			left : o.left + 4,
			top : o.top - 15,
			'font-size' : '9px',
			color : '#92278F',
			display : 'none'
		}).appendTo(p.getPlaceholder()).fadeIn('slow');
	});
}

function initTrees() {
	$("#red").treeview({
		animated : "fast",
		collapsed : true,
		unique : true,
		persist : "cookie",
		toggle : function() {
			window.console && console.log("%o was toggled", this);
		}
	});
}

function viewMap(mapKey) {
	current_map_id = mapKey;
	url = "/grass/mapa/grupo/";
	setZoom(false);
	ups_id = 1;
	data = {
		'ups_id' : ups_id,
		'node_id' : mapKey
	};
	ajax(url, data, function(data) {
		setImagePreview(data);
		$('#img_capa').width("640px");
		$('#img_capa2').width("640px");
		$('#img_capa').height("480px");
		$('#img_capa2').height("480px");
		$('#img_capa').hide();
		hyst_data = data.hyst_data;
		cut_value = Number(data.valor_corte) - 1;
		map_title = data.map_title;
		curr_final = data.es_final;
		var d1 = getValues(hyst_data);

		$("#hyst_container").show();

		plotWithOptions(d1);
		$("#placeholder > div > div.yAxis > div.tickLabel").hide();
		$("#placeholder > div > div > div.tickLabel:first").hide();
		$("#placeholder > div > div.xAxis > div.tickLabel").css("left", "-=25");
		$("#cuttingPointLabel").html(cut_value + 1);
		$("#map_title").html('Mapa ' + map_title).show();
		$("#groups_message").hide();
		if(!data.corte_ejecutado) {
			$("#ejecutar").show();
			$("#podar").hide();
		} else {
			$("#ejecutar").hide();
			$("#podar").show();
		}
		showImage();
	});
}

function createFirstNode() {
	data = {
		'ups_id' : '1'
	};
	ajax("/ecolgoia/create_fisrt_node/", data, function(data) {
		if(data.corte_ejecutado == 'missing_maps') {
			$("#dialog_missing").dialog({
				buttons : {
					"Aceptar" : function() {
						$(this).dialog("close");
						return;
					}
				}
			});
			$("#dialog_missing").dialog("open");
			return;
		}
		if(data.corte_ejecutado == 'missing_approved') {
			$("#dialog_missing_approved").dialog({
				buttons : {
					"Aceptar" : function() {
						$(this).dialog("close");
						return;
					}
				}
			});
			$("#dialog_missing_approved").dialog("open");
			return;
		}
		getNodes();
		node_id = data.node_id
		viewMap(node_id);
		$("#success_dialog").dialog({
			buttons : {
				"Aceptar" : function() {
					$(this).dialog("close");
					return;
				}
			}
		});
		$("#success_message").Text("Mapa generado exitosamente");
		$("#success_dialog").dialog("open");
	});
}

function changeCut(index) {
	$("#dialog").dialog({
		buttons : {
			"Confirmar" : function() {
				$("#dialog").dialog("close");
				cut_value = index;
				data = {
					'ups_id' : '1',
					'cut_value' : cut_value,
					'node_id' : current_map_id
				};
				ajax("/ecolgoia/change_cut/", data, function(data) {

					$("#success_dialog").dialog({
						buttons : {
							"Aceptar" : function() {
								$(this).dialog("close");
								return;
							}
						}
					});
					$("#success_message").html("Punto de corte cambiado exitosamente");
					$("#success_dialog").dialog("open");

					getNodes();
					viewMap(current_map_id);

				});
			},
			"Cancelar" : function() {
				$(this).dialog("close");
				return;
			}
		}
	});
	$("#dialog").dialog("open");
}

function getNodes() {
	data = {
		'ups_id' : '1'
	};
	ajax("/ecolgoia/get_nodes/", data, function(data) {

		$("#main").html("");
		var currId;
		var currVal;
		var currParent;

		if(data.length > 0) {
			$.each(data, function(index, value) {
				currId = value.id;
				currVal = value.mapkey;
				currParent = value.parent;
				currIndex = value.mapindex;
				if(currParent == undefined) {
					$("#main").append("<ul id='red' class='treeview-red'><li id='" + currId + "'><span><a id='mapLink_" + currId + "' onclick=\"javascript:viewMap('" + currVal + "');\" href='javascript:;' >" + currIndex + "</a></span></li></ul>");
				} else {
					$("#" + currParent).append("<ul><li id='" + currId + "' ><span><a id='mapLink_" + currId + "' onclick=\"javascript:viewMap('" + currVal + "');\" href='javascript:;' >" + currIndex + "</a></span></li></ul>");

				}
			});
			$("#tree_header").hide();
			initTrees();
		} else {
			$("#tree_message").html("Click aqu&iacute; para empezar");
			$("#tree_header").show();
		}
		setImageGroupsLink();
	});
}


$(document).ready(function() {

	getNodes();
	checkStatus();
	$("#tbs_capa").height("auto");
	$(".app").height("auto");
	$("#ejecutar").hide();

	$("#dialog").dialog({
		autoOpen : false,
		modal : true
	});
	$("#dialog_cuts").dialog({
		autoOpen : false,
		modal : true
	});
	$("#dialog_missing").dialog({
		autoOpen : false,
		modal : true
	});
	$("#dialog_missing_approved").dialog({
		autoOpen : false,
		modal : true
	});
	$("#dialog_delete").dialog({
		autoOpen : false,
		modal : true
	});

	$("#success_dialog").dialog({
		autoOpen : false,
		modal : true
	});
	
	$("#dialog_delete_all").dialog({
		autoOpen : false,
		modal : true
	});	
	
	$("#dialog_delete_success").dialog({
		autoOpen : false,
		modal : true
	});	

	$('.lst_cartografica_admin').change(function() {
		id = $(this).attr('id');
		if(id == 'id_sector_groups') {
			url = "/grass/mapa/grupo/";
		} else {
			url = "/grass/mapset/aptitud/";
		}
		setZoom(false);
		if($(this).val().length == 1) {
			id_aptitud = String($(this).val());
			capa = String($(this).find("option:selected").text());
			ups_id = 1;
			$('#name_capa').text(capa);
			data = {
				'capa' : capa,
				'ups_id' : ups_id,
				'id_aptitud' : id_aptitud
			};
			ajax(url, data, function(data) {
				setImagePreview(data);
			});
		}
	});

	$("#ejecutar").button({
		icons : {
			primary : ""
		}
	}).click(function() {
		data = {
			'ups_id' : '1',
			'node_id' : current_map_id
		};
		ajax("/ecolgoia/generate/aptitudegroups/", data, function(data) {
			getNodes();
			corte_ejecutado = data.corte_ejecutado
			if(corte_ejecutado == 'missing_maps') {
				$("#dialog_missing").dialog({
					buttons : {
						"Aceptar" : function() {
							$(this).dialog("close");
							return;
						}
					}
				});
				$("#dialog_missing").dialog("open");
			}
			if(corte_ejecutado == 'missing_approved') {
				$("#dialog_missing_approved").dialog({
					buttons : {
						"Aceptar" : function() {
							$(this).dialog("close");
							return;
						}
					}
				});
				$("#dialog_missing_approved").dialog("open");
			}
			if(corte_ejecutado == 'ok') {
				$("#ejecutar").hide();
				$("#success_dialog").dialog({
					buttons : {
						"Aceptar" : function() {
							$(this).dialog("close");
							return;
						}
					}
				});
				$("#success_message").html("Corte ejecutado exitosamente");
				$("#success_dialog").dialog("open");
			}
			if(corte_ejecutado == 'insuficientes') {
				$("#dialog_cuts").dialog({
					buttons : {
						"Aceptar" : function() {
							$(this).dialog("close");
							return;
						}
					}
				});
				$("#dialog_cuts").dialog("open");
			}
		});
	});

	$("#podar").button({
		icons : {
			primary : ""
		}
	}).click(function() {
		$("#dialog_delete").dialog({
			buttons : {
				"Confirmar" : function() {
					$("#dialog_delete").dialog("close");
					data = {
						'ups_id' : '1',
						'node_id' : current_map_id
					};
					ajax("/ecolgoia/eliminate_nodes/", data, function(data) {
						getNodes();
						if(data.message == 'ok') {
							$("#ejecutar").show();
							$("#podar").hide();

							$("#success_dialog").dialog({
								buttons : {
									"Aceptar" : function() {
										$(this).dialog("close");
										return;
									}
								}
							});
							$("#success_message").html("Mapas eliminados exitosamente");
							$("#success_dialog").dialog("open");

						}
					});
				},
				"Cancelar" : function() {
					$(this).dialog("close");
					return;
				}
			}
		});
		$("#dialog_delete").dialog("open");
	});

	$("#id_zoom").click(function() {
		$('#img_capa').css("padding-left", "47px");
	});

});
