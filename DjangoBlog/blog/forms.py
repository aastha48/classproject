
from django.forms import forms,ModelForm
from blog.models import Comment, Post


class CommentForm(ModelForm):
     class Meta:
         model=Comment
         fields=['name','email','comment_body']


class PostForm(ModelForm):
    class Meta:
        model=Post
        fields=['title','author','body','status']
