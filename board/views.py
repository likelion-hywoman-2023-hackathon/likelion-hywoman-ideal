
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, UpdateView, DeleteView
from django.urls import reverse_lazy  # reverse_lazy를 import
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.views.generic import View, UpdateView, DeleteView
from django.urls import reverse_lazy  # reverse_lazy를 import
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from .models import Post, Comment
from .forms import PostForm, CommentForm

from django.contrib.auth.mixins import UserPassesTestMixin

###Post

# 게시글 등록하기
class post_register(LoginRequiredMixin, View):
    def get(self, request):
        form = PostForm()
        context = {
            "form": form,
            "title": "Board"
        }
        return render(request, "board/post_register.html", context)

    def post(self, request):
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("board:post_list")

        context = {
            'form': form
        }

        return render(request, "board/post_register.htm", context)


# 게시글 전체 보기
class post_list(View):
    def get(self, request):
        posts = Post.objects.all()
        context = {
            "posts": posts,
            "title": "Board"
        }
        return render(request, "board/post_list.html", context)


# 게시글 상세보기
class post_detail(View):
    def get(self, request, pk):
        post = Post.objects.prefetch_related('comment_set').get(pk=pk)
        comments = post.comment_set.all()
        comment_form = CommentForm()

        context = {
            "title": "Board",
            "post_id": pk,
            "post_title": post.title,
            "post_author": post.author,
            "post_contents": post.contents,
            "comments": comments,
            "comment_form": comment_form,
        }
        return render(request, 'board/post_detail.html', context)


# 게시글 수정하기
class post_update(LoginRequiredMixin, UpdateView):
    model = Post  # 수정할 게시글의 모델을 명시적으로 지정
    form_class = PostForm
    template_name = "board/post_register.html"  # post_register.html을 재활용
    context_object_name = "form"
    def get_success_url(self):
        return reverse_lazy("board:post_detail", kwargs={"pk": self.object.pk})


#게시글 삭제하기
class post_delete(LoginRequiredMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'board/post_delete.html'
    def get_object(self):
        object = get_object_or_404(Post, id=self.kwargs['pk'])
        return object
    def get_success_url(self):
        return reverse_lazy("board:post_list")



###Comment
class CommentWrite(LoginRequiredMixin, View):
    def post(self, request, pk):
        form = CommentForm(request.POST)
        post = get_object_or_404(Post, pk=pk)

        if form.is_valid():
            content = form.cleaned_data['content']
            author = request.user

            try:
                comment = Comment.objects.create(post=post, content=content, author=author)
            except ObjectDoesNotExist as e:
                print('게시물이 존재하지 않습니다.', str(e))
            except ValidationError as e:
                print('오류가 발생했습니다.', str(e))
            return redirect('board:post_detail', pk=pk)

        context = {
            'title': 'Board',
            'post_id': pk,
            'comment': post.comment_set.all(),
            'comment_form': form
        }
        return render(request, 'board/post_detail.html', context)

##댓글 수정하기
class CommentUpdate(View):
    def get(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        form = CommentForm(instance=comment)
        return render(request, 'board/comment_update.html', {'form': form, 'comment': comment})

    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('board:post_detail', pk=comment.post.pk)  # 이동할 URL 지정
        return render(request, 'board/comment_update.html', {'form': form, 'comment': comment})

class CommentDelete(View):
    def post(self, request, pk):
        if request.user.is_authenticated:
            comment = get_object_or_404(Comment, pk=pk)
            comment.delete()
            return redirect('board:post_detail', pk=comment.post.id)
        return redirect('board:post_detail', pk=pk)
