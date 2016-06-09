$(document).ready(function () {
    // using jQuery

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    $(document).click(function (e) {
        var $that = $(e.target);
        // -----------------------------------------General-----------------------------------------
        if ($that.closest("#general_analysis")[0]){      
            $("#spinner").show();
              var selected_id = [];
              var selected_variable = [];
              var selected_starttime = [];
              var selected_endtime = [];
              var removeoutlier = [];
              var fillingData = [];

              $(".ck_ana:checked").each(function (index, elem) {
                var arr = elem.id.split("_");
                selected_id.push(String(arr[1]));
                selected_variable.push(String(arr[2]));
                selected_starttime.push(String(document.getElementById("Starttime_" + arr[1] + "_" + arr[2]).value));
                selected_endtime.push(String(document.getElementById("Endtime_" + arr[1] + "_" + arr[2]).value));
                  
                if(document.getElementById(elem.id.replace('Ana', 'Removeoutlier')).checked == true){
                    removeoutlier.push("True");
                }else{
                    removeoutlier.push("False");
                }
                
                if(document.getElementById(elem.id.replace('Ana', 'fillingData')).checked == true){
                    fillingData.push("True");
                }else{
                    fillingData.push("False");
                }
              });
            
            var timestep =  String($(document.getElementById("timestep")).val());
            
            id_container = "general_content";
            
            $.ajax({
                async:true,
                type: 'POST',
                url: 'general_multivariable_statistic',
                data: {
                    'selected_id[]': selected_id,
                    'selected_variable[]': selected_variable ,
                    'selected_starttime[]':selected_starttime,
                    'selected_endtime[]': selected_endtime,
                    'removeoutlier[]':removeoutlier,
                    'fillingData[]':fillingData,
                    'timestep': timestep,
    
                },
                complete: function() {
                $("#spinner").hide();
                },  
                success: function (data) {
                    $(document.getElementById(id_container)).append(data)

                },
                error: function () {
                    alert('Failed in sending ajax request')
                },
                dataType: 'html',
                headers: {
                    'X-CSRFToken': csrftoken
                }
            });
        } else if ($that.closest("#linearRegressionAnalysis")[0]) {
            $("#spinner").show();
              var selected_id = [];
              var selected_variable = [];
              var selected_starttime = [];
              var selected_endtime = [];
              var removeoutlier = [];
              var fillingData = [];
                
              $(".ck_ana:checked").each(function (index, elem) {
                var arr = elem.id.split("_");
                selected_id.push(String(arr[1]));
                selected_variable.push(String(arr[2]));
                selected_starttime.push(String(document.getElementById("Starttime_" + arr[1] + "_" + arr[2]).value));
                selected_endtime.push(String(document.getElementById("Endtime_" + arr[1] + "_" + arr[2]).value));
                  
                if(document.getElementById(elem.id.replace('Ana', 'Removeoutlier')).checked == true){
                    removeoutlier.push("True");
                }else{
                    removeoutlier.push("False");
                }
                  
                if(document.getElementById(elem.id.replace('Ana', 'fillingData')).checked == true){
                    fillingData.push("True");
                }else{
                    fillingData.push("False");
                }
                  
              });
            
            var timestep =  String($(document.getElementById("timestep")).val());
            var dependentVariable = String($(document.getElementById("dependentVariable")).val());
            
            id_container = "linearRegressionContent";
            
                                                                                                                        
            
            $.ajax({
                async:true,
                type: 'POST',
                url: 'multiLinearRegression',
                data: {
                    'selected_id[]': selected_id,
                    'selected_variable[]': selected_variable ,
                    'selected_starttime[]':selected_starttime,
                    'selected_endtime[]': selected_endtime,
                    'removeoutlier[]':removeoutlier,
                    'fillingData[]':fillingData,
                    'timestep': timestep,
                    'dependentVariable': dependentVariable,                                                            
                },
                complete: function() {
                $("#spinner").hide();
                },  
                success: function (data) {
                    $(document.getElementById(id_container)).append(data)

                },
                error: function () {
                    alert('Failed in sending ajax request')
                },
                dataType: 'html',
                headers: {
                    'X-CSRFToken': csrftoken
                }
            });
        }else if($that.closest("#multipleBoxPlotAnalysis")[0]){
            $("#spinner").show();
              var selected_id = [];
              var selected_variable = [];
              var selected_starttime = [];
              var selected_endtime = [];
              var removeoutlier = [];
              var fillingData = [];
                
              $(".ck_ana:checked").each(function (index, elem) {
                var arr = elem.id.split("_");
                selected_id.push(String(arr[1]));
                selected_variable.push(String(arr[2]));
                selected_starttime.push(String(document.getElementById("Starttime_" + arr[1] + "_" + arr[2]).value));
                selected_endtime.push(String(document.getElementById("Endtime_" + arr[1] + "_" + arr[2]).value));
                  
                if(document.getElementById(elem.id.replace('Ana', 'Removeoutlier')).checked == true){
                    removeoutlier.push("True");
                }else{
                    removeoutlier.push("False");
                }
                  
                if(document.getElementById(elem.id.replace('Ana', 'fillingData')).checked == true){
                    fillingData.push("True");
                }else{
                    fillingData.push("False");
                }
                  
              });
            
            var timestep =  String($(document.getElementById("timestep")).val());
            var dependentVariable = String($(document.getElementById("dependentVariable")).val());
            
            id_container = "multipleBoxPlotContent";                                                                                                                           
            $.ajax({
                async:true,
                type: 'POST',
                url: 'multipleBoxPlot',
                data: {
                    'selected_id[]': selected_id,
                    'selected_variable[]': selected_variable ,
                    'selected_starttime[]':selected_starttime,
                    'selected_endtime[]': selected_endtime,
                    'removeoutlier[]':removeoutlier,
                    'fillingData[]':fillingData,
                    'timestep': timestep,
                    'dependentVariable': dependentVariable,                                                            
                },
                complete: function() {
                $("#spinner").hide();
                },  
                success: function (data) {
                    $(document.getElementById(id_container)).append(data)

                },
                error: function () {
                    alert('Failed in sending ajax request')
                },
                dataType: 'html',
                headers: {
                    'X-CSRFToken': csrftoken
                }
            });
            
            
        }
    });


});