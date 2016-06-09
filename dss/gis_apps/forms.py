from django import forms
from models import Upload

class UploadForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ("upload_file","user",)
        
        # fields = ("title","body","pub_date")
