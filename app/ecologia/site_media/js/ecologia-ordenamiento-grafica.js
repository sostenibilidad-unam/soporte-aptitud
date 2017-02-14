var JSACCORDION = {
	"INFORMACION" : 0,
	"VISTA_PREVIA" : 1,
	"FUNCION_CONTINUA" : 2,
	"FUNCION_DISCRETA" : 3,
}
var js_accordion;

var JSPLOT = {
	"CRECIENTE_CX" : 0,
	"DECRECIENTE_CX" : 1,
	"DECRECIENTE_CV" : 2,
	"CRECIENTE_CV" : 3,
	"CAMPANA" : 4,
	"CAMPANA_INV" : 5,
	"DIFUSA" : 6
};
var jplot_grafica;

var CMD_GRASS = {
	"DESAGRUPAR" : 0,
	"DISTANCIA" : 1,
	"PENDIENTE" : 2,
	"MASCARA" : 3,
	"NULOS" : 4,
	"ESTADISTICA" : 5
}

var toggle = 0;
var min, max;
var xmin, xmax;
var ampl, satu;
var abcd = [];
var b_terminal = false;
var b_grass = false;
var parm_control;

var ENTER = 13;
var totalPoints = 100;

var function_min_val;
var function_max_val;


/*
 * Max Min
 */

Array.prototype.max = function() {
	var max = Number.MIN_VALUE, v, len = this.length, i = 0;
	for(; i < len; ++i)
	if( typeof ( v = this[i]) == 'number')
		max = Math.max(max, v);
	return max;
}

Array.prototype.min = function() {
	var min = Number.MAX_VALUE, v, len = this.length, i = 0;
	for(; i < len; ++i)
	if( typeof ( v = this[i]) == 'number')
		min = Math.min(min, v);
	return min;
}
function createSamplePoints(max, min, stepSize){
	// Function to get the Max value in Array
    Array.max = function( array ){
        return Math.max.apply( Math, array );
    };

    // Function to get the Min value in Array
    Array.min = function( array ){
       return Math.min.apply( Math, array );
    };
	// Obtenemos el paso
	var STEP = (max-min)/stepSize;
	// Obtenemos los puntos muestra con lo que iniciamos
	var samplePoints = new Array();
	var index = 0;
	//alert("min: " + min + " max: " + max);
	var tmp = min;
	for(var i=min;i<=max;i=i+STEP){	
		samplePoints[index] = i;	
		index++;		
	}
	return samplePoints;
}
/**
 * @return un arreglo donde el primer elemento  es y- y el segundo es y*
 * 
 */
function getMinusAsteriskArray(samplePoints){
	var y_minus = Array.min(samplePoints);
	var y_asterisk = Array.max(samplePoints);
	var result = new Array();
	result[0] = y_minus;
	result[1] = y_asterisk;
	function_min_val = y_minus;
	function_max_val = y_asterisk;
	return result;	
}

/*
 * isNumeric
 */

function isNumeric(input) {
	return (input - 0) == input && input.length > 0;
}

/*
 * Ecuacion
 */

function log10(x) {
	return (Math.log(x) / Math.log(10));
}

function ecu_creciente_cx(x, max, satu,y_minus,y_asterisk) {
	pc = ((log10(log10(1.1 + 0.88 * (10 - satu))) / Math.pow(log10(max), 2) ) ) * 1;
	parm_control = pc;
	//return (1 - Math.exp((x * (pc * -1)))  );
	return (1 - Math.exp((x * (pc ))) - y_minus ) / (y_asterisk-y_minus);
}

function ecu_decreciente_cx(x, max, satu,y_minus,y_asterisk) {
	pc = Math.pow(10, ((3 / 10) * (log10(Math.pow(max, 5)) - satu )));
	parm_control = pc;
	//return (1 - Math.exp((x - 30) / pc));
	//var e = 1 - Math.exp((-1* ( (x-30)/pc )));
	var e = 1 - Math.exp(( ( (x-30)/pc )));
	return (e - y_minus)/(y_asterisk-y_minus);
}

function ecu_creciente_cv(x, max, satu,y_minus,y_asterisk) {
	pc = ((log10(log10(1.1 + 0.88 * (10 - satu))) / Math.pow(log10(max), 2) ) ) * -1;
	parm_control = pc;
	var e = Math.exp((x * pc));
	return (e-y_minus)/(y_asterisk-y_minus);
}

function ecu_decreciente_cv(x, max, satu,y_minus,y_asterisk) {
	pc = ((log10(log10(1.1 + 0.88 * (10 - satu))) / Math.pow(log10(max), 2) ) ) * -1;
	parm_control = pc;
	var e = Math.exp((x * (pc * -1)));
	
	return (e-y_minus)/(y_asterisk-y_minus);
}
/**
 * Calcula los valores normalizados de y-, y*
 * usados para el cálculo del a función creciente CV
 * @return un arreglo donde el primer elemento  es y- y el segundo es y*
 */
