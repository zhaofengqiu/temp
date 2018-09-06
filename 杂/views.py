#-*-coding:utf-8-*-
import os

import re
import time

from flask import render_template, redirect, request, flash, current_app, url_for
from flask_login import login_required, login_user, logout_user, current_user

from .. import cache, qn,oss
from ..models import *
from . import administer
from .forms import *
from ..utils import get_sitemap, save_file, get_rss_xml, asyncio_send


def clean_cache(key):
    """
    在发布文章后删除首页，归档，分类，标签缓存，
    在更新文章后删除对应文章缓存
    在添加说说，更改友链页后删除对应缓存
    :param key: cache prefix
    """
    if key == 'all':
        cache.clear()
    elif key != 'all' and cache.get(key):
        cache.delete(key)
    else:
        pass

@administer.route('/')
@administer.route('/index')
@login_required
def index():
    return render_template('admin/admin_index.html')

@administer.route('/login/', methods=['GET', 'POST'])
def login():
    form = AdminLogin()
    if form.validate_on_submit():
        user = Admin.query.filter_by(login_name=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(url_for('administer.index'))
        flash('账号或密码无效。')
    return render_template('admin/login.html',
                           title='登录',
                           form=form)

@administer.route('/logout')
@login_required
def logout():
    logout_user()
    flash('你已经登出账号。')
    return redirect(url_for('administer.index'))

@administer.route('/setting', methods=['GET', 'POST'])
@login_required
def set_site():
    form = AdminSiteForm()
    user = Admin.query.all()[0]
    if form.validate_on_submit():
        user.name = form.username.data
        user.profile = form.profile.data
        user.site_name = form.site_name.data
        user.site_title = form.site_title.data
        user.record_info = form.record_info.data or None
        db.session.add(user)
        db.session.commit()
        flash('设置成功')
        # 清除所有缓存
        clean_cache('global')
        return redirect(url_for('administer.index'))
    form.username.data = user.name
    form.profile.data = user.profile
    form.site_name.data = user.site_name
    form.site_title.data = user.site_title
    form.record_info.data = user.record_info or None
    return render_template('admin/admin_profile.html',
                           title='设置网站信息',
                           form=form)

@administer.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            if form.password.data == form.password2.data:
                current_user.password = form.password.data
                db.session.add(current_user)
                flash('密码更改成功')
                return redirect(url_for('administer.index'))
            flash('请确认密码是否一致')
            return redirect(url_for('administer.change_password'))
        flash('请输入正确的密码')
        return redirect(url_for('administer.change_password'))
    return render_template('admin/change_password.html', form=form,
                           title='更改密码')

@administer.route('/links', methods=['GET', 'POST'])
@login_required
def add_link():
    form = SocialLinkForm()
    fr_form = FriendLinkForm()
    # 社交链接
    if form.submit.data and form.validate_on_submit():
        exist_link = SiteLink.query.filter_by(link=form.link.data).first()
        if exist_link:
            flash('链接已经存在哦...')
            return redirect(url_for('administer.add_link'))
        else:
            link = SiteLink(link=form.link.data, name=form.name.data,
                            isFriendLink=False)
            db.session.add(link)
            db.session.commit()
            flash('添加成功')
            # 清除缓存
            clean_cache('global')
            return redirect(url_for('administer.add_link'))
    # 友链
    if fr_form.submit2.data and fr_form.validate_on_submit():
        exist_link = SiteLink.query.filter_by(link=fr_form.link.data).first()
        if exist_link:
            flash('链接已经存在哦...')
            return redirect(url_for('administer.add_link'))
        else:
            link = SiteLink(link=fr_form.link.data, name=fr_form.name.data,
                            info=fr_form.info.data, isFriendLink=True)
            db.session.add(link)
            db.session.commit()
            flash('添加成功')
            # 清除缓存
            clean_cache('global')
            return redirect(url_for('administer.add_link'))
    return render_template('admin/admin_add_link.html', title="站点链接",
                           form=form, fr_form=fr_form)

@administer.route('/admin-links')
@login_required
def admin_links():
    links = SiteLink.query.order_by(SiteLink.id.desc()).all()
    social_links = [link for link in links if link.isFriendLink is False]
    friend_links = [link for link in links if link.isFriendLink is True]
    return render_template('admin/admin_link.html', title="管理链接",
                           social_links=social_links, friend_links=friend_links)

@administer.route('/delete/link/<int:id>')
@login_required
def delete_link(id):
    link = SiteLink.query.get_or_404(id)
    db.session.delete(link)
    db.session.commit()
    # 清除缓存
    clean_cache('global')
    return redirect(url_for('administer.admin_links'))

@administer.route('/great/link/<int:id>')
@login_required
def great_link(id):
    link = SiteLink.query.get_or_404(id)
    if link.isGreatLink:
        link.isGreatLink = False
    else:
        link.isGreatLink = True
    db.session.add(link)
    db.session.commit()
    # 清除缓存
    clean_cache('global')
    return redirect(url_for('administer.admin_links'))

def save_tags(tags):
    """
    保存标签到模型
    :param tags: 标签集合，创建时间，文章ID
    """
    for tag in tags:
        exist_tag = Tag.query.filter_by(tag=tag).first()
        if not exist_tag:
            tag = Tag(tag=tag)
            db.session.add(tag)
    db.session.commit()

def save_post(form, draft=False):
    """
    封装保存文章到数据库的重复操作
    :param form: write or edit form
    :param draft: article is or not draft
    :return: post object
    """
    category = Category.query.filter_by(category=form.category.data).first()
    if not category:
        category = Category(category=form.category.data)
        db.session.add(category)

    tags = [tag for tag in form.tags.data.split(',')]
    if draft is True:
        post = Post(body=form.body.data, title=form.title.data,
                    url_name=form.url_name.data, category=category,
                    tags=form.tags.data, timestamp=form.time.data, draft=True)
    else:
        post = Post(body=form.body.data, title=form.title.data,
                    url_name=form.url_name.data, category=category,
                    tags=form.tags.data, timestamp=form.time.data, draft=False)
        # 保存标签模型
        save_tags(tags)
        # 更新xml
        update_xml(post.timestamp)

    return post

# 编辑文章后更新sitemap
def update_xml(update_time):
    # 获取配置信息
    author_name = current_app.config['ADMIN_NAME']
    title = current_app.config['SITE_NAME']
    subtitle = current_app.config['SITE_TITLE']
    protocol = current_app.config['WEB_PROTOCOL']
    url = current_app.config['WEB_URL']
    web_time = current_app.config['WEB_START_TIME']
    count = current_app.config['RSS_COUNTS']

    post_list = Post.query.order_by(Post.timestamp.desc()).all()
    posts = [post for post in post_list if post.draft is False]
    # sitemap
    sitemap = get_sitemap(posts)
    save_file(sitemap, 'sitemap.xml')
    # rss
    rss_posts = posts[:count]
    rss = get_rss_xml(author_name, protocol, url, title, subtitle, web_time, update_time, rss_posts)
    save_file(rss, 'atom.xml')

@administer.route('/write', methods=['GET', 'POST'])
@login_required
def write():
    form = AdminWrite()
    if form.validate_on_submit():
        # 保存草稿
        if 'save_draft' in request.form and form.validate():
            post = save_post(form, True)
            db.session.add(post)
            flash('保存成功！')
        # 发布文章
        elif 'submit' in request.form and form.validate():
            post = save_post(form)
            db.session.add(post)
            flash('发布成功！')
            # 清除缓存
            clean_cache('global')
        db.session.commit()
        return redirect(url_for('administer.write'))
    form.time.data=time.strftime("%Y-%m-%d", time.localtime())
    return render_template('admin/admin_write.html',
                           form=form, title='写文章')

# 编辑文章或草稿
@administer.route('/edit/<int:time>/<name>', methods=['GET', 'POST'])
@login_required
def admin_edit(time, name):
    timestamp = str(time)[0:4] + '-' + str(time)[4:6] + '-' + str(time)[6:8]
    post = Post.query.filter_by(timestamp=timestamp, url_name=name).first()

    form = AdminWrite()
    if form.validate_on_submit():
        category = Category.query.filter_by(category=form.category.data).first()
        post.category = category
        post.tags = form.tags.data
        post.url_name = form.url_name.data
        post.timestamp = form.time.data
        post.title = form.title.data
        post.body = form.body.data
        # 编辑草稿
        if post.draft is True:
            if 'save_draft' in request.form and form.validate():
                db.session.add(post)
                flash('保存成功！')
            elif 'submit' in request.form and form.validate():
                post.draft = False
                db.session.add(post)
                db.session.commit()
                flash('发布成功')
                # 清除缓存
                clean_cache('global')
                # 更新 xml
                update_xml(post.timestamp)
            return redirect(url_for('administer.admin_edit', time=post.timestampInt, name=post.url_name))
        # 编辑文章
        else:
            db.session.add(post)
            db.session.commit()
            flash('更新成功')
            # 清除对应文章缓存
            key = '_'.join(map(str, ['post', post.year, post.month, post.url_name]))
            clean_cache(key)
            update_xml(post.timestamp)
            return redirect(url_for('administer.admin_edit', time=post.timestampInt, name=post.url_name))
    form.category.data = post.category.category
    form.tags.data = post.tags
    form.url_name.data = post.url_name
    form.time.data = post.timestamp
    form.title.data = post.title
    form.body.data = post.body
    return render_template('admin/admin_write.html',
                           form=form, post=post, title='编辑文章')

@administer.route('/add-page', methods=['GET', 'POST'])
@login_required
def add_page():
    form = AddPageForm()
    if form.validate_on_submit():
        page = Page(title=form.title.data,
                    url_name=form.url_name.data,
                    body=form.body.data,
                    canComment=form.can_comment.data,
                    isNav=form.is_nav.data)
        db.session.add(page)
        db.session.commit()
        flash('添加成功')
        if page.isNav is True:
            # 清除缓存
            clean_cache('global')
        return redirect(url_for('administer.add_page'))
    return render_template('admin/admin_add_page.html',
                           form=form,
                           title='添加页面')

@administer.route('/edit-page/<name>', methods=['GET', 'POST'])
@login_required
def edit_page(name):
    page = Page.query.filter_by(url_name=name).first()
    start_title = page.title
    form = AddPageForm()
    if form.validate_on_submit():
        page.title = form.title.data
        page.body = form.body.data
        page.canComment = form.can_comment.data
        page.isNav = form.is_nav.data
        page.url_name = form.url_name.data
        db.session.add(page)
        db.session.commit()
        flash('更新成功')
        # 清除缓存
        clean_cache('global')
        return redirect(url_for('administer.edit_page', name=page.url_name))
    form.title.data = start_title
    form.body.data = page.body
    form.can_comment.data = page.canComment
    form.is_nav.data = page.isNav
    form.url_name.data = page.url_name
    return render_template('admin/admin_add_page.html',
                           title="编辑页面",
                           form=form,
                           page=page)

@administer.route('/page/delete/<name>')
@login_required
def delete_page(name):
    page = Page.query.filter_by(title=name).first()
    db.session.delete(page)
    db.session.commit()
    flash('删除成功')
    if page.isNav is True:
        # 清除缓存
        clean_cache('global')
    return redirect(url_for('administer.admin_pages'))

@administer.route('/draft')
@login_required
def admin_drafts():
    posts = Post.query.order_by(Post.id.desc()).all()
    drafts = [post for post in posts if post.draft]
    return render_template('admin/admin_draft.html',
                           drafts=drafts,
                           title='管理草稿')

@administer.route('/pages')
@login_required
def admin_pages():
    pages = Page.query.order_by(Page.id.desc()).all()
    return render_template('admin/admin_page.html',
                           pages=pages,
                           title='管理页面')

@administer.route('/posts')
@login_required
def admin_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.id.desc()).paginate(
        page, per_page=current_app.config['ADMIN_POSTS_PER_PAGE'],
        error_out=False
    )
    posts = [post for post in pagination.items if post.draft is False]
    return render_template('admin/admin_post.html',
                           title='管理文章',
                           posts=posts,
                           pagination=pagination)

