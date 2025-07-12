from flick.router import basehandler

STATIC_PATH = ""


class Index(basehandler.BaseRequestHandler):

    def get(self):
        # import pdb; pdb.set_trace()
        self.render("index.html")
