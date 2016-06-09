from django.conf.urls import patterns, include, url
from . import views
from . import models

urlpatterns = [
               url(r'^basemap$',views.gisbase),
               url(r'^province$',views.province),
               url(r'^stations$',views.stations),
               url(r'^csv$',views.some_view),
               url(r'^data_review$',views.data_review),
               url(r'^data_download$',views.data_download),
               url(r'^update_geojson$',views.update_geojson),
               url(r'^show_graph$',views.show_graph),
               url(r'^uploadmap$',views.upload_map),
               url(r'^confirm_upload_map$',views.confirm_upload_map),
               url(r'^statistic_data$',views.statistic_data),
               url(r'^resample_data$',views.resample_data),
               url(r'^histogram_statistics$',views.histogram_statistics),
               url(r'^averagemonthly_statistics$',views.averagemonthly_statistics),
               url(r'^extract_data$',views.extract_data),
               url(r'^export2swat$',views.export2swat),
               url(r'^upload_model_file$',views.upload_model_file),
               url(r'^confirm_model_file$',views.confirm_model_file),
               url(r'^validation_analysis$',views.validation_analysis),
               url(r'^multivariable_statistic$',views.multivariable_statistic),
               url(r'^blank$',views.blank),
               url(r'^general_multivariable_statistic$',views.general_multivariable_statistic),
               url(r'^validation_residual_analysis$',views.validation_residual_analysis),
               url(r'^generate_swat_wgn$',views.generate_swat_wgn),
               url(r'^multiLinearRegression$',views.multiLinearRegression),
               url(r'^outlierDectection$',views.outlierDectection),
               url(r'^multipleBoxPlot$',views.multipleBoxPlot)
            ]