function calculateCrecienteCv_yLess_yAsterisk(min, max, satu){	
	// parámetro de control
	var pc = ((log10(log10(1.1 + 0.88 * (10 - satu))) / Math.pow(log10(max), 2) ) ) * -1;
	
	var samplePoints = createSamplePoints(max,min,20);
	// Aplicamos la fórmula a los puntos muestra
	for(var i=0;i<samplePoints.length;i++){
		// Actualizamos el punto con la función ya aplicada		
		//samplePoints[i] =  1 - Math.exp((-1* ( (samplePoints[i]-30)/pc )));
		samplePoints[i] =  Math.exp((samplePoints[i] * pc ));
	}
	return getMinusAsteriskArray(samplePoints);
}
/**
 * Calcula los valores normalizados de y-, y*
 * usados para el cálculo del a función decreciente CV
 * @return un arreglo donde el primer elemento  es y- y el segundo es y*
 */
function calculateDecrecienteCv_yLess_yAsterisk(min, max, satu){	
	// parámetro de control
	var pc = ((log10(log10(1.1 + 0.88 * (10 - satu))) / Math.pow(log10(max), 2) ) ) * -1;
	
	var samplePoints = createSamplePoints(max,min,20);
	// Aplicamos la fórmula a los puntos muestra
	for(var i=0;i<samplePoints.length;i++){
		// Actualizamos el punto con la función ya aplicada		
		//samplePoints[i] =  1 - Math.exp((-1* ( (samplePoints[i]-30)/pc )));
		samplePoints[i] =  Math.exp((samplePoints[i] * (pc * -1)));
	}
	return getMinusAsteriskArray(samplePoints);
}
/**
 * Calcula los valores normalizados de y-, y*
 * usados para el cálculo del a función decreciente CX
 * @return un arreglo donde el primer elemento  es y- y el segundo es y*
 */
function calculateDecrecienteCx_yLess_yAsterisk(min, max, satu){
	/*
	 * pc = Math.pow(10, ((3 / 10) * (log10(Math.pow(max, 5)) - satu )));
	parm_control = pc;
	return (1 - Math.exp((x - 30) / pc));
	 */
	// parámetro de control
	var pc = Math.pow(10, ((3 / 10) * (log10(Math.pow(max, 5)) - satu )));
	
	var samplePoints = createSamplePoints(max,min,20);
	// Aplicamos la fórmula a los puntos muestra
	for(var i=0;i<samplePoints.length;i++){
		// Actualizamos el punto con la función ya aplicada		
		//samplePoints[i] =  1 - Math.exp((-1* ( (samplePoints[i]-30)/pc )));
		samplePoints[i] =  1 - Math.exp(( ( (samplePoints[i]-30)/pc )));
	}
	return getMinusAsteriskArray(samplePoints);
}
/**
 * Calcula los valores normalizados de y-, y*
 * usados para el cálculo del a función creciente CX
 * @return un arreglo donde el primer elemento  es y- y el segundo es y*
 */
function calculateCrecienteCx_yLess_yAsterisk(min, max, satu){
	/*
	 * pc = ((log10(log10(1.1 + 0.88 * (10 - satu))) / Math.pow(log10(max), 2) ) ) * -1;
	parm_control = pc;
	return (1 - Math.exp((x * (pc * -1)))  );
	 */
	// parámetro de control
	var pc = (log10(log10(1.1 + 0.88 * (10 - satu))) / Math.pow(log10(max), 2) ) * 1;
	
	var samplePoints = createSamplePoints(max,min,20);
	// Aplicamos la fórmula a los puntos muestra
	for(var i=0;i<samplePoints.length;i++){
		// Actualizamos el punto con la función ya aplicada		
		samplePoints[i] = (1 - Math.exp(samplePoints[i] * pc)  );
	}
	return getMinusAsteriskArray(samplePoints);
}
/**
 * Calcula los valores normalizados de y-, y*
 * usados para el cálculo del a función contnua de campana
 * @return un arreglo donde el primer elemento  es y- y el segundo es y*
 */
function calculateCampana_yLess_yAsterisk(min, max, xmax, alfa){
	
	var alfa = ampl;
	var samplePoints = createSamplePoints(max,min,20);
	// Aplicamos la fórmula a los puntos muestra
	for(var i=0;i<samplePoints.length;i++){
		// Actualizamos el punto con la funci+ón ya aplicada
		samplePoints[i] = Math.pow(Math.E, -1 * Math.pow( (samplePoints[i]-xmax)/alfa ,2));
	}
	return getMinusAsteriskArray(samplePoints);
}

