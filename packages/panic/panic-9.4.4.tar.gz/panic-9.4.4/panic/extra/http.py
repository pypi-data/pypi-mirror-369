import urllib, urllib.request, xml.dom

def http_request(url,params=None,parse=False):
    #print('http_request: %s' % str(values))
    #urlCGI = 'http://sms.lleida.net/xmlapi/smsgw.cgi'
    
    if not params and '?' in url:
        url,params = url.split('?',1)
        params = dict(t.split('=',1) for t in params.split('&'))
    if params:
        params = urllib.parse.urlencode(params)
        params = params.encode('utf-8') # data should be bytes

    req = urllib.request.Request(url, params)
    with urllib.request.urlopen(req) as response:
        res = response.read()        
    
    #print('received',res)
    if not parse:
        return res
    
    try:
        dom = xml.dom.minidom.parseString(res) #.encode( "utf-8" ))
    except UnicodeDecodeError:
        res = res.decode("Latin-1")
        dom = xml.dom.minidom.parseString(res) #.encode( "utf-8" ))
    
    return dom     


def build_message(self,username,message,password='',dst='',source=''):
        raise Exception('Not implemented, just an example')
        print('Building message ...')
        # Create XML document
        doc = xml.dom.minidom.Document()
        # SMS Node
        sms_element = doc.createElement("sms")
        doc.appendChild(sms_element)
        # User Node
        user_element = doc.createElement("user")
        user_element.appendChild(doc.createTextNode(username))
        sms_element.appendChild(user_element)
        # Password Node
        pass_element = doc.createElement("password")
        pass_element.appendChild(doc.createTextNode(password))
        sms_element.appendChild(pass_element)
        # Dst Node
        dst_element = doc.createElement("dst")
        for num in dst:
            num_element = doc.createElement("num")
            num_element.appendChild(doc.createTextNode(str(num)))
            dst_element.appendChild(num_element)
        sms_element.appendChild(dst_element)    
        # Txt Node
        txt_element = doc.createElement("txt")
        txt_element.appendChild(doc.createTextNode(message))
        txt_element.setAttribute("encoding","utf-8")
        
        # TODO: charset must be utf-8, but message appears cut. iso-8859-1 converts to no accentuated strings
        txt_element.setAttribute("charset","iso-8859-1")
        sms_element.appendChild(txt_element)
        # Source Node
        if(len(source) > 0):
            src_element = doc.createElement("src")
            src_element.appendChild(doc.createTextNode(source))
            sms_element.appendChild(src_element)
        
        # XML Document created, ready to be sendt
        xmlToSend = doc.toxml("iso-8859-1")
        
        values = {'xml' : xmlToSend }
        dom = ""
        msg = ""
        status = ""
        credit = ""
        
        #print('Sending message ...')
        try:
            dom = self.http_request(values)

        except Exception as error: 
            return self.errorMsg(error) 
        
        
        #print('Parsing the response ...')
        try:
            status_element = dom.getElementsByTagName("status")[0]
            status = self.getText(status_element.childNodes)
            msg_element = dom.getElementsByTagName("msg")[0]
            msg = self.getText(msg_element.childNodes)
            
            # Control the status of the response
            if(status != '100'):
                return self.errorMsg(msg)
            else :
                credit_element = dom.getElementsByTagName("newcredit")[0]
                credit = self.getText(credit_element.childNodes)
        
        except Exception as error:
            return self.errorMsg('error parsing POST response')
            
        # Prepare the return value
        res = {'result':True, 'message':msg, 'credit': credit}
        
        return res    
