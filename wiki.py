import sys
import json
import os
import subprocess
import hashlib
import cherrypy

class Wiki():

    def __init__(self):
        self.rstpath = '/home/felix/Documents/Notes/rst/'
        self.htmlpath = '/home/felix/Documents/Notes/rst/html/'
        # Load md5 check sums of the rst files
        try:
            f = open(self.rstpath + '.md5sums')
            d = f.read()
            f.close()
            self.md5sums = json.loads(d)
        except:
            self.md5sums = dict()

    @cherrypy.expose
    def index(self):
        # self.loadMd5sums()
        files = os.listdir(self.rstpath)
        page = '<html><head></head><body>'
        test = '\nTEST\n'
        for f in files:
            if ".rst" == f[-4:]:
                md5sum = self.md5(self.rstpath + f)
                if not (f in self.md5sums):
                    self.createHtml(f, md5sum)
                # Extra elif to prevent KeyError in md5sums
                elif(md5sum != self.md5sums[f]):
                    self.createHtml(f, md5sum)

                page += '<a href="/page?pagename=%s.html">%s</a><br>' %(f[:-4], f[:-4])

        test += '\n'
        print(test)

        self.saveMd5sums()

        return page + '</body></html>'

    @cherrypy.expose
    def page(self, pagename):
        # self.loadMd5sums()
        rstfile = pagename[:-5] + '.rst'
        md5sum = self.md5(self.rstpath + rstfile)
        if  md5sum != self.md5sums[rstfile]:
            self.createHtml(rstfile, md5sum, True)

        f = open(self.htmlpath + pagename)
        page = f.read()
        f.close()
        return page

    # Call of the rst2html for the given rstfile
    def createHtml(self, rstfile, md5sum, save=False):
        process = subprocess.Popen(['rst2html', '--stylesheet-path=%svoidspace.css' %(self.htmlpath),
            '%s%s' %(self.rstpath, rstfile), '%s%s.html' %(self.htmlpath, rstfile[:-4])])
        out, err = process.communicate()
        errcode = process.returncode
        print('errcode:%s' %(errcode))

        if str(errcode) == "0":
            self.md5sums[rstfile] = md5sum
            if save:
                self.saveMd5sums()

    def saveMd5sums(self):
        f = open(self.rstpath + '.md5sums', 'w')
        f.write(json.dumps(self.md5sums))
        f.close()

    def md5(self, fname):
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
   
if __name__ == '__main__':
    # CherryPy always starts with app.root when trying to map request URIs
    # to objects, so we need to mount a request handler root. A request
    # to '/' will be mapped to HelloWorld().index().
    config = {'global':
        {
            'server.socket_host': "127.0.0.1",
            'server.socket_port': 8080,
            'server.thread_pool': 10,
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static':
        {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': "./public"
        }
    }
    cherrypy.quickstart(Wiki(), '/', config=config)