function ecu_campana(x, max, ampl, xmax, y_minus,y_asterisk) {
	
	/*
	 * Parámetros
	 *
		X = mapa del atributo
		Xmax
		alfa: ampl
		Y-: 
		Y*
		
		Función:
		
		v = (E^-(X-Xmax/alfa)^2  - Y-) / Y* - Y-
		
	*/
	var alfa = ampl;
	var e = Math.pow(Math.E, -1 * Math.pow((x-xmax)/alfa,2));		
	var v = (e - y_minus)/(y_asterisk-y_minus);
	return v;
}
function ecu_campana_inversa(x, max, ampl, xmin, y_minus,y_asterisk) {
	var campana = ecu_campana(x, max, ampl, xmin, y_minus,y_asterisk);	 
	return 1-Number(campana);
}
function ecu_difusa_logic(x, abcd) {
	a = abcd[0];
	b = abcd[1];
	c = abcd[2];
	d = abcd[3];
	f0 = (1 - ((x - a) / (b - a)) ) * (Math.PI / 2);
	f1 = ((x - c) / (d - c) ) * (Math.PI / 2);
	if(x < a) {
		return 0;
	} else if(x > d) {
		return 0;
	} else if(x >= a && x <= b) {
		return Math.pow(Math.cos(f0), 2);
	} else if(x > b && x < c) {
		return 1;
	} else if(x >= c && x <= d) {
		return Math.pow(Math.cos(f1), 2);
	}
}

/*
 * Normalizar
 */

function normalizar(x, max, min) {
	return ((x - min) / (max - min));
}

function normalizar_inv(x, max, min) {
	return (1 - ((x - min) / (max - min)));
}

/*
 * 	jplot_graficas
 */
function onJplot() {
	peso = (max - min) / 20;

	//clean chart
	$("#chart1").html("");

	var ecu = function() {
		var data = [[]];
		v = new Array();
		i = 0;
		var valoresY = null;
		if(jplot_grafica==JSPLOT.CAMPANA)
			valoresY = calculateCampana_yLess_yAsterisk(min, max, xmax, ampl);
		else if(jplot_grafica==JSPLOT.CAMPANA_INV)
			valoresY = calculateCampana_yLess_yAsterisk(min, max, xmin, ampl);
		else if(jplot_grafica==JSPLOT.CRECIENTE_CX)
			valoresY = calculateCrecienteCx_yLess_yAsterisk(min,max,satu);
		else if(jplot_grafica==JSPLOT.DECRECIENTE_CX)
			valoresY = calculateDecrecienteCx_yLess_yAsterisk(min,max,satu);
		else if(jplot_grafica==JSPLOT.DECRECIENTE_CV)
			valoresY = calculateDecrecienteCv_yLess_yAsterisk(min,max,satu);
		else if(jplot_grafica==JSPLOT.CRECIENTE_CV)
			valoresY = calculateCrecienteCv_yLess_yAsterisk(min,max,satu);
			
		for( x = min; x <= max; x = x + peso) {

			switch (jplot_grafica) {
				case JSPLOT.CRECIENTE_CX:
					v[i] = ecu_creciente_cx(x, max, satu,valoresY[0],valoresY[1]);
					break;

				case JSPLOT.DECRECIENTE_CX:
					v[i] = ecu_decreciente_cx(x, max, satu,valoresY[0],valoresY[1]);
					break;

				case JSPLOT.DECRECIENTE_CV:
					v[i] = ecu_decreciente_cv(x, max, satu,valoresY[0],valoresY[1]);
					break;

				case JSPLOT.CRECIENTE_CV:
					v[i] = ecu_creciente_cv(x, max, satu,valoresY[0],valoresY[1]);
					break;

				case JSPLOT.CAMPANA:					
					v[i] = ecu_campana(x, max, ampl, xmax,valoresY[0],valoresY[1]);
					break;

				case JSPLOT.CAMPANA_INV:
					v[i] = ecu_campana_inversa(x, max, ampl, xmin,valoresY[0],valoresY[1]);
					break;

				case JSPLOT.DIFUSA:
					function_min_val = min;
					function_max_val = max;
					v[i] = ecu_difusa_logic(x, abcd);
					break;
			}
			l(x + "      " + v[i])
			i++;
		}
		i = 0;
		/*
		 * Normalizar
		 */

		for( x = min; x <= max; x = x + peso) {
			switch (jplot_grafica) {
				case JSPLOT.CRECIENTE_CX:
				case JSPLOT.DECRECIENTE_CX:
				case JSPLOT.DECRECIENTE_CV:
				case JSPLOT.CRECIENTE_CV:
				case JSPLOT.CAMPANA:
					//y = normalizar(v[i], v.max(), v.min());
					y = v[i];
					break;
				case JSPLOT.CAMPANA_INV:
					//y = normalizar_inv(v[i], v.max(), v.min());
					y = v[i];
					break;
				case JSPLOT.DIFUSA:
					y = v[i];
					break;
			}
			data[0].push([x, y]);
			i++;
		}
		return data;
	};
		
	var plot1 = $.jqplot('chart1', [], {
		dataRenderer : ecu,
		seriesDefaults : {
			showMarker : false,
			color : '#81017E',
		},
		grid : {
			gridLineColor : '#a69bab',
			background : '#f5f5f5',
		},
		axes : {
			xaxis : {
				min : min,
				max : max,
				//numberTicks : 6,
				//tickInterval:20,
				tickOptions : {
					formatString : '%.0f'
					//markSize : 0,
				},
			},
			yaxis : {
				min : 0,
				max : 1,
				ticks : ["0", "0.25", "0.50", "0.75", "1"],				
				tickOptions : {
					markSize : 0,
				}
			}
		}
	});
}

