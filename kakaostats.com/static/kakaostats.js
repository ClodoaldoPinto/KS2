function textboxHint(id, options, blurClass) {
    var o = { selector: 'input:text[title]', blurClass:blurClass };
    $e = $('#'+id);
    $.extend(true, o, options || {});

    if ($e.is(':text')) {
      if (!$e.attr('title')) $e = null;
    } else {
      $e = $e.find(o.selector);
    }
    if ($e) {
      $e.each(function() {
      var $t = $(this);
      if ($.trim($t.val()).length == 0) { $t.val($t.attr('title')); }
      if ($t.val() == $t.attr('title')) {
	$t.addClass(o.blurClass);
      } else {
        $t.removeClass(o.blurClass);
      }

     $t.focus(function() {
	if ($.trim($t.val()) == $t.attr('title')) {
	  $t.val('');
	  $t.removeClass(o.blurClass);
	}
	}).blur(function() {
	  var val = $.trim($t.val());
	  if (val.length == 0 || val == $t.attr('title')) {
	    $t.val($t.attr('title'));
	    $t.addClass(o.blurClass);
	  }
	});

         // empty the text box on form submit
	$(this.form).submit(function(){
	  if ($.trim($t.val()) == $t.attr('title')) $t.val('');
	});
   });
 }
}

var blurClass = 'blur';
$(document).ready(
    function() {
        textboxHint('search', '', blurClass);
    }
);

function setCookie(name, value, days) {
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        var expires = ';expires=' + date.toGMTString();
    }
    else var expires = '';
    document.cookie = name + '=' + value + expires + '; path=/';
}

function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}

function headerMatrixBuilder (table) {
    var $tr, $th, rowspan, colspan, $cell, i, j, k, l, m;
    $tr = $(table).eq(0).children('thead').children('tr');
    headerMatrix = new Array($tr.length);
    for (i = 0; i < $tr.length; i++) {
	headerMatrix[i] = new Array();
    }
    for (i = 0; i < $tr.length; i++) {
	$th = $tr.eq(i).children('th');
        m = 0;
	for (j = 0; j < $th.length; j++) {
	    $cell = $th.eq(j);
	    colspan = $cell.attr('colspan') || 1;
	    rowspan = $cell.attr('rowspan') || 1;
	    for (k = 0; k < colspan; k++) {
		while (i > 0 && headerMatrix[i][m] != undefined) {
		    m++;
		}
		for (l = 0; l < rowspan; l++) {
		    headerMatrix[l + i][m] = [i, j, true];
		}
	        m++;
	    }
	}
    }
    //mostraHM(headerMatrix);
}

function toggleColumn(table, column, pageName, load) {
    var hmCell, $th, colspan, visible, $tr, toggleColumnArray;
    for (var i = 0; i < headerMatrix.length; i++) {
	hmCell = headerMatrix[i][column];
	visible = hmCell[2] = !hmCell[2];
	for (var j = 0; j < $(table).length; j++) {
	    $th = $(table).eq(j).children('thead').children('tr').eq(hmCell[0]).children('th').eq(hmCell[1]);
	    if (i == hmCell[0]) {
		colspan = $th.attr('colspan') || 1;
		if (visible) colspan++;
		else colspan--;
		$th.attr('colspan', colspan);
		if (colspan == 0) $th.addClass('hideCell');
		else if (visible) $th.removeClass('hideCell');
	    }
	}
    }
    $tr = $(table).children('tbody').children('tr');
    $tr.each(function(i){$(this).children('td').eq(column).toggleClass('hideCell');});
    if (!load || load == null) setToggleArray(column, visible, pageName);
}

function setToggleArray(column, visible, pageName) {
    var toggleColumnArray = getToggleArray(pageName);
    toggleColumnArray[column] = visible;
    setCookie('toggleColumn' + pageName, JSON.stringify(toggleColumnArray), 365);
}

function getToggleArray(pageName, toggleDefaultArray) {
    var toggleColumnArray = $.parseJSON(getCookie('toggleColumn' + pageName));
    if (toggleColumnArray == null) {
	if (toggleDefaultArray == null)
	    toggleColumnArray = [true,true,true,true,true,true,true,true,true,true,true,true,true];
	else toggleColumnArray = toggleDefaultArray;
	setCookie('toggleColumn' + pageName, JSON.stringify(toggleColumnArray), 365);
    }
    return toggleColumnArray;
}

