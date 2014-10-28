def set_current_user(auth, user):
    user_dict = auth.store.user_to_dict(user)
    auth.set_session(user_dict)


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