function show_jqplot(id) {

	//clean chart
	$("#chart1").html("");
	$('#id_panel').fadeIn('normal');

	$("#div_min_max").hide();
	$("#div_xmax").hide();
	$("#div_xmin").hide();
	$("#div_amplitud").hide();
	$("#div_saturacion").hide();

	$("#div_min_max_difusa").hide();
	$("#div_difusa_a").hide();
	$("#div_difusa_b").hide();
	$("#div_difusa_c").hide();
	$("#div_difusa_d").hide();

	$("#div_add").fadeOut('normal');
	$("#div_add").hide();
	$("#div_view").fadeIn('normal');

	$('#' + toggle + ' img').toggle();

	switch(id) {
		case JSPLOT.CRECIENTE_CX:
			toggle = 1;

			$("#div_min_max").show();
			$("#div_saturacion").show();
			$("#mf").show();
			min = 0;
			max = 200;
			satu = 9;

			$('#sld_min_max').slider("option", "max", max);
			$("#sld_min_max").slider("option", "values", [min, max]);
			$("#sld_saturacion").slider("option", "value", satu);
			$('#sld_saturacion').slider("option", "max", satu);

			$("#txt_min").val(min);
			$("#txt_max").val(max);
			$("#txt_saturacion").val(satu);
			jplot_grafica = JSPLOT.CRECIENTE_CX;
			onJplot();
			break;

		case JSPLOT.DECRECIENTE_CX:
			toggle = 2;

			$("#div_min_max").show();
			$("#div_saturacion").show();
			$("#mf").show();
			min = 0;
			max = 200;
			satu = 9;

			$('#sld_min_max').slider("option", "max", max);
			$("#sld_min_max").slider("option", "values", [min, max]);
			$("#sld_saturacion").slider("option", "value", satu);
			$('#sld_saturacion').slider("option", "max", satu);

			$("#txt_min").val(min);
			$("#txt_max").val(max);
			$("#txt_saturacion").val(satu);
			jplot_grafica = JSPLOT.DECRECIENTE_CX;
			onJplot();
			break;

		case JSPLOT.DECRECIENTE_CV:
			toggle = 3;
			$("#div_min_max").show();
			$("#div_saturacion").show();
			$("#mf").show();
			min = 0;
			max = 200;
			satu = 9;

			$('#sld_min_max').slider("option", "max", max);
			$("#sld_min_max").slider("option", "values", [min, max]);
			$("#sld_saturacion").slider("option", "value", satu);
			$('#sld_saturacion').slider("option", "max", satu);

			$("#txt_min").val(min);
			$("#txt_max").val(max);
			$("#txt_saturacion").val(satu);
			jplot_grafica = JSPLOT.DECRECIENTE_CV;
			onJplot();
			break;

		case JSPLOT.CRECIENTE_CV:
			toggle = 4;
			$("#div_min_max").show();
			$("#div_saturacion").show();
			$("#mf").show();
			min = 0;
			max = 200;
			satu = 9;

			$('#sld_min_max').slider("option", "max", max);
			$("#sld_min_max").slider("option", "values", [min, max]);
			$("#sld_saturacion").slider("option", "value", satu);
			$('#sld_saturacion').slider("option", "max", satu);

			$("#txt_min").val(min);
			$("#txt_max").val(max);
			$("#txt_saturacion").val(satu);
			jplot_grafica = JSPLOT.CRECIENTE_CV;
			onJplot();
			break;

		case JSPLOT.CAMPANA:
			toggle = 5;
			$("#div_min_max").show();
			$("#div_xmax").show();
			$("#div_amplitud").show();
			$("#mf").show();
			/*
			min = 0;
			max = 40;	
			ampl = 20;
			xmax = 10; 
			*/
			min = 0;
			max = 200;
			ampl = 50;
			xmax = 100;
			

			$('#sld_min_max').slider("option", "max", max);
			$("#sld_min_max").slider("option", "values", [min, max]);
			$("#sld_amplitud").slider("option", "value", ampl);
			$('#sld_amplitud').slider("option", "max", ampl);
			$("#sld_xmax").slider("option", "value", ampl);
			$('#sld_xmax').slider("option", "max", max);

			$("#txt_min").val(min);
			$("#txt_max").val(max);
			$("#txt_amplitud").val(ampl);
			$("#txt_xmax").val(xmax);
			jplot_grafica = JSPLOT.CAMPANA;
			onJplot();

			break;

		case JSPLOT.CAMPANA_INV:
			toggle = 6;
			$("#div_min_max").show();
			$("#div_xmin").show();
			$("#div_amplitud").show();
			$("#mf").show();
			min = 0;
			max = 200;
			ampl = 50;
			xmin = 100;

			$('#sld_min_max').slider("option", "max", max);
			$("#sld_min_max").slider("option", "values", [min, max]);
			$("#sld_amplitud").slider("option", "value", ampl);
			$('#sld_amplitud').slider("option", "max", ampl);
			$("#sld_xmin").slider("option", "value", xmin);

			$("#txt_min").val(min);
			$("#txt_max").val(max);
			$("#txt_amplitud").val(ampl);
			$("#txt_xmin").val(xmin);
			jplot_grafica = JSPLOT.CAMPANA_INV;
			onJplot();

			break;

		case JSPLOT.DIFUSA:
			toggle = 7;
			$("#div_min_max_difusa").show();
			$("#div_difusa_a").show();
			$("#div_difusa_b").show();
			$("#div_difusa_c").show();
			$("#div_difusa_d").show();
			$("#mf").show();
			min = 0;
			max = 1000;
			abcd = [0, 400, 600, 1000];

			$("#sld_min_max_difusa").slider("option", "values", [min, max]);
			$('#sld_min_max_difusa').slider("option", "max", max);

			$("#sld_difusa_a").slider("option", "value", abcd[0]);
			$('#sld_difusa_a').slider("option", "max", abcd[0]);

			$("#sld_difusa_b").slider("option", "value", abcd[1]);
			$('#sld_difusa_b').slider("option", "max", abcd[1]);

			$("#sld_difusa_c").slider("option", "value", abcd[2]);
			$('#sld_difusa_c').slider("option", "max", abcd[2]);

			$("#sld_difusa_d").slider("option", "value", abcd[3]);
			$('#sld_difusa_d').slider("option", "max", abcd[3]);

			$("#txt_min_difusa").val(min);
			$("#txt_max_difusa").val(max);

			$("#txt_difusa_a").val(abcd[0]);
			$("#txt_difusa_b").val(abcd[1]);
			$("#txt_difusa_c").val(abcd[2]);
			$("#txt_difusa_d").val(abcd[3]);
			jplot_grafica = JSPLOT.DIFUSA;
			onJplot();

			break;
	}
	$('#' + toggle + ' img').toggle();
}

