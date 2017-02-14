$(document).ready(function() {
	
	$("#id_username").keypress(function(evt){
		return acceptInputStr(this,evt);
	});
	
	$("#accordion").accordion({
		autoHeight : false,
		navigation : true,
		create : function(event, ui) {
			//limpiar
			$('#accordion select').each(function(id, val) {
				id = this.id;
				$('#' + id + ' option').attr('selected', false);
			});
		}
	});

	$('#id_fecha_inicio').datepicker({
	});

	/*
	 * Switch
	 */
	$("#rad_registro").buttonset().change(function() {
		id = $('#rad_registro :checked').attr('id');
		if(id == 'rad_ver') {
			div_show_hide('div_ver', 'div_crear')
		} else if(id == 'rad_crear') {
			div_show_hide('div_crear', 'div_ver')
		}
	});
	/*
	 * select programa admin
	 */

	$('#id_programa_admin').change(function() {
		$('#id_sector').empty();
		id = String($(this).val());
		data = {
			'id' : id
		};
		ajax("/ecologia/get/programa/", data, function(data) {

			$.each(data.sector, function(id, val) {
				$('#id_sector').append($('<option></option>').val(val[0]).html(val[1]));
			});
			if(data.operador == 0) {
				$("input[name='operador']").attr("checked", false);
			} else {
				$("input[name='operador']").each(function() {
					c = $(this);
					if(c.val() == data.operador) {
						c.attr('checked', true);
					}
				});
			}

			$.each(data.programa, function(id, val) {
				$('#' + id).text(val);
			});
			div_show('info_programa');
		});
	});
	/*
	 * select programa autoridad
	 */

	$('#id_programa_root2').change(function() {
		$("#tbs_programa").tabs("option", "selected", 0);
		id = String($(this).val());
		data = {
			'id' : id
		};
		ajax("/ecologia/get/programa/", data, function(data) {
			$.each(data.programa, function(id, val) {
				$('#' + id).text(val);
			});
			div_show_hide('info_programa', 'add_programa');
		});
	});
	
	
	/*
	 *  FORM Asignar Operador-Sector a mapset
	 */

	$("#fasignar input[type=submit]").click(function() {

		$('#id_programa').val($('#id_programa_admin').val());
		
		ajax_form('#fasignar','/ecologia/set/asignar/', function(data) {
			if(data.success){
				
			}			
		});
		
	});
	
	/*
	 * Seleccionar sector
	 */

	$('#id_sector').change(function() {
		id_sector = String($(this).val());
		id_programa = String($('#id_programa_admin').val());
		data = {
			'id_sector' : id_sector,
			'id_programa' : id_programa
		};
		ajax("/ecologia/get/operador/sector/", data, function(data) {

			if(data.operador == 0) {
				$("input[name='operador']").attr("checked", false);
			} else {
				$("input[name='operador']").each(function() {
					c = $(this);
					if(c.val() == data.operador) {
						c.attr('checked', true);
					}
				});
			}

		});
	});
	/*
	 * tool bar
	 */
	$('#btn_add').click(function() {

		$("#id_programa_root2 option").attr("selected", false);
		div_show_hide('add_programa', 'info_programa');
	});
});
