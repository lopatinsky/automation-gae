from webapp2_extras import security


def set_current_user(auth, user):
    user_dict = auth.store.user_to_dict(user)
    auth.set_session(user_dict)


def set_password(user, password):
    user.password = security.generate_password_hash(password, length=12)


def user_required(handler):
    def check_user(self, *args, **kwargs):
        if self.user is None:
            self.redirect("/admin/login")
        else:
            return handler(self, *args, **kwargs)
    return check_user


def api_user_required(handler):
    def check_user(self, *args, **kwargs):
        if self.user is None:
            self.abort(401)
        else:
            return handler(self, *args, **kwargs)
    return check_user
