from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import BlogPost, Entry
from .forms import PostForm, EntryForm

def index(request):
    return render(request, 'blogs/index.html')


@login_required
def posts(request):
    posts = BlogPost.objects.filter(owner=request.user).order_by('date_added')
    context = {'posts': posts}
    return render(request, 'blogs/posts.html', context)


@login_required
def post(request, post_id):
    """Show a single topic and all its entries"""
    post = BlogPost.objects.get(id=post_id)
    check_post_owner(post, request)
    entries = post.entry_set.order_by('-date_added')
    context = {'post': post, 'entries': entries}
    return render(request, 'blogs/post.html', context)


@login_required
def edit_post(request, post_id):
    """Edit an existing entry"""
    post = BlogPost.objects.get(id=post_id)
    check_post_owner(post, request)

    if request.method != 'POST':
        #Initial request; pre-fill form with the current entry
        form = PostForm(instance=post)
    else:
        #POST data submitted; process data
        form = PostForm(instance=post, data=request.POST)
        if form.is_valid():
            edited_post = form.save(commit=False)
            edited_post.owner = request.user
            edited_post.save()
            return redirect('blogs:posts')
    context = {'post': post, 'form': form}
    return render(request, 'blogs/edit_post.html', context)

@login_required
def delete_post(request, post_id):
    post = BlogPost.objects.get(id=post_id)
    check_post_owner(post, request)
    if request.method == 'POST':
        post.delete()
        return redirect('blogs:posts')
    context = {'post': post}
    return render(request, 'blogs/delete_post.html', context)


@login_required
def new_post(request):
    """Ad a new Topic"""
    if request.method != 'POST':
        #Nothing was added, create empty form
        form = PostForm()
    else:
        #POST was sent, proceed datas
        form = PostForm(data=request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.owner = request.user
            new_post.save()
            return redirect('blogs:posts')
    #Show empty or  invalid form
    context = {'form': form}
    return render(request, 'blogs/new_post.html', context)


@login_required
def new_entry(request, post_id):
    post = BlogPost.objects.get(id=post_id)
    check_post_owner(post, request)
    if request.method != 'POST':
        form = EntryForm
    else:
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.post = post
            new_entry.save()
            return redirect('blogs:post', post_id=post_id)

    context = {'post': post, 'form': form}
    return render(request, 'blogs/new_entry.html', context)


@login_required
def edit_entry(request, entry_id):
    """Edit an existing entry"""
    entry = Entry.objects.get(id=entry_id)
    post = entry.post
    check_post_owner(post, request)

    if request.method != 'POST':
        #Initial request; pre-fill form with the current entry
        form = EntryForm(instance=entry)
    else:
        #POST data submitted; process data
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('blogs:post', post_id=post.id)
    context = {'entry': entry, 'post': post, 'form': form}
    return render(request, 'blogs/edit_entry.html', context)

@login_required
def delete_entry(request, entry_id):
    entry = Entry.objects.get(id=entry_id)
    post = entry.post
    if request.method == 'POST':
        entry.delete()
        return redirect('blogs:post', post_id=post.id)
    context = {'entry': entry, 'post': post}
    return render(request, 'blogs/delete_entry.html', context)


def check_post_owner(post, request):
    if post.owner != request.user:
        raise Http404


# Create your views here.
