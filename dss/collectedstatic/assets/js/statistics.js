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
        // -----------------------------------------Extract data-----------------------------------------

        if ($that.closest("#extract_data")[0]) {
            $("#spinner").show();
            var id = document.getElementById("id").value;
            var varibale = document.getElementById("variable").value;
            var start_time = document.getElementById("starttime").value;
            var end_time = document.getElementById("endtime").value;
            var timstep = ($that.closest("#extract_data")[0]).getAttribute("timestep");
            
            if(document.getElementById("removeOutliers").checked == true){
                var removeOutliers = "True";
            }else{
                var removeOutliers = "False";
            };
            
            if(document.getElementById("fillingData").checked == true){
                var fillingData = "True";
            }else{
                var fillingData = "False";
            };
            
            
            $.ajax({
                async:true,
                type: 'POST',
                url: 'extract_data',
                data: {
                    'id':document.getElementById("id").value ,
                    'variable': ($that.closest("#extract_data")[0]).getAttribute("variable"),
                    'starttime': ($that.closest("#extract_data")[0]).getAttribute("starttime"),
                    'endtime': ($that.closest("#extract_data")[0]).getAttribute("endtime"),
                    'timestep': ($that.closest("#extract_data")[0]).getAttribute("timestep"),
                    'removeOutliers': removeOutliers,
                    'fillingData':fillingData
                },
                complete: function() {
                $("#spinner").hide();
                },  
                success: function (url) {
                    window.location = url;
                },
                error: function () {
                    alert('Failed in sending ajax request')
                },
                dataType: 'html',
                headers: {
                    'X-CSRFToken': csrftoken
                }
            });
        };
        // -----------------------------------------Monthly Graph-----------------------------------------
        if ($that.closest("#monthly_statistic")[0] || $that.closest("#yearly_statistic")[0] || $that.closest("#daily_statistic")[0] || $that.closest("#hourly_statistic")[0]|| $that.closest("#initial_statistic")[0]) {      
            $("#spinner").show();
            var id = String(document.getElementById("id").value);
            var varibale = String(document.getElementById("variable").value);
            var start_time = String(document.getElementById("starttime").value);
            var end_time = String(document.getElementById("endtime").value);
            var id_container;
            
            if(document.getElementById("removeOutliers").checked == true){
                var removeOutliers = "True";
            }else{
                var removeOutliers = "False";
            };
            
            if(document.getElementById("fillingData").checked == true){
                var fillingData = "True";
            }else{
                var fillingData = "False";
            };
            
            if(document.getElementById('linear_regression').checked == true){
                var linear_regression = "True";
            }else{
                var linear_regression = "False";
            };
            
            if ($that.closest("#yearly_statistic")[0]) {
                var timestep = "AS";
                id_container = "yearly_content";
            } else if ($that.closest("#monthly_statistic")[0]) {
                var timestep = "M";
                id_container = "monthly_content";
            } else if ($that.closest("#daily_statistic")[0]) {
                var timestep = "D";
                id_container = "daily_content";
            } else if ($that.closest("#hourly_statistic")[0]) {
                var timestep = "H";
                id_container = "hourly_content";
            }else if ($that.closest("#initial_statistic")[0]) {
                var timestep = "raw";
                id_container = "initial_data_content";
            };

            $.ajax({
                async:true,
                type: 'POST',
                url: 'resample_data',
                data: {
                    'id': String(document.getElementById("id").value),
                    'variable': String(document.getElementById("variable").value),
                    'starttime': String(document.getElementById("starttime").value),
                    'endtime': String(document.getElementById("endtime").value),
                    'timestep': timestep,
                    'removeOutliers':removeOutliers,
                    'fillingData':fillingData,
                    'linear_regression':linear_regression,
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


        } else if ($that.closest("#histogram_statistic")[0]) {
            $("#spinner").show();
            var id = String(document.getElementById("id").value);
            var varibale = String(document.getElementById("variable").value);
            var start_time = String(document.getElementById("starttime").value);
            var end_time = String(document.getElementById("endtime").value);
            var id_container = "histogram_content";
            
            if(document.getElementById("removeOutliers").checked == true){
                var removeOutliers = "True";
            }else{
                var removeOutliers = "False";
            };
            
            if(document.getElementById("fillingData").checked == true){
                var fillingData = "True";
            }else{
                var fillingData = "False";
            };

            
            if(document.getElementById('linear_regression').checked == true){
                var linear_regression = "True";
            }else{
                var linear_regression = "False";
            };
            
            $.ajax({
                async:true,
                type: 'POST',
                url: 'histogram_statistics',
                data: {
                    'id': String(document.getElementById("id").value),
                    'variable': String(document.getElementById("variable").value),
                    'starttime': String(document.getElementById("starttime").value),
                    'endtime': String(document.getElementById("endtime").value),
                    'removeOutliers':removeOutliers,
                    'fillingData':fillingData,
                    'linear_regression':linear_regression,
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
        } else if ($that.closest("#averagemonthly_statistic")[0]) {
            $("#spinner").show();
            var id = String(document.getElementById("id").value);
            var varibale = String(document.getElementById("variable").value);
            var start_time = String(document.getElementById("starttime").value);
            var end_time = String(document.getElementById("endtime").value);
            var id_container = "avgmonthly_content";
            
            if(document.getElementById("removeOutliers").checked == true){
                var removeOutliers = "True";
            }else{
                var removeOutliers = "False";
            };
            
            if(document.getElementById("fillingData").checked == true){
                var fillingData = "True";
            }else{
                var fillingData = "False";
            };

            
            if(document.getElementById('linear_regression').checked == true){
                var linear_regression = "True";
            }else{
                var linear_regression = "False";
            };

            $.ajax({
                async:true,
                type: 'POST',
                url: 'averagemonthly_statistics',
                data: {
                    'id': String(document.getElementById("id").value),
                    'variable': String(document.getElementById("variable").value),
                    'starttime': String(document.getElementById("starttime").value),
                    'endtime': String(document.getElementById("endtime").value),
                    'removeOutliers':removeOutliers,
                    'fillingData':fillingData,
                    'linear_regression':linear_regression,
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
        }else if($that.closest("#outlierAnalysis")[0]){
            
            $("#spinner").show();
            var id = String(document.getElementById("id").value);
            var varibale = String(document.getElementById("variable").value);
            var start_time = String(document.getElementById("starttime").value);
            var end_time = String(document.getElementById("endtime").value);
            var outliersDetectionMethod = String($(document.getElementById("outliersDetectionMethod")).val());;
            var id_container = "oulierDectectionContent";
            
            $.ajax({
                async:true,
                type: 'POST',
                url: 'outlierDectection',
                data: {
                    'id': String(document.getElementById("id").value),
                    'variable': String(document.getElementById("variable").value),
                    'starttime': String(document.getElementById("starttime").value),
                    'endtime': String(document.getElementById("endtime").value),
                    'outliersDetectionMethod':outliersDetectionMethod,
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
            
        }else if($that.closest("#editOutliers")[0]){
            $("#spinner").show();
            var id = String(document.getElementById("id").value);
            var varibale = String(document.getElementById("variable").value);
            var datetime = [];
            var outlierValue = [];
            var editedValue = [];
            
            var table = ($that.parent().parent()[0]).getElementsByClassName("ouliersTable")[0];
            var rows = table.rows;
            
            for ( i = 1; i < table.rows.length; i++ ) {
                 datetime.push(rows[i].getElementsByClassName("datetime")[0].innerText);
                 outlierValue.push(rows[i].getElementsByClassName("outlierValue")[0].innerText);
                 editedValue.push(rows[i].getElementsByClassName("editedValue")[0].value);
              };
            
            $.ajax({
                async:true,
                type: 'POST',
                url: '/database/updateEditedData',
                data: {
                    'id': id,
                    'variable': varibale,
                    'datetime[]': datetime,
                    'editedValue[]':editedValue,
                },
                complete: function() {
                $("#spinner").hide();
                },  
                success: function (data) {
                    alert(data);
                    ($that.parent().parent().parent().parent()).remove();
                },
                error: function () {
                    alert('Failed in sending ajax request')
                },
                dataType: 'html',
                headers: {
                    'X-CSRFToken': csrftoken
                }
            });   
       
            $("#spinner").hide();
        }else if($that.closest(".removeAnalysis")[0]){
            ($that.parent().parent()).remove();
        }
        
        
        ;
    });


});