function toggleColumns(table, pageName, toggleColumnIds, toggleDefaultArray) {
    var toggleColumnArray = getToggleArray(pageName, toggleDefaultArray);
    toggleColumnIds = toggleColumnIds.split(',');
    for (var i = 0; i < toggleColumnArray.length; i++) {
	if (!toggleColumnArray[i]) {
	    toggleColumn(table, i, pageName, true);
	    if (toggleColumnIds[i] != '') {
	        $('#' + toggleColumnIds[i]).removeAttr('checked');
	    }
	}
    }
}

function destaque(event) {
    $(this).toggleClass('destaque');
}

function mostraHM(hm) {
    var cell, s = '';
    for (var j = 0; j < 3; j++) {
	for (var k = 0; k < 13; k++) {
	    if (hm[j][k] == undefined)
		cell = ['u','u'];
	    else
		cell = hm[j][k];
	    s += '[' + cell + ']';
	}
	s += '\n';
    }
    alert(s);
}

function showChart() {
    var $chartDiv = $('#chartDiv');
    var left = Math.floor(($chartDiv.outerWidth() - 640) / 2);
    var top = Math.floor(($chartDiv.outerHeight() - 300) / 2);
    $('#chartImage').css('left', left).css('top', top);
    $chartDiv
        .css('z-index', '100').fadeTo('fast', 1)
        .on('click', function() {
            $chartDiv.fadeOut('fast');
            $chartDiv.off('click');
        })
	;
}

/* ***  Header fixer  *** */

(function() {
    var flag=false;
    var tid; //table id as defined on html page
    var sheight;
    function ge$(d) {return document.getElementById(d);}
    this.scrollHeader = function() {
        if(flag) {
            return;
        }
        var fh=ge$('Scroller:fx');
        var sd=ge$(tid+':scroller');
        fh.style.left=(0-sd.scrollLeft)+'px';
    };
    function addScrollerDivs() {
        if(ge$(tid+':scroller')) {
            return;
        }
        var sd=document.createElement("div");
        var tb=ge$(tid);
        sd.style.height=sheight+"px";
        sd.style.overflow='visible';
        sd.style.overflowX='auto';
        sd.style.overflowY='auto';
        sd.style.width=tb.width;
        sd.id=tid+':scroller';
        sd.onscroll=scrollHeader;

        var tb2=tb.cloneNode(true);
        sd.appendChild(tb2);
        tb.parentNode.replaceChild(sd,tb);
        var sd2=document.createElement("div");
        sd2.id='Scroller:fx:OuterDiv';
        sd2.style.cssText='position:relative;width:100%;overflow:hidden;overflow-x:hidden;padding:0px;margin:0px;';
        sd2.innerHTML='<div id="Scroller:fx" style="position:relative;width:9999px;padding:0px;margin-left:0px;"><div id="Scroller:content"><font size="3" color="red">Please wait while loading the table..</font></div></div>';
        sd.parentNode.insertBefore(sd2,sd);
    }
    function fxheader() {
        if(flag) {return;}
        flag=true;
        var tbDiv=ge$(tid);
        tbDiv.rows[0].style.display='';
        var twp=tbDiv.width;
        var twi=parseInt(twp);
        if(twp.indexOf("%") > 0) {
            twi=((ge$('Scroller:fx:OuterDiv').offsetWidth * twi) / 100)-20;
            twp=twi+'px';
            tbDiv.style.width=twp;
        }
        var oc=tbDiv.rows[0].cells;
        var fh=ge$('Scroller:fx');
        var tb3=tbDiv.cloneNode(true);
        tb3.id='Scroller:content';
        tb3.style.marginTop = '0px';
        fh.replaceChild(tb3,ge$('Scroller:content'));
		var theadLength = $('#' + tid + ' thead tr').length;
        var theadHeight = 0;
		for (var i = 0; i < theadLength; i++) {
			theadHeight += tbDiv.rows[i].offsetHeight;
		}
		theadHeight += theadLength - 1;
        ge$('Scroller:fx:OuterDiv').style.height = theadHeight + 'px';
        tbDiv.style.marginTop = "-" + theadHeight + "px";
        scrollHeader();
        if(tbDiv.offsetHeight < sheight) {
            ge$(tid+':scroller').style.height=tbDiv.offsetHeight + 'px';
        }
        window.onresize=fxheader;
        flag=false;
    }
    this.fxheaderInit = function(_tid,_sheight) {
        tid=_tid;
        sheight=_sheight;
        flag=false;
        addScrollerDivs();
        fxheader();
    };
})();
