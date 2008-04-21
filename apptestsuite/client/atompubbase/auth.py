from urllib import urlencode
import atompubbase

class ClientLogin:
  """
  Perform ClientLogin up front, save the auth token, and then
  register for all the PRE events so that we can add the auth token
  to all requests.
  """

  def __init__(self, http, name, password, service):
    auth = dict(accountType="HOSTED_OR_GOOGLE", Email=name, Passwd=password, service=service,
                source='AtomPubBase-1.0')
    resp, content = http.request("https://www.google.com/accounts/ClientLogin", method="POST", body=urlencode(auth), headers={'Content-Type': 'application/x-www-form-urlencoded'})
    lines = content.split('\n')
    d = dict([tuple(line.split("=", 1)) for line in lines if line])
    if resp.status == 403:
        self.Auth = ""
    else:
        self.Auth = d['Auth']
    atompubbase.events.register_callback("PRE", self.pre_cb)

  def pre_cb(self, headers, body, filters):
    headers['authorization'] = 'GoogleLogin Auth=' + self.Auth 

