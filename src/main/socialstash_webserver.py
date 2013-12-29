__author__ = 'Dev'

import time
import BaseHTTPServer
import snapbundle_instagram_fxns
import snapbundle_helpers

HOST_NAME = 'localhost'
PORT_NUMBER = 9000


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

    def do_GET(s):
        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        s.wfile.write("<html><head><title>Social Stash Test Web Server.</title></head>")
        s.wfile.write("<body>")
        # If someone went to "http://something.somewhere.net/foo/bar/",
        # then s.path equals "/foo/bar/".

        path_list = s.path
        path_list = path_list.split('/')
        application = path_list[1]
        if application == 'instagram':
            username = path_list[2]

            urn = snapbundle_instagram_fxns.get_urn_from_username(username)
            s.wfile.write("<b>Object urn:</b> %s" % urn)

            response = snapbundle_instagram_fxns.check_for_object(urn)
            if response:
                s.wfile.write('<table border="3">')
                s.wfile.write('<CAPTION>' + "<b>Object Info (" + str(len(response)) + ")" + '</b></CAPTION>')
                s.wfile.write('<TR><TH>Key</TH><TH>Value</TH></TR>')
                for current in sorted(response.keys()):
                    s.wfile.write("<TR><TD>" + str(current) + "</TD><TD>" + str(response[current]) + "</TD></TR>")
                s.wfile.write('</table><BR>')
            else:
                s.wfile.write('<BR>No Object Info Found <BR>')

#            response = snapbundle_instagram_fxns.get_object_metadata_dictionary(urn)
#            if response:
#                s.wfile.write('<TABLE BORDER="3">')
#                s.wfile.write('<CAPTION>' + "<b>Metadata Info (" + str(len(response)) + ")" + '</b></CAPTION>')
#                for current in sorted(response.keys()):
#                    s.wfile.write("<TR><TD>" + str(current) + "</TD><TD>" + str(response[current]) + "</TD></TR>")
#                s.wfile.write('</TABLE><BR>')
#            else:
#                s.wfile.write('<BR>No Metadata Info Found <BR>')

            response = snapbundle_instagram_fxns.get_object_metadata(urn)
            if response:
                s.wfile.write('<TABLE BORDER="3">')
                s.wfile.write('<CAPTION>' + "<b>Metadata Info (" + str(len(response)) + ")" + '</b></CAPTION>')
                s.wfile.write('<TR><TH>Key</TH><TH>Decoded Value</TH><TH>URN</TH><TH>Moniker</TH></TR>')
                for current in response:
                    s.wfile.write("<TR><TD>" + str(current['key'])
                                  + "</TD><TD>" + str(snapbundle_helpers.get_raw_value_decoded(current['rawValue'], current['dataType']))
                                  + "</TD><TD>" + str(current['urn'])
                                  + "</TD><TD>" + str(current['moniker'])
                                  + "</TD></TR>")
                s.wfile.write('</TABLE><BR>')
            else:
                s.wfile.write('<BR>No Metadata Info Found <BR>')

            response = snapbundle_instagram_fxns.get_object_relationships(urn, 'FOLLOWING')
            if response:
                s.wfile.write('<TABLE BORDER="3">')
                s.wfile.write('<CAPTION>' + "<b>Following Users (" + str(len(response)) + ")" + '</b></CAPTION>')
                s.wfile.write('<TR><TH>User</TH><TH>URN</TH></TR>')

                for current in sorted(response.keys()):
                    s.wfile.write("<TR><TD>" + str(current) + "</TD><TD>" + str(response[current]) + "</TD></TR>")
                s.wfile.write('</TABLE><BR>')
            else:
                s.wfile.write('<BR>No Following Users Info Found <BR>')

            response = snapbundle_instagram_fxns.get_object_relationships(urn, 'FOLLOWED_BY')
            if response:
                s.wfile.write('<TABLE BORDER="3">')
                s.wfile.write('<CAPTION>' + "<b>Followed By Users (" + str(len(response)) + ")" + '</b></CAPTION>')
                s.wfile.write('<TR><TH>User</TH><TH>URN</TH></TR>')
                for current in sorted(response.keys()):
                    s.wfile.write("<TR><TD>" + str(current) + "</TD><TD>" + str(response[current]) + "</TD></TR>")
                s.wfile.write('</TABLE><BR>')
            else:
                s.wfile.write('<BR>No Followed By Users Info Found <BR>')

        s.wfile.write("</body></html>")

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)