@administer.route('/delete/<int:time>/<name>')
@login_required
def delete(time, name):
    timestamp = str(time)[0:4] + '-' + str(time)[4:6] + '-' + str(time)[6:8]
    post = Post.query.filter_by(timestamp=timestamp, url_name=name).first()
    db.session.delete(post)
    db.session.commit()
    flash('删除成功')
    # 清除缓存
    clean_cache('global')
    return redirect(url_for('administer.admin_posts'))

@administer.route('/comments')
@login_required
def admin_comments():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['ADMIN_COMMENTS_PER_PAGE'],
        error_out=False
    )
    comments = pagination.items
    return render_template('admin/admin_comment.html', title='管理评论',
                        comments=comments, pagination=pagination)

@administer.route('/delete/comment/<int:id>')
@login_required
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    page = comment.page
    db.session.delete(comment)
    db.session.commit()
    flash('删除成功')

    if page and page.url_name == 'guestbook':
        # 清除缓存
        clean_cache('global')
    return redirect(url_for('administer.admin_comments'))

@administer.route('/allow/comment/<int:id>')
@login_required
def allow_comment(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    flash('允许通过')

    # 发送邮件
    admin_mail = current_app.config['ADMIN_MAIL']

    if comment.isReply:
        reply_to_comment = Comment.query.get_or_404(comment.replyTo)
        reply_email = reply_to_comment.email
        if reply_email != admin_mail:
            # 邮件配置
            from_addr = current_app.config['MAIL_USERNAME']
            password = current_app.config['MAIL_PASSWORD']
            to_addr = reply_email
            smtp_server = current_app.config['MAIL_SERVER']
            mail_port = current_app.config['MAIL_PORT']
            # 站点链接
            base_url = current_app.config['WEB_URL']
            # 收件人就是被回复的人
            nickname = reply_to_comment.author
            com = comment.comment

            post_url = ''
            if comment.post:
                post_url = 'http://' + '/'.join(map(str, [base_url,
                                        comment.post.year, comment.post.month, comment.post.url_name]))
            elif comment.page:
                post_url = 'http://' + base_url + '/page/' + comment.page.url_name
            elif comment.article:
                post_url = 'http://' + base_url + '/column/' + comment.article.column.url_name \
                                        + '/' + str(comment.article.id)
            # 发送邮件
            msg = render_template('user_mail.html', nickname=nickname,comment=com, url=post_url)
            asyncio_send(from_addr, password, to_addr, smtp_server, mail_port, msg)

    page = comment.page
    if page and page.url_name == 'guestbook':
        # 清除缓存
        clean_cache('global')
    return redirect(url_for('administer.admin_comments'))

@administer.route('/unable/comment/<int:id>')
@login_required
def unable_comment(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    flash('隐藏成功')

    page = comment.page
    if page and page.url_name == 'guestbook':
        # 清除缓存
        clean_cache('global')
    return redirect(url_for('administer.admin_comments'))

@administer.route('/write/shuoshuo', methods=['GET','POST'])
@login_required
def write_shuoshuo():
    form = ShuoForm()
    if form.validate_on_submit():
        shuo = Shuoshuo(shuo=form.shuoshuo.data)
        db.session.add(shuo)
        db.session.commit()
        flash('发布成功')
        # 清除缓存
        clean_cache('global')
        return redirect(url_for('administer.write_shuoshuo'))
    return render_template('admin/admin_write_shuoshuo.html',
                           title='写说说', form=form)

@administer.route('/shuos')
@login_required
def admin_shuos():
    shuos = Shuoshuo.query.order_by(Shuoshuo.timestamp.desc()).all()
    return render_template('admin/admin_shuoshuo.html',
                           title='管理说说',
                           shuos=shuos)

@administer.route('/delete/shuoshuo/<int:id>')
@login_required
def delete_shuo(id):
    shuo = Shuoshuo.query.get_or_404(id)
    db.session.delete(shuo)
    db.session.commit()
    flash('删除成功')
    # 清除缓存
    clean_cache('global')
    return redirect(url_for('administer.admin_shuos'))


# 管理主题
@administer.route('/write/column', methods=['GET','POST'])
@login_required
def write_column():
    form = ColumnForm()
    if form.validate_on_submit():
        column = Column(column=form.column.data, timestamp=form.date.data,
                        url_name=form.url_name.data, body=form.body.data,
                        password=form.password.data)
        db.session.add(column)
        db.session.commit()
        flash('专题发布成功！')
        return redirect(url_for('administer.admin_column', id=column.id))
    form.date.data=time.strftime("%Y-%m-%d", time.localtime())
    return render_template('admin_column/edit_column.html',
                           form=form, title='编辑专题')

@administer.route('/edit/column/<int:id>', methods=['GET','POST'])
@login_required
def edit_column(id):
    column = Column.query.get_or_404(id)
    form = ColumnForm()
    if form.validate_on_submit():
        column.column = form.column.data
        column.timestamp = form.date.data
        column.url_name = form.url_name.data
        column.body = form.body.data
        column.password = form.password.data
        db.session.add(column)
        db.session.commit()
        flash('专题更新成功！')
        return redirect(url_for('administer.admin_column', id=column.id))

    form.column.data = column.column
    form.date.data = column.timestamp
    form.url_name.data = column.url_name
    form.body.data = column.body
    return render_template('admin_column/edit_column.html',
                           form=form, title='更新专题', column=column)

@administer.route('/admin/columns')
@login_required
def admin_columns():
    columns = Column.query.all()
    return render_template('admin_column/admin_columns.html',
                           columns=columns, title='管理专题')

@administer.route('/admin/column/<int:id>')
@login_required
def admin_column(id):
    column = Column.query.get_or_404(id)
    articles = column.articles.order_by(Article.timestamp.desc()).all()
    return render_template('admin_column/admin_column.html', column=column,
                           articles=articles, title=column.column)

@administer.route('/delete/column/<int:id>')
@login_required
def delete_column(id):
    column = Column.query.get_or_404(id)
    articles = column.articles.order_by(Article.timestamp.desc()).all()
    db.session.delete(column)
    db.session.commit()
    flash('删除专题')
    # clean all of this column cache
    clean_cache('column_' + column.url_name)
    for i in articles:
        clean_cache('_'.join(['article', column.url_name, str(i.id)]))
    return redirect(url_for('administer.admin_columns'))

@administer.route('/<url>/write/article', methods=['GET','POST'])
@login_required
def write_column_article(url):
    column = Column.query.filter_by(url_name=url).first()
    form = ColumnArticleForm()
    if form.validate_on_submit():
        article = Article(title=form.title.data, timestamp=form.date.data,
                          body=form.body.data, secrecy=form.secrecy.data, column=column)
        db.session.add(article)
        db.session.commit()
        flash('添加文章成功！')
        # clean cache
        clean_cache('column_' + url)
        return redirect(url_for('administer.admin_column', id=column.id))
    form.date.data=time.strftime("%Y-%m-%d", time.localtime())
    return render_template('admin_column/write_article.html', form=form,
                           title='编辑文章', column=column)

@administer.route('/<url>/edit/article/<int:id>', methods=['GET','POST'])
@login_required
def edit_column_article(url, id):
    column = Column.query.filter_by(url_name=url).first()
    article = Article.query.filter_by(id=id).first()
    _title = article.title

    form = ColumnArticleForm()
    if form.validate_on_submit():
        article.title = form.title.data
        article.timestamp = form.date.data
        article.secrecy = form.secrecy.data
        article.body = form.body.data
        db.session.add(article)
        db.session.commit()
        flash('更新文章成功！')
        # clear cache
        clean_cache('_'.join(['article', url, str(id)]))
        if article.title != _title:
            # the title is change
            clean_cache('column_' + url)
        return redirect(url_for('administer.admin_column', id=column.id))

    form.title.data = article.title
    form.date.data = article.timestamp
    form.body.data = article.body
    form.secrecy.data = article.secrecy
    return render_template('admin_column/write_article.html', form=form,
                           title='更新文章', column=column, article=article)

@administer.route('/<url>/delete/article/<int:id>')
@login_required
def delete_column_article(url, id):
    column = Column.query.filter_by(url_name=url).first()
    article = Article.query.filter_by(id=id).first()
    db.session.delete(article)
    db.session.commit()
    flash('删除文章成功！')
    # 清除对于缓存
    clean_cache('_'.join(['article', url, str(id)]))
    clean_cache('column_' + url)
    return redirect(url_for('administer.admin_column', id=column.id))


# 上传文件到静态目录
@administer.route('/upload/file', methods=['GET', 'POST'])
@login_required
def upload_file():
    source_folder = current_app.config['UPLOAD_PATH']
    if request.method == 'POST':
        file = request.files['file']
        # print(file)
        # print(dir(file))
        # print(file.mimetype)
        # print(file.content_length)
        # print(file.stream.read())
        filename = file.filename
        path = os.path.join(source_folder, filename)
        file.save(path)

        return redirect(url_for('administer.index'))
    return render_template('admin/upload_file.html', title="上传文件")


# 侧栏box---begin
@administer.route('/add/sidebox', methods=['GET', 'POST'])
@login_required
def add_side_box():
    form = SideBoxForm()
    if form.validate_on_submit():
        box = SideBox(title=form.title.data, body=form.body.data,
                      is_advertising=form.is_advertising.data)
        db.session.add(box)
        db.session.commit()
        flash('添加侧栏插件成功')
        # 清除缓存
        clean_cache('global')
        return redirect(url_for('administer.admin_side_box'))
    return render_template('admin/admin_edit_sidebox.html', form=form,
                           title='添加插件')


@administer.route('/edit/sidebox/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_side_box(id):
    box = SideBox.query.get_or_404(id)
    form = SideBoxForm()
    if form.validate_on_submit():
        box.title = form.title.data
        box.body = form.body.data
        box.is_advertising = form.is_advertising.data
        db.session.add(box)
        db.session.commit()
        flash('更新侧栏插件成功')
        # 清除缓存
        clean_cache('global')
        return redirect(url_for('administer.admin_side_box'))

    form.title.data = box.title
    form.body.data = box.body
    form.is_advertising.data = box.is_advertising
    return render_template('admin/admin_edit_sidebox.html', form=form,
                           title='更新插件', box=box)


@administer.route('/sideboxs')
@login_required
def admin_side_box():
    boxes = SideBox.query.order_by(SideBox.id.desc()).all()
    return render_template('admin/admin_sidebox.html', boxes=boxes, title='管理插件')


@administer.route('/unable/box/<int:id>')
@login_required
def unable_side_box(id):
    box = SideBox.query.get_or_404(id)
    if box.unable:
        box.unable = False
    else:
        box.unable = True
    db.session.add(box)
    db.session.commit()
    # 清除缓存
    clean_cache('global')
    return redirect(url_for('administer.admin_side_box'))


@administer.route('/delete/box/<int:id>')
@login_required
def delete_side_box(id):
    box = SideBox.query.get_or_404(id)
    db.session.delete(box)
    db.session.commit()
    flash('删除插件成功')
    # 清除缓存
    clean_cache('global')
    return redirect(url_for('administer.admin_side_box'))
# 侧栏box---end

# qiniu picture bed begin
@administer.route('/qiniu/picbed', methods=['GET', 'POST'])
@login_required
def qiniu_picbed():
    # 判断是否需要七牛图床
    need_qiniu_picbed = current_app.config['NEED_PIC_BED']
    if not need_qiniu_picbed:
        flash('你没有设置七牛配置...')
        return redirect(url_for('administer.index'))
    if request.method == 'POST':

        img_name = request.form.get('key', None)
        file = request.files['file']
        filename = file.filename
        img_stream = file.stream.read()
        if img_name:
            filename = re.sub(r'[\/\\\:\*\?"<>|]', r'_', img_name)
        if file.mimetype.startswith('image') and qn.upload_qn(filename, img_stream):
            flash('upload image {0} successful'.format(filename))
            return redirect(url_for('administer.qiniu_picbed'))

        flash('upload image fail')
        return redirect(url_for('administer.qiniu_picbed'))
    # get all images
    images = qn.get_all_images()
    counts = len(images)

    return render_template('plugin/picbed.html',
                           title="七牛图床", images=images, counts=counts)

@administer.route('/qiniu/delete', methods=['GET', 'POST'])
@login_required
def delete_img():
    key = request.get_json()['key']
    if qn.del_file(key):
        flash('delete image {0} successful'.format(key))
        return redirect(url_for('administer.qiniu_picbed'))
    flash('delete image fail')
    return redirect(url_for('administer.qiniu_picbed'))

@administer.route('/qiniu/rename', methods=['GET', 'POST'])
@login_required
def rename_img():
    key = request.get_json()['key']
    key_to = request.get_json()['keyTo']
    if qn.rename_file(key, key_to):
        flash('rename image {0} successful'.format(key))
        return redirect(url_for('administer.qiniu_picbed'))
    flash('rename image fail')
    return redirect(url_for('administer.qiniu_picbed'))

# alyun oss
@administer.route('/aliyunoss/picbed', methods=["GET","POST"])
@login_required
def aliyunoss_pic():

        need_qiniu_picbed = current_app.config['NEED_PIC_BED_OSS']
        if not need_qiniu_picbed:
            flash('你没有设置阿里云配置...')
            return redirect(url_for('administer.index'))
        if request.method=="GET":
            img_datas=OssImg.query.order_by(OssImg.date.desc()).limit(20).all()
        else:
            searchkeys=request.form.get('searchkey').split()
            sum=request.form.get('sum')
            try :
                sum = int(sum)
            except:
                flash('查找几个要输入数字')
                return redirect(url_for('administer.aliyunoss_pic'))

            if  len(searchkeys)==0 :
                return redirect(url_for('administer.aliyunoss_pic'))
            img_datass=[]
            for searchkey in searchkeys:
                img_datas = OssImg.query.filter(OssImg.filename.ilike('%'+searchkey+'%')).limit(sum).all()
                for img_data in img_datas:
                    img_datass.append(img_data)
            img_datas=list(set(img_datass))
            img_datas=sorted(img_datas,key=lambda data : data.date, reverse=True)

        return render_template('plugin/aliyunosspicbd.html', img_datas=img_datas)

@administer.route('/aliyunoss/detail/<string:key>')
def ossimgdetail(key):
    img_data=OssImg.query.filter_by(key=key).first()
    return render_template('plugin/osspicdetail.html',img_data=img_data)
@administer.route('/aliyunoss/img/delete/',methods=['POST'])
@login_required
def delete_oss_pic():
    key=request.form.get('key')
    option=request.form.get('option')

    if option=="True":
        print(option)
        oss.img_delete(key)
        img_data = OssImg.query.filter_by(key=key).first()
        db.session.delete(img_data)
        db.session.commit()
        return redirect(url_for('administer.aliyunoss_pic'))
    else:
        return redirect(url_for('administer.ossimgdetail',key=key))
    

