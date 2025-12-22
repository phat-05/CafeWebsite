from functools import wraps

from flask import redirect, request, jsonify, render_template
from flask_login import current_user

from app.models import UserRole, Position  #


def customer_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.path.startswith('/api'):
                return jsonify({"message": "Vui lòng đăng nhập để thực hiện chức năng này!"})
            return redirect('/login')

        if current_user.user_role != UserRole.CUSTOMER:
            if request.path.startswith('/api'):
                return jsonify({"message": "Bạn không có quyền thực hiện chức năng này!"}), 403
            return render_template("forbidden.html"), 403

        return f(*args, **kwargs)

    return decorated_func

def serving_staff_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.path.startswith('/api'):
                return jsonify({"message": "Vui lòng đăng nhập!"})
            return redirect('/login')

        is_serving_staff = (
                current_user.user_role == UserRole.STAFF and
                current_user.staff and
                current_user.staff.position == Position.STAFF
        )

        if not is_serving_staff:
            if request.path.startswith('/api'):
                return jsonify({"message": "Chức năng chỉ dành cho nhân viên phục vụ!"}), 403
            return render_template("forbidden.html"), 403

        return f(*args, **kwargs)

    return decorated_func

def cashier_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.path.startswith('/api'):
                return jsonify({"message": "Vui lòng đăng nhập!"})
            return redirect('/login')

        is_cashier = (
                current_user.user_role == UserRole.STAFF and
                current_user.staff and
                current_user.staff.position == Position.CASHIER
        )

        if not is_cashier:
            if request.path.startswith('/api'):
                return jsonify({"message": "Chức năng chỉ dành cho thu ngân!"}), 403
            return render_template("forbidden.html"), 403

        return f(*args, **kwargs)

    return decorated_func


def admin_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.path.startswith('/api'):
                return jsonify({"message": "Vui lòng đăng nhập!"})
            return redirect('/login')

        if current_user.user_role != UserRole.ADMIN:
            if request.path.startswith('/api'):
                return jsonify({"message": "Chức năng chỉ dành cho quản trị viên!"}), 403
            return render_template("forbidden.html"), 403

        return f(*args, **kwargs)

    return decorated_func


def anonymous_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect('/')
        return f(*args, **kwargs)

    return decorated_func


def login_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.path.startswith('/api'):
                return jsonify({"message": "Vui lòng đăng nhập để thực hiện chức năng này!"})
            return redirect('/login')
        return f(*args, **kwargs)

    return decorated_func