function show_jqplot2(id) {

	//clean chart
	$("#chart1").html("");
	$('#id_panel').fadeIn('normal');

	$("#div_min_max").hide();
	$("#div_xmax").hide();
	$("#div_xmin").hide();
	$("#div_amplitud").hide();
	$("#div_saturacion").hide();

	$("#div_min_max_difusa").hide();
	$("#div_difusa_a").hide();
	$("#div_difusa_b").hide();
	$("#div_difusa_c").hide();
	$("#div_difusa_d").hide();

	$("#div_add").fadeOut('normal');
	$("#div_add").hide();
	$("#div_view").fadeIn('normal');

	$('#' + toggle + ' img').toggle();

	switch(id) {

		case JSPLOT.CRECIENTE_CX:
			toggle = 1;
			$("#div_min_max").show();
			$("#div_saturacion").show();
			$("#mf").show();

			$("#sld_min_max").slider("option", "values", [min, max]);
			$("#sld_saturacion").slider("option", "value", satu);

			$("#txt_min").val(min);
			$("#txt_max").val(max);
			$("#txt_saturacion").val(satu);
			jplot_grafica = JSPLOT.CRECIENTE_CX;
			onJplot();
			break;

		case JSPLOT.DECRECIENTE_CX:
			toggle = 2;
			$("#div_min_max").show();
			$("#div_saturacion").show();
			$("#mf").show();

			$("#sld_min_max").slider("option", "values", [min, max]);
			$("#sld_saturacion").slider("option", "value", satu);

			$("#txt_min").val(min);
			$("#txt_max").val(max);
			$("#txt_saturacion").val(satu);
			jplot_grafica = JSPLOT.DECRECIENTE_CX;
			onJplot();
			break;

		case JSPLOT.DECRECIENTE_CV:
			toggle = 3;
			$("#div_min_max").show();
			$("#div_saturacion").show();
			$("#mf").show();

			$("#sld_min_max").slider("option", "values", [min, max]);
			$("#sld_saturacion").slider("option", "value", satu);
			$("#txt_min").val(min);
			$("#txt_max").val(max);
			$("#txt_saturacion").val(satu);
			jplot_grafica = JSPLOT.DECRECIENTE_CV;
			onJplot();
			break;

		case JSPLOT.CRECIENTE_CV:
			toggle = 4;

			$("#div_min_max").show();
			$("#div_saturacion").show();
			$("#mf").show();

			$("#sld_min_max").slider("option", "values", [min, max]);
			$("#sld_saturacion").slider("option", "value", satu);
			$("#txt_min").val(min);
			$("#txt_max").val(max);
			$("#txt_saturacion").val(satu);
			jplot_grafica = JSPLOT.CRECIENTE_CV;
			onJplot();
			break;

		case JSPLOT.CAMPANA:
			toggle = 5;			
			$("#div_min_max").show();
			$("#div_xmax").show();
			$("#div_amplitud").show();
			$("#mf").show();

			$("#sld_min_max").slider("option", "values", [min, max]);
			$("#sld_amplitud").slider("option", "value", ampl);
			$("#sld_xmax").slider("option", "value", xmax);

			$("#txt_min").val(min);
			$("#txt_max").val(max);
			$("#txt_amplitud").val(ampl);
			$("#txt_xmax").val(xmax);
			jplot_grafica = JSPLOT.CAMPANA;
			onJplot();

			break;

		case JSPLOT.CAMPANA_INV:
			toggle = 6;
			$("#div_min_max").show();
			$("#div_xmin").show();
			$("#div_amplitud").show();
			$("#mf").show();

			$("#sld_min_max").slider("option", "values", [min, max]);
			$("#sld_amplitud").slider("option", "value", ampl);
			$("#sld_xmin").slider("option", "value", xmin);

			$("#txt_min").val(min);
			$("#txt_max").val(max);
			$("#txt_amplitud").val(ampl);
			$("#txt_xmin").val(xmin);
			jplot_grafica = JSPLOT.CAMPANA_INV;
			onJplot();

			break;

		case JSPLOT.DIFUSA:
			toggle = 7;
			$("#div_min_max_difusa").show();
			$("#div_difusa_a").show();
			$("#div_difusa_b").show();
			$("#div_difusa_c").show();
			$("#div_difusa_d").show();
			$("#mf").show();

			$("#sld_min_max_difusa").slider("option", "values", [min, max]);
			$("#sld_difusa_a").slider("option", "value", abcd[0]);
			$("#sld_difusa_b").slider("option", "value", abcd[1]);
			$("#sld_difusa_c").slider("option", "value", abcd[2]);
			$("#sld_difusa_d").slider("option", "value", abcd[3]);

			$("#txt_min_difusa").val(min);
			$("#txt_max_difusa").val(max);

			$("#txt_difusa_a").val(abcd[0]);
			$("#txt_difusa_b").val(abcd[1]);
			$("#txt_difusa_c").val(abcd[2]);
			$("#txt_difusa_d").val(abcd[3]);
			jplot_grafica = JSPLOT.DIFUSA;
			onJplot();

			break;
	}
	$('#' + toggle + ' img').toggle();
}


