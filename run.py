# -*- coding: utf-8 -*-
import os
from flask import Flask
from flask import render_template
from flask import request
import requests
from requests import ConnectionError
import pprint
import json


app = Flask(__name__)


@app.route('/')
def Welcome():
    InstanceAddress = os.getenv('CF_INSTANCE_IP', 'default')
    return render_template('index.html', address=InstanceAddress)


@app.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == 'POST':
        gatewayid = request.form['gatewayid']
        securitytoken = request.form['securitytoken']
        distinationId = request.form['distinationId']
        InstanceAddress = os.getenv('CF_INSTANCE_IP', '')

        baseurl = "https://sgmanager.ng.bluemix.net/v1/sgconfig/"
        apiurl = baseurl + gatewayid +  "/destinations/"  + distinationId + "/ipTableRule"
        # pprint.pprint(apiurl.encode('utf-8'))
        s = requests.session()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': securitytoken.encode('utf-8')
        }
        data = {
            "src": InstanceAddress.encode('utf-8'),
            "app": ""
        }

        # s.verify = False
        s.headers = headers
        response = s.put(apiurl.encode('utf-8'), data=json.dumps(data))

        # pprint.pprint(vars(s))
        # pprint.pprint(vars(response))

        if response.status_code == 200:
            apiurl = baseurl + gatewayid + "/destinations"
            s = requests.session()
            headers = {'Authorization': securitytoken.encode('utf-8')}
            s.headers = headers
            response = s.get(apiurl.encode('utf-8'))

        result = json.loads(response.content)
        # ips = result[0]["ip_table_rules"]
        ips = result[0]["ip_table_rules"]
        pprint.pprint(result[0])

        # pprint.pprint(result.ip_table_rules)
        pprint.pprint(ips)

        return render_template("index.html", type="config", address=InstanceAddress, result=ips, status_code=response.status_code)


@app.route('/test', methods=['POST'])
def test():
    InstanceAddress = os.getenv('CF_INSTANCE_IP', '')

    if request.method == 'POST':
        target = request.form['target']
        s = requests.session()
        try:
            response = s.get(target)
            pprint.pprint(response.text)
        except ConnectionError as e:
            result = e
            print('Error code: ', e)
        else:
            result = response.text
            print('request error')

        return render_template("index.html", type="check", result_check=result, address=InstanceAddress)


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port), debug=True)
