import markdown
from django.shortcuts import render,get_object_or_404
from .models import Post,Category,Tag
from comments.forms import CommentForm
from django.views.generic import ListView,DetailView

def index(request):
    post_list = Post.objects.all().order_by('-create_time')
    return render(request,'blog/index.html',context={'post_list':post_list})

#代替index视图函数
class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        #在视图函数中将模板变量传递给模板是通过给render函数的context参数传递一个字典实现的，
        #在类视图中，这个需要传递的模板变量字典是通过get_context_data获得的
        #所以我们复写该方法，以便我们能够自己再插入一些我们自定义的模板变量进去

        #首先获得父类生成的传递给模板的字典
        context = super().get_context_data(**kwargs)
        #父类生成的字典中已有paginator、page_obj、is_paginated这三个模板变量
        #paginator是Paginator的一个实例
        #page_obj是Page的一个实例
        #is_paginated是一个布尔变量，用于指示是否已分页
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')

        #调用自己写的pagination_data方法获得显示分页导航条需要的数据
        pagination_data = self.pagination_data(paginator,page,is_paginated)

        #将分页导航条的模板变量更新到context中，注意pagination_data方法返回的也是一个字典
        context.update(pagination_data)
        return context

    def pagination_data(self,paginator,page,is_paginated):
        if not is_paginated:
            return {}

        #当前页左边连续的页码号，初始值为空
        left = []
        # 当前页右边连续的页码号，初始值为空
        right = []
        #标识第一页页码后是否需要显示省略号
        left_has_more = False

        # 标识最后一页页码前是否需要显示省略号
        right_has_more = False

        #标示是否需要显示第一页的页码号
        first = False
        # 标示是否需要显示最后一页页的页码号
        last = False

        #获得用户当前请求的页码号
        page_number = page.number
        #获得分页后的总页数
        total_pages = paginator.num_pages
        #获得整个分页页码列表，比如分了四页，就是[1,2,3,4]
        page_range = paginator.page_range

        if page_number == 1:
            #注意这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码
            right = page_range[page_number:page_number+2]
            if right[-1]<total_pages-1:
                right_has_more = True
            if right[-1]<total_pages:
                last = True
        elif page_number == total_pages:
            left = page_range[(total_pages-3) if (total_pages-3)>0 else 0:total_pages-1]
            if left[0]>2:
                left_has_more = True
            if left[0]>1:
                first = True
        else:
            left = page_range[(page_number-3) if (page_number-3)>0 else 0:page_number-1]
            if left[0]>2:
                left_has_more = True
            if left[0]>1:
                first = True

            right = page_range[page_number,page_number+2]
            if right[-1]<total_pages-1:
                right_has_more = True
            if right[-1]<total_pages:
                last = True

        data = {
            'left':left,
            'right':right,
            'left_has_more':left_has_more,
            'right_has_more':right_has_more,
            'first':first,
            'last':last,
        }
        return data


def detail(request,pk):
    post = get_object_or_404(Post,pk=pk)
    post.increase_views()
    post.body = markdown.markdown(post.body,
                                  extensions=[
                                      'markdown.extensions.extra',
                                      'markdown.extensions.codehilite',
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           ])
    form = CommentForm()
    comment_list = post.comment_set.all()
    context = {
        'post':post,
        'comment_list':comment_list,
        'form':form
    }
    return render(request,'blog/detail.html',context)


#代替detail函数
class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get(self,request,*args,**kwargs):
        #复写get方法的目的是因为每当文章被访问一次，就得将文章阅读量+1
        #get方法放回的是一个HttpResponse实例
        #之所以需要先调用父类的get方法，是因为只有当get方法被调用后，
        #才有self.object属性，其值为Post实例，即被访问的文章post
        response = super(PostDetailView,self).get(request,*args,**kwargs)
        self.object.increase_views()
        return response
    def get_object(self, queryset=None):
        #复写get_object方法的目的是因为需要对post的body值进行渲染
        post = super(PostDetailView,self).get_object(queryset=None)
        post.body = markdown.markdown(post.body,
                                      extensions=[
                                          'markdown.extensions.extra',
                                          'markdown.extensions.codehilite',
                                          'markdown.extensions.toc',
                                      ])
        return  post

    def get_context_data(self, **kwargs):
        #复写get_context_date的目的是因为除了将post传递给模板外（DetailView已经帮我们完成），
        #还要把评论表单、post下的评论列表传递给模板
        context = super(PostDetailView,self).get_context_data(**kwargs)
        form = CommentForm()
        comment_list = self.object.comment_set.all()
        context.update({
            'form':form,
            'comment_list':comment_list
        })
        return context


def archives(request,year,month):
    post_list = Post.objects.filter(create_time__year=year,create_time__month=month).order_by('-create_time')
    return render(request,'blog/index.html',context={'post_list':post_list})

#代替上面的archives函数
class ArchivesView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return super(ArchivesView,self).get_queryset().filter(create_time__year=year,create_time__month=month)

def category(request,pk):
    cate = get_object_or_404(Category,pk=pk)
    post_list = Post.objects.filter(category=cate).order_by('-create_time')
    return render(request,'blog/index.html',context={'post_list':post_list})

#代替上面的category视图函数
class CategoryView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        cate = get_object_or_404(Category,pk=self.kwargs.get('pk'))
        return super(CategoryView,self).get_queryset().filter(category=cate)

class TagView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        tag = get_object_or_404(Tag,pk=self.kwargs.get('pk'))
        return super(TagView,self).get_queryset().filter(tags = tag)