# -*- coding:utf-8 -*-
import json
import base64
import logging
import math
import random
import requests
import rsa
import re

class Sinchung(object):
    API_PROTOCOL = 'https'
    API_HOST = 'portal.hanyang.ac.kr'
    API_URL = API_PROTOCOL + '://' + API_HOST
    CHALLENGE_URL = API_URL + '/sugang/findPkiChallenges.do'
    PUBLIC_URL = API_URL + '/sugang/publicTk.do'
    SUGANG_URL = API_URL + '/sugang/sulg.do'
    LOGIN_URL = API_URL + '/sugang/lgnps.do'
    SINCHUNG_URL = API_URL + '/sugang/SgscAct/saveSugangSincheong2.do'
    NET_FUNNEL_KEY_URL = API_PROTOCOL + '://nf.hanyang.ac.kr/ts.wseq?opcode=5101&nfid=0&prefix=NetFunnel.gRtype=5101;&sid=service_1&aid=act_2&js=yes&user_data='
    NET_FUNNEL_END_URL = API_PROTOCOL + '://nf.hanyang.ac.kr/ts.wseq?opcode=5004&key={}&nfid=0&prefix=NetFunnel.gRtype=5004;&js=yes'
    CAPTCHA_RESET_URL = API_PROTOCOL + '://' + API_HOST + '/sugang/SgscAct/resetCaptchaTryCnt.do'

    def __init__(self, verbose=True, erica=True):
        """
        :param verbose: print some massage.
        :type verbose: Boolean
        """
        logging_format = '%(asctime)-15s %(message)s'
        logging.basicConfig(format=logging_format)
        self.logger = logging.getLogger('sugang_logger')
        if verbose:
            self.logger.setLevel(logging.INFO)
        else:
            self.logger.setLevel(logging.ERROR)

        self.is_login = False
        self.code = None
        self.location = 'Y0000316' if erica else 'H0002256'

    def login(self, ID, PW):
        """
        login procedure. it doesn't return True or False. but it will print any message.
        :param ID: required login. your id.
        :param PW: your pw.
        """
        self.ID = str(ID)
        self.session = requests.Session()
        req = self.session.get(self.SUGANG_URL)
        cookies = dict(WMONID=req.cookies['WMONID'], SUGANG_JSESSIONID=req.cookies['SUGANG_JSESSIONID'],
                       ipSecGb=base64.b64encode('1'), NetFunnel_ID='', loginUserId=base64.b64encode(self.ID))
        headers = {'Content-Type': 'application/json+sua; charset=utf-8'}

        req = self.session.post(self.CHALLENGE_URL, headers=headers)
        secret = json.loads(req.text)
        challenge = secret['challeng'][0]['value']
        keyNm = 'sso_00{0}'.format(random.randint(1, 3))
        publicTk_data = dict(keyNm=keyNm, encStr=self.ID)

        req = self.session.post(self.PUBLIC_URL, headers=headers, data=json.dumps(publicTk_data))
        public = json.loads(req.text)

        public_key_n = int(public['key'][0]['value'], 16)
        public_key_e = 65537
        self.PUBLIC_KEY = rsa.key.PublicKey(public_key_n, public_key_e)

        hashed_id = self.rsa_enc(self.ID, self.PUBLIC_KEY)
        hashed_pw = self.rsa_enc(PW, self.PUBLIC_KEY)

        login_data = dict(challenge=challenge, ipSecGb=1, keyNm=keyNm, loginGb=1, userId=hashed_id,
                          password=hashed_pw, signeddata='', symm_enckey='', systemGb='SUGANG',
                          returl='https://portal.hanyang.ac.kr/sugang/slgns.do?locale=ko')

        headers.pop('Content-Type')

        self.session.post(self.LOGIN_URL, headers=headers, data=login_data)
        cookies['_SSO_Global_Logout_url'] = ''

        req = self.session.get("https://portal.hanyang.ac.kr/sugang/sulg.do")

        if 'logoutLink2' in req.text:
            self.is_login = True
            self.logger.info('Login Completed')

    def rsa_enc(self, data, public_key):
        """
        encrypt by rsa. it was inspired by haegun Jeong.

        :param data: any encrypt data
        :param public_key: rsa.key.public_key
        """
        base64_encoded = base64.b64encode(data)
        length = len(base64_encoded)
        splitcnt = int(math.ceil(float(length) / 50))
        enc_final = ''

        for i in range(splitcnt):
            pos = i * 50
            end_pos = length if i == splitcnt - 1 else pos + 50
            enc_final += (rsa.encrypt(base64_encoded[pos:end_pos], public_key)).encode('hex')

        return enc_final

    def register(self):
        if not self.is_login:
            raise SinchungError('please login. use login method.')

        if not self.sugang_codes:
            raise SinchungError('please set your class no. use sugang_codes property.')

        headers = {'Content-Type': 'application/json+sua; charset=utf-8'}
        self.logger.info('---------------- start ----------------')
        # IN_JOJIK_GB_CD: "H0002256" 서울캠
        for code in self.sugang_codes:
            req = self.session.post(self.NET_FUNNEL_KEY_URL + self.ID, headers=headers)
            m = re.search('(?<=key=)(\w|\d)+', req.text)
            key = m.group(0)
            data = dict(IN_A_JAESUGANG_GB='',
                        IN_JAESUGANG_HAKSU_NO='',
                        IN_JAESUGANG_YN='N',
                        IN_JOJIK_GB_CD=self.location,
                        IN_SINCHEONG_FLAG='1',
                        IN_SUNSU_FLAG='',
                        IN_SGSC_GB='0',
                        IN_HGT_SUUP_FLAG=0,
                        IN_SUUP_NO=code,
                        IN_NETFUNNEL_KEY=key,
                        strReturnPopupYn='N')
            req = self.session.post(self.SINCHUNG_URL, data=json.dumps(data), headers=headers)
            result = json.loads(req.text)

            if result.get('outCode', None) == 'CAP':
                cap_res = self.session.post(self.CAPTCHA_RESET_URL, headers=headers)
                res = self.session.post(self.SINCHUNG_URL, data=json.dumps(data), headers=headers)
                result = json.loads(res.text)

            self.logger.info(
                u'code: {}, message: {}, current point: {}, max point {}'.format(
                    code, result.get('outMsg', ''), result.get('scHahjeom', ''), result.get('maxHakjeom', '')))

            req = self.session.post(self.NET_FUNNEL_END_URL.format(key), headers=headers)
        self.logger.info('----------------  end  ----------------')

    @property
    def sugang_codes(self):
        """
        getter sugang sinchung codes.

        :return: any sugang code list
        """
        if not self.code:
            self.sugang_codes = []
        return self.code

    @sugang_codes.setter
    def sugang_codes(self, codes):
        """
        set sugang sinchung code.
        :param codes: It will be list
        """
        self.code = codes


class SinchungError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)
