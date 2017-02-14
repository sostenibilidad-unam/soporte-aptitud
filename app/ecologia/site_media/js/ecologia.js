$(document).ready(function() {
	$("input:submit").button();

	$.datepicker.regional['es'] = {
		closeText : 'Cerrar',
		prevText : '<Ant',
		nextText : 'Sig>',
		currentText : 'Hoy',
		monthNames : ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
		monthNamesShort : ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
		dayNames : ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
		dayNamesShort : ['Dom', 'Lun', 'Mar', 'Mié', 'Juv', 'Vie', 'Sáb'],
		dayNamesMin : ['Do', 'Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sá'],
		weekHeader : 'Sm',
		dateFormat : 'yy-mm-dd',
		firstDay : 1,
		isRTL : false,
		showMonthAfterYear : false,
		yearSuffix : ''
	};
	$.datepicker.setDefaults($.datepicker.regional['es']);
});
/*
 * LOG
 */
function l(log) {
	console.log(log);
}

/*
 * AJAX overlay
 */

function show_overlay() {

	$('#overlay').addClass("ui-widget-overlay");
	$("#overlay").css("z-index", "1001");
	$('#overlay').width($(document).width());
	$('#overlay').height($(document).height());
	$('#floatingBarsG').show();
}

function hide_overlay() {
	$('#floatingBarsG').hide();
	$('#overlay').removeClass("ui-widget-overlay");
	$('#overlay').width("");
	$('#overlay').height("");

}

/*
 * Sleep
 */
function sleep(millisegundos) {
	var inicio = new Date().getTime();
	while((new Date().getTime() - inicio) < millisegundos) {
	}
}

/*
 * UTIL
 */
function div_show_hide(show, hide) {
	$("#" + hide).fadeOut('normal');
	$("#" + hide).hide();
	$("#" + show).fadeIn('normal');
}

function div_show(show) {
	$("#" + show).fadeOut('normal');
	$("#" + show).hide();
	$("#" + show).fadeIn('normal');
}

function div_hide(hide) {
	$("#" + hide).fadeOut('normal');
	$("#" + hide).hide();
}

function cleanString(str){
	if(str.indexOf("á")>=0)
		str = str.replace( new RegExp("á","g"),"a");
	if(str.indexOf("é")>=0)
		str = str.replace(new RegExp("é","g"),"e");
	if(str.indexOf("í")>=0)
		str = str.replace(new RegExp("í","g"),"i");
	if(str.indexOf("ó")>=0)
		str = str.replace(new RegExp("ó","g"),"o");
	if(str.indexOf("ú")>=0)
		str = str.replace(new RegExp("ú","g"),"u");
	if(str.indexOf("ñ")>=0)
		str = str.replace(new RegExp("ñ","g"),"n");
	if(str.indexOf("|")>=0)
		str = str.replace(new RegExp("|","g"),"");
	if(str.indexOf("&")>=0)
		str = str.replace(new RegExp("&","g"),"");
	if(str.indexOf("<")>=0)
		str = str.replace(new RegExp("<","g"),"");
	if(str.indexOf(">")>=0)
		str = str.replace(new RegExp(">","g"),"");
	return str;
}
function acceptInputStr(input,evt){
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
