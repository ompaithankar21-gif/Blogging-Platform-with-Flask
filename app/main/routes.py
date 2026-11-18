import re
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Post, Category, Tag, Comment, User
from ..forms import PostForm, CommentForm

main_bp = Blueprint("main", __name__)


def make_slug(title, post_id=None):
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    original = slug
    number = 2
    while Post.query.filter(Post.slug == slug, Post.id != post_id).first():
        slug = f"{original}-{number}"
        number += 1
    return slug


def seed_categories():
    if Category.query.count() == 0:
        for name in ["Technology", "Lifestyle", "Travel", "Design", "Culture"]:
            db.session.add(Category(name=name))
        db.session.commit()


@main_bp.route("/")
def index():
    seed_categories()
    page = request.args.get("page", 1, type=int)
    category = request.args.get("category")
    tag = request.args.get("tag")
    search = request.args.get("q", "").strip()
    query = Post.query.filter_by(is_published=True)
    if category:
        query = query.join(Category).filter(Category.name == category)
    if tag:
        query = query.join(Post.tags).filter(Tag.name == tag)
    if search:
        query = query.filter(db.or_(Post.title.ilike(f"%{search}%"), Post.summary.ilike(f"%{search}%")))
    posts = query.order_by(Post.created_at.desc()).paginate(page=page, per_page=6, error_out=False)
    categories = Category.query.order_by(Category.name).all()
    popular_tags = Tag.query.limit(12).all()
    return render_template("main/index.html", posts=posts, categories=categories,
                           popular_tags=popular_tags, active_category=category,
                           search=search)


@main_bp.route("/post/<slug>", methods=["GET", "POST"])
def post_detail(slug):
    post = Post.query.filter_by(slug=slug, is_published=True).first_or_404()
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Please log in to join the conversation.", "warning")
            return redirect(url_for("auth.login", next=request.url))
        db.session.add(Comment(body=form.body.data.strip(), post=post, author=current_user))
        db.session.commit()
        flash("Your comment was posted.", "success")
        return redirect(url_for("main.post_detail", slug=slug))
    return render_template("main/post_detail.html", post=post, form=form)


@main_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_post():
    seed_categories()
    form = PostForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name)]
    if form.validate_on_submit():
        post = Post(title=form.title.data.strip(), summary=form.summary.data.strip(),
                    content=form.content.data, is_published=form.is_published.data,
                    author=current_user, category_id=form.category.data,
                    slug="")
        post.slug = make_slug(post.title)
        post.tags = parse_tags(form.tags.data)
        db.session.add(post)
        db.session.commit()
        flash("Post saved successfully.", "success")
        return redirect(url_for("main.post_detail", slug=post.slug))
    return render_template("main/editor.html", form=form, post=None)


def parse_tags(raw):
    tags = []
    for name in {part.strip().lower() for part in (raw or "").split(",") if part.strip()}:
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            tag = Tag(name=name)
            db.session.add(tag)
            db.session.flush()
        tags.append(tag)
    return tags


@main_bp.route("/post/<slug>/edit", methods=["GET", "POST"])
@login_required
def edit_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if post.author_id != current_user.id:
        abort(403)
    form = PostForm(obj=post)
    form.category.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name)]
    form.tags.data = ", ".join(tag.name for tag in post.tags)
    if form.validate_on_submit():
        post.title = form.title.data.strip()
        post.slug = make_slug(post.title, post.id)
        post.summary = form.summary.data.strip()
        post.content = form.content.data
        post.category_id = form.category.data
        post.is_published = form.is_published.data
        post.tags = parse_tags(form.tags.data)
        db.session.commit()
        flash("Your changes were saved.", "success")
        return redirect(url_for("main.post_detail", slug=post.slug))
    return render_template("main/editor.html", form=form, post=post)


@main_bp.route("/post/<slug>/delete", methods=["POST"])
@login_required
def delete_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if post.author_id != current_user.id:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted.", "info")
    return redirect(url_for("main.dashboard"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    posts = Post.query.filter_by(author_id=current_user.id).order_by(Post.updated_at.desc()).all()
    return render_template("main/dashboard.html", posts=posts)
