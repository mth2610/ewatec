from django import forms
from models import Article

class ArticleForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = ("title","body","person","picture")
#        fields = ("title","body","pub_date","person","picture")
        # fields = ("title","body","pub_date")