$(document).ready(function() {

	$("#sld_min_max").slider({
		range : true,
		min : 0,
		//max : 1000,
		values : [0, 20],
		step : 1,
		slide : function(event, ui) {
			$("#txt_min").val(ui.values[0]);
			$("#txt_max").val(ui.values[1]);
		},
		stop : function(event, ui) {
			$("#txt_min").val(ui.values[0]);
			$("#txt_max").val(ui.values[1]);
			_min = parseFloat(ui.values[0]);
			_max = parseFloat(ui.values[1]);
			
			if(_max > (_min + 1)) {
				min = parseFloat(ui.values[0]);
				max = parseFloat(ui.values[1]);
			}
			
			
			$('#sld_xmax').slider("option", "max", max);			
			if(xmax>max){
				$("#txt_xmax").val(max);
				$("#sld_xmax").slider("option", "value", max);	
			}
			
			/*
			if(xmin<min){
				$("#txt_xmin").val(min);
				$("#sld_xmin").slider("option", "value", min);	
			}			
			*/
			
			onJplot();
		}
	});

	$("#sld_xmin").slider({
		animate : true,
		range : "min",
		min : 0,
		//max : 200,
		step : 1,

		slide : function(event, ui) {
			$("#txt_xmin").val(ui.value);
		},
		stop : function(event, ui) {
			$("#txt_xmin").val(ui.value);
			xmin = parseFloat(ui.value);
			
			onJplot();
		},
	});

	$("#sld_xmax").slider({
		animate : true,
		range : "min",
		min : 0,
		//max : 200,
		step : 1,
		slide : function(event, ui) {
			$("#txt_xmax").val(ui.value);
		},
		stop : function(event, ui) {
			$("#txt_xmax").val(ui.value);
			xmax = parseFloat(ui.value);
			onJplot();
		},
	});

	$("#sld_amplitud").slider({
		animate : true,
		range : "min",
		min : 0,
		//max : 100,
		step : 1,

		slide : function(event, ui) {
			$("#txt_amplitud").val(ui.value);
		},
		stop : function(event, ui) {
			$("#txt_amplitud").val(ui.value);
			ampl = parseFloat(ui.value);
			onJplot();
		},
	});

	$("#sld_saturacion").slider({
		animate : true,
		range : "min",
		min : 0,
		//max : 10,
		step : 1,

		slide : function(event, ui) {
			$("#txt_saturacion").val(ui.value);
		},
		stop : function(event, ui) {
			$("#txt_saturacion").val(ui.value);
			satu = parseFloat(ui.value);
			onJplot();
		},
	});

	$("#sld_min_max_difusa").slider({
		range : true,
		min : 0,
		//max : 1000,
		step : 1,
		values : [0, 20],

		slide : function(event, ui) {
			$("#txt_min_difusa").val(ui.values[0]);
			$("#txt_max_difusa").val(ui.values[1]);
		},
		stop : function(event, ui) {
			$("#txt_min_difusa").val(ui.values[0]);
			$("#txt_max_difusa").val(ui.values[1]);
			_min = parseFloat(ui.values[0]);
			_max = parseFloat(ui.values[1]);

			if(_max > (_min + 0.10)) {
				min = parseFloat(ui.values[0]);
				max = parseFloat(ui.values[1]);
			}
			onJplot();
		}
	});

	$("#sld_difusa_a").slider({
		animate : true,
		range : "min",
		min : 0,
		//max : 1000,
		step : 1,

		slide : function(event, ui) {
			$("#txt_difusa_a").val(ui.value);
		},
		stop : function(event, ui) {
			$("#txt_difusa_a").val(ui.value);
			abcd[0] = parseFloat(ui.value);
			onJplot();
		}
	});

	$("#sld_difusa_b").slider({
		animate : true,
		range : "min",
		//max : 1,
		step : 1,

		slide : function(event, ui) {
			$("#txt_difusa_b").val(ui.value);
		},
		stop : function(event, ui) {
			$("#txt_difusa_b").val(ui.value);
			abcd[1] = parseFloat(ui.value);
			onJplot();
		}
	});

	$("#sld_difusa_c").slider({
		animate : true,
		range : "min",
		//max : 1,
		step : 1,

		slide : function(event, ui) {
			$("#txt_difusa_c").val(ui.value);
		},
		stop : function(event, ui) {
			$("#txt_difusa_c").val(ui.value);
			abcd[2] = parseFloat(ui.value);
			onJplot();
		}
	});

	$("#sld_difusa_d").slider({
		animate : true,
		range : "min",
		//max : 1,
		step : 1,

		slide : function(event, ui) {
			$("#txt_difusa_d").val(ui.value);
		},
		stop : function(event, ui) {
			$("#txt_difusa_d").val(ui.value);
			abcd[3] = parseFloat(ui.value);
			onJplot();
		}
	});

	/*
	 * Input text enter
	 */
	$('#txt_min').bind('keypress focusout', function(event) {
		if((event.type == "keypress" && event.which == ENTER) || event.type == "focusout") {
			min = $(this).val();
			max = $('#sld_min_max').slider( "option", "values")[1];
			if(isNumeric(min) && min >= 0 && min < max) {
				min = parseFloat(min);
				$('#sld_min_max').slider("values", [min, max]);
				onJplot();
			} else {
				min = $('#sld_min_max').slider( "option", "values")[0];
				$('#txt_min').val(min)
			}
		}
	});

	$('#txt_max').bind('keypress focusout', function(event) {
		if((event.type == "keypress" && event.which == ENTER) || event.type == "focusout") {
			max = $(this).val();
			min = $('#sld_min_max').slider( "option", "values")[0];

			if(isNumeric(max) && max > min) {
				max = parseFloat(max);
				$('#sld_min_max').slider("option", "max", max);
				$('#sld_min_max').slider("values", [min, max]);
				onJplot();
			} else {
				max = $('#sld_min_max').slider( "option", "values")[1];
				$('#txt_max').val(max)
			}
		}
	});

	$('#txt_min_difusa').bind('keypress focusout', function(event) {
		if((event.type == "keypress" && event.which == ENTER) || event.type == "focusout") {
			min = $(this).val();
			max = $('#sld_min_max_difusa').slider( "option", "values")[1];
			if(isNumeric(min) && min >= 0 && min < max) {
				min = parseFloat(min);
				$('#sld_min_max_difusa').slider("values", [min, max]);
				onJplot();
			} else {
				min = $('#sld_min_max_difusa').slider( "option", "values")[0];
				$('#txt_min_difusa').val(min)
			}

		}
	});

	$('#txt_max_difusa').bind('keypress focusout', function(event) {
		if((event.type == "keypress" && event.which == ENTER) || event.type == "focusout") {
			max = $(this).val();
			min = $('#sld_min_max_difusa').slider( "option", "values")[0];

			if(isNumeric(max) && max > min) {
				max = parseFloat(max);
				$('#sld_min_max_difusa').slider("option", "max", max);
				$('#sld_min_max_difusa').slider("values", [min, max]);
				onJplot();
			} else {
				max = $('#sld_min_max_difusa').slider( "option", "values")[1];
				$('#txt_max_difusa').val(max)
			}
		}
	});

	$('#txt_xmax').bind('keypress focusout', function(event) {
		if((event.type == "keypress" && event.which == ENTER) || event.type == "focusout") {
			xmax = $(this).val();

			if(isNumeric(xmax) && xmax >= min && xmax <= max) {
				$('#sld_xmax').slider("option", "max", xmax);
				$('#sld_xmax').slider("value", xmax);
				xmax = parseFloat(xmax);
				onJplot();
			} else {
				xmax = $('#sld_xmax').slider("option", "value");
				$('#txt_xmax').val(xmax)
			}
		}
	});

	$('#txt_xmin').bind('keypress focusout', function(event) {
		if((event.type == "keypress" && event.which == ENTER) || event.type == "focusout") {
			xmin = $(this).val();

			if(isNumeric(xmin) && xmin >= min && xmin <= max) {
				$('#sld_xmin').slider("value", xmin);
				xmin = parseFloat(xmin);
				onJplot();
			} else {
				xmin = $('#sld_xmin').slider("option", "value");
				$('#txt_xmin').val(xmin)
			}
		}
	});

	$('#txt_amplitud').bind('keypress focusout', function(event) {
		if((event.type == "keypress" && event.which == ENTER) || event.type == "focusout") {
			a = $(this).val();

			if(isNumeric(a) && a >= 0) {
				$('#sld_amplitud').slider("option", "max", a);
				$('#sld_amplitud').slider("value", a);
				ampl = parseFloat(a);
				onJplot();
			} else {
				a = $('#sld_amplitud').slider("option", "value");
				$('#txt_amplitud').val(a)
			}
		}
	});

	$('#txt_saturacion').bind('keypress focusout', function(event) {
		if((event.type == "keypress" && event.which == ENTER) || event.type == "focusout") {
			s = $(this).val();

			if(isNumeric(s) && s >= 0) {
				$('#sld_saturacion').slider("option", "max", s);
				$('#sld_saturacion').slider("value", s);
				satu = parseFloat(s);
				onJplot();
			} else {
				s = $('#sld_saturacion').slider("option", "value");
				$('#txt_saturacion').val(s)
			}
		}
	});

	$('#txt_difusa_a').bind('keypress focusout', function(event) {
		if((event.type == "keypress" && event.which == ENTER) || event.type == "focusout") {
			v = $(this).val();
			$('#sld_difusa_a').slider("option", "max", v);
			$('#sld_difusa_a').slider("value", v);
			abcd[0] = parseFloat(v);
			onJplot();
		}
	});

	$('#txt_difusa_b').bind('keypress focusout', function(event) {
		if((event.type == "keypress" && event.which == ENTER) || event.type == "focusout") {
			v = $(this).val();
			$('#sld_difusa_b').slider("option", "max", v);
			$('#sld_difusa_b').slider("value", v);
			abcd[1] = parseFloat(v);
			onJplot();
		}
	});
	$('#txt_difusa_c').bind('keypress focusout', function(event) {
		if((event.type == "keypress" && event.which == ENTER) || event.type == "focusout") {
			v = $(this).val();
			$('#sld_difusa_c').slider("option", "max", v);
			$('#sld_difusa_c').slider("value", v);
			abcd[2] = parseFloat(v);
			onJplot();
		}
	});

	$('#txt_difusa_d').bind('keypress focusout', function(event) {
		if((event.type == "keypress" && event.which == ENTER) || event.type == "focusout") {
			v = $(this).val();
			$('#sld_difusa_d').slider("option", "max", v);
			$('#sld_difusa_d').slider("value", v);
			abcd[3] = parseFloat(v);
			onJplot();
		}
	});
});