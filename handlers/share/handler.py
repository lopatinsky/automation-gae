import datetime
from urlparse import urlparse
import webapp2
from .lib_ga import ga_track_event, ga_track_page


GA_TID = "UA-53165573-6"


class GATrackBaseRequestHandler(webapp2.RequestHandler):
    def __init__(self, request=None, response=None):
        super(GATrackBaseRequestHandler, self).__init__(request, response)
        self.ga_headers = {'User-Agent': self.request.headers["User-Agent"]}
        self.cid = self.get_cid()

    def track_event(self, category, action, label=None, value=None):
        self.cid = ga_track_event(GA_TID, category, action, label=label, value=value, cid=self.cid, v=1,
                                  req_headers=self.ga_headers)

    def get_cid(self):
        cid = None
        ga = self.request.cookies.get('_ga')
        if ga:
            cid = '.'.join(ga.split('.')[-2:])
        return cid


class GATrackRequestHandler(GATrackBaseRequestHandler):
    def __init__(self, request=None, response=None):
        super(GATrackRequestHandler, self).__init__(request=request, response=response)
        self.campaign = {}

    def page_titles(self, *args, **kwargs):
        raise NotImplementedError()

    def action(self, *args, **kwargs):
        raise NotImplementedError()

    def set_campaign(self, *args, **kwargs):
        pass

    def get(self, *args, **kwargs):

        dh = self.request.host
        dp = self.request.path_qs
        titles = self.page_titles(*args, **kwargs)
        self.set_campaign(*args, **kwargs)

        for dt in titles:
            self.cid = ga_track_page(GA_TID, dh, dp, dt, self.cid, req_headers=self.ga_headers, campaign=self.campaign)
        if self.cid is not None:
            cookie = '.'.join(('GA1', str(dh.count('.')), self.cid))
            expires = datetime.datetime.utcnow() + datetime.timedelta(days=365 * 2)
            self.response.set_cookie('_ga', cookie, path='/', expires=expires)

        self.action(*args, **kwargs)


class GATrackDownloadHandler(GATrackRequestHandler):
    def set_campaign(self, platform, client_id=None):
        self.campaign["cn"] = "share_free_cup"
        self.campaign["cs"] = "ios" if platform == "i" else "android"
        referer = self.request.headers["Referer"]
        if referer:
            self.campaign["cm"] = urlparse(referer).hostname
        if client_id:
            self.campaign["cc"] = client_id

    def page_titles(self, platform, client_id=None):
        return ["download_link"]

    def action(self, platform, client_id=None):
        ua = self.request.headers['User-Agent']
        from_ = self.campaign["cs"]
        if 'Android' in ua:
            self.track_event('download', 'download_auto', 'android|from_%s|%s' % (from_, client_id))
            self.redirect("https://play.google.com/store/apps/details?id=com.empatika.doubleb")
        else:
            if "iPhone" in ua or "iPad" in ua or "iPad" in ua:
                self.track_event('download', 'download_auto', 'ios|from_%s|%s' % (from_, client_id))
            else:
                self.track_event('download', 'download_auto', 'other|from_%s|%s' % (from_, client_id))
            self.redirect("https://itunes.apple.com/ru/app/dablbi-kofe-i-caj/id908237281")
