(function($) {
	var options = {
		series : {
			threshold : null
		}
	};

	function init(plot) {

		function thresholdData(plot, s, datapoints) {
			if(!s.threshold) {
				return;
			}
			if(s.threshold.above) {
				thresholdData2(plot, s, datapoints, true, s.threshold.above.color, s.threshold.above.limit);
			}
			if(s.threshold.below) {
				thresholdData2(plot, s, datapoints, false, s.threshold.below.color, s.threshold.below.limit);
			}
		}

		function thresholdData2(plot, s, datapoints, isAbove, color, limit) {

			var ps = datapoints.pointsize, i, x, y, p, prevp, thresholded = $.extend({}, s);
			thresholded.datapoints = {
				points : [],
				pointsize : ps
			};
			thresholded.label = null;
			thresholded.color = color;
			thresholded.threshold = null;
			thresholded.originSeries = s;
			thresholded.data = [];

			var origpoints = datapoints.points, addCrossingPoints = s.lines.show;
			threspoints = [];
			newpoints = [];

			for( i = 0; i < origpoints.length; i += ps) {
				x = origpoints[i]
				y = origpoints[i + 1];
				prevp = p;
				if( isAbove ? (x > limit) : (x <= limit)) {
					p = threspoints;
				} else {
					p = newpoints;
				}
				if(addCrossingPoints && prevp != p && x != null && i > 0 && origpoints[i - ps] != null) {
					var interx = (x - origpoints[i - ps]) / (y - origpoints[i - ps + 1]) * (limit - y) + x;

					// interpolation point at end of segment
					prevp.push(interx);
					prevp.push(limit);
					for( m = 2; m < ps; ++m) {
						prevp.push(origpoints[i + m]);
					}
					// mark start of new segment
					for( m = 0; m < ps; ++m) {
						p.push(null);
					}
					// interpolation point at start of segment
					p.push(interx);
					p.push(limit);
					for( m = 2; m < ps; ++m) {
						p.push(origpoints[i + m]);
					}
				}
				p.push(x);
				p.push(y);
				for( m = 2; m < ps; ++m) {
					p.push(origpoints[i + m]);
				}
			}
			datapoints.points = newpoints;
			thresholded.datapoints.points = threspoints;
			if(thresholded.datapoints.points.length > 0) {
				plot.getData().push(thresholded);
			}
		}


		plot.hooks.processDatapoints.push(thresholdData);
	}


	$.plot.plugins.push({
		init : init,
		options : options,
		name : 'threshold',
		version : '1.1'
	});
})(jQuery);