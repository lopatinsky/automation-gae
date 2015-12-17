import logging
from google.appengine.api.namespace_manager import namespace_manager
from handlers.web_admin.web.company import CompanyBaseHandler
from methods.auth import user_rights_required
from models import CompanyUser
from models.config.version import CURRENT_APP_ID, DEMO_APP_ID
from models.user import MAP_RIGHTS

__author__ = 'dvpermyakov'


class ListUsersHandler(CompanyBaseHandler):
    @user_rights_required
    def get(self):
        namespace = namespace_manager.get_namespace()
        namespace_manager.set_namespace('')
        users = CompanyUser.query(CompanyUser.namespace == namespace).fetch()
        for user in users:
            user.rights_str = ''
            for right in CompanyUser.ALL_RIGHTS_BITS:
                if user.has_rights((right,)):
                    user.rights_str += MAP_RIGHTS[right] + ', '

        public_hostname = "demo.rbcn.mobi" if CURRENT_APP_ID == DEMO_APP_ID else "auto.rbcn.mobi"
        login_url = "http://%s/company/login" % public_hostname
        self.render('/user/list.html', users=users, login_url=login_url)


class CreateUsersHandler(CompanyBaseHandler):
    @user_rights_required
    def get(self):
        rights = []
        for right in CompanyUser.ALL_RIGHTS_BITS:
            rights.append({
                'name': MAP_RIGHTS[right],
                'value': right
            })
        self.render('/user/edit.html', rights=rights)

    @user_rights_required
    def post(self):
        rights = []
        for right in CompanyUser.ALL_RIGHTS_BITS:
            confirmed = self.request.get(str(right))
            if confirmed:
                rights.append(right)
        login = self.request.get('login')
        values = {
            'namespace': namespace_manager.get_namespace(),
            'login': login,
            'password_raw': self.request.get('password'),
            'rights': CompanyUser.make_mask(rights),
        }
        namespace_manager.set_namespace('')
        success, user = CompanyUser.create_user(login, **values)
        self.redirect('/company/user/list')


class EditUsersHandler(CompanyBaseHandler):
    @user_rights_required
    def get(self):
        namespace_manager.set_namespace('')
        user_id = self.request.get_range('user_id')
        user = CompanyUser.get_by_id(user_id)
        rights = []
        for right in CompanyUser.ALL_RIGHTS_BITS:
            rights.append({
                'name': MAP_RIGHTS[right],
                'value': right
            })
        self.render('/user/edit.html', rights=rights, cur_user=user)

    @user_rights_required
    def post(self):
        namespace_manager.set_namespace('')
        user_id = self.request.get_range('user_id')
        user = CompanyUser.get_by_id(user_id)
        rights = []
        for right in CompanyUser.ALL_RIGHTS_BITS:
            confirmed = self.request.get(str(right))
            if confirmed:
                rights.append(right)
        user.rights = CompanyUser.make_mask(rights)
        user.put()
        self.redirect('/company/user/list')
