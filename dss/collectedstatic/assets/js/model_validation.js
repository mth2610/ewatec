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
        // -----------------------------------------Monthly Graph-----------------------------------------
        if ($that.closest("#initial_analysis")[0] || $that.closest("#residual_analysis")[0]){      
            $("#spinner").show();
            var id = String(document.getElementById("id").value);
            var varibale = String(document.getElementById("variable").value);
            var start_time = String(document.getElementById("starttime").value);
            var end_time = String(document.getElementById("endtime").value);
            var observation_plot = String($(document.getElementById("observation-plot")).val());
            var simulation_plot = String($(document.getElementById("simulation-plot")).val());
            var timestep =  String($(document.getElementById("timestep")).val());
            var file_path = String(document.getElementById("file-path").value);
            
            console.log(file_path);
            
            
            if(document.getElementById('removeoutlier').checked == true){
                var removeoutlier = "True";
            }else{
                var removeoutlier = "False";
            }
            
            
            if ($that.closest("#initial_analysis")[0]){
                var url = 'validation_analysis';
                var id_container = "initial_content";
            }else if($that.closest("#residual_analysis")[0]){
                var url = 'validation_residual_analysis';
                var id_container = "residual_content";
            }
            
            $.ajax({
                async:true,
                type: 'POST',
                url: url,
                data: {
                    'id': String(document.getElementById("id").value),
                    'variable': String(document.getElementById("variable").value),
                    'starttime': String(document.getElementById("starttime").value),
                    'endtime': String(document.getElementById("endtime").value),
                    'observation_plot': observation_plot,
                    'simulation_plot': simulation_plot,
                    'timestep': timestep,
                    'removeoutlier':removeoutlier,
                    'file_path': file_path
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
        }
    });


});