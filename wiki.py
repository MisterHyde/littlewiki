import sys
import json
import os
import subprocess
import hashlib
import cherrypy
from cherrypy.lib.static import serve_file

class Wiki():

    def __init__(self):
        # The path where the .rst files lies
        self.rstpath = '/home/felix/Documents/Notes/'
        # The path where the html files should be stored
        self.htmlpath = '/home/felix/Documents/Notes/html/'
        # A dictionary with the relative paths to all rst files
        self.rstfiles = dict()
        # A dict for storing paths to the img folders of the rst files
        self.imgpaths = dict()
        self.currdir = "%s/" %(os.path.dirname(os.path.abspath(__file__)))

        # Load md5 check sums of the rst files
        try:
            f = open(self.rstpath + '.md5sums')
            d = f.read()
            f.close()
            self.md5sums = json.loads(d)
        except:
            self.md5sums = dict()
            
        self.cssfile = ''
        if "main.css" in os.listdir(self.htmlpath):
            self.cssfile = '%smain.css' %(self.htmlpath)

        self.searchRst()

    # Creates a html site with links to all .html files
    @cherrypy.expose
    def index(self):
        self.searchRst()
        page = '<html><head></head><body>'
        for filename,path in self.rstfiles.items():
            page += '<a href="/page?pagename=%s.html">%s</a><br>' %(filename[:-4], filename[:-4])
        return page + '</body></html>'

    # Returns the html page specified with the GET parameter 'pagename'
    @cherrypy.expose
    def page(self, pagename):
        rstfile = pagename[:-5] + '.rst'
        md5sum = self.md5(self.rstfiles[rstfile])
        if  md5sum != self.md5sums[rstfile]:
            self.createHtml(rstfile, md5sum, True)

        f = open(self.htmlpath + pagename)
        page = f.read()
        f.close()
        print(os.path.dirname(os.path.abspath(__file__)))
        return serve_file(self.htmlpath + pagename)

    def searchRst(self):
        for dirname, dirnames, filenames in os.walk(self.rstpath):
            if '.git' in dirnames:
                dirnames.remove('.git')
            for filename in filenames:
                if filename[-4:] == '.rst':
                    self.rstfiles[filename] = os.path.join(dirname, filename)
                    md5sum = self.md5(self.rstfiles[filename])
                    if not (filename in self.md5sums):
                        self.createHtml(filename, md5sum)
                    # Extra elif to prevent KeyError in md5sums
                    elif(md5sum != self.md5sums[filename]):
                        self.createHtml(filename, md5sum)
                    # If exists img dir then create a symlink in the html path
                    if os.path.isdir("%s/img" %(dirname)):
                        print("%s/img" %(dirname) + " => %s%s" %(self.htmlpath, filename[:-4]))
                        try:
                            os.symlink("%s/img" %(dirname), "%spublic/%s" %(
                                self.currdir ,filename[:-4]))
                        except:
                            print('')

        self.saveMd5sums()


    # Call of the rst2html for the given rstfile
    def createHtml(self, rstfile, md5sum, save=False):
        rstcmd = list()
        rstcmd.append('rst2html')
        if self.cssfile != '':
            rstcmd.append('--stylesheet-path=%s' %(self.cssfile))
        rstcmd.append('--tab-width=4')
        rstcmd.append('%s' %(self.rstfiles[rstfile]))
        rstcmd.append('%s%s.html' %(self.htmlpath, rstfile[:-4]))
        test = '\n'
        for t in rstcmd:
            test += t + ' '
        test += '\n'
        print(test)
        process = subprocess.Popen(rstcmd)
        out, err = process.communicate()
        errcode = process.returncode
        print('errcode:%s' %(errcode))

        if str(errcode) == "0":
            self.md5sums[rstfile] = md5sum
            if save:
                self.saveMd5sums()

    # Saves self.md5sums as json string to self.rstpath+.md5sums
    def saveMd5sums(self):
        f = open(self.rstpath + '.md5sums', 'w')
        f.write(json.dumps(self.md5sums))
        f.close()

    # Creates a md5 sum for the given file copied from the stackoverflypost
    # "https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file#3431835" 
    # from the user quantum soup
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
            'server.socket_port': 18080,
            'server.thread_pool': 10,
        },
        '/static':
        {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': "%s/public" % (os.path.dirname(os.path.abspath(__file__)))
        }

    }
    cherrypy.quickstart(Wiki(), '/', config=config)
