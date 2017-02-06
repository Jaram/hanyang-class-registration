Hanyang Class Registration
================================
Intro
-----
Unofficial Hanyang Registration for Python

Installation
-----------------

::

	pip install hanyang_registration
	
Quick Start
-----------
1. Login
~~~~~~~~~

::

    from hanyang_registration import sugang

    sinchung = sugang.Sinchung(verbose=True, erica=True) #default True
    sinchung.login('2014036123', 'your_password')
    

2. Set Class Codes
~~~~~~~~~~~~~~~~~~~~~~

::
    
    sinchung.sugang_codes = ['12345', '12345', '12345', ...]
    
3. Register
~~~~~~~~~~~

::

    sinchung.register()



Changelog
-----------

- v1.0.2 - Release
- v1.1 - init시에 log_level이 verbose로 변경되었습니다.

::

    sinchung = sugang.Sinchung(verbose=True) # default True

- v1.1.1 - `issue#5`__ `issue#6`__ 을 수정하였습니다.

__ https://github.com/Jaram/hanyang-class-registration/issues/5
__ https://github.com/Jaram/hanyang-class-registration/issues/6

- v1.1.2 - 새로 추가된 IN_HGT_SUUP_FLAG param 추가
- v1.1.4 - IN_HGT_SUUP_FLAG에 일반적인  수강신청을 위해서 0번값 추가.
- v1.1.5 - IN_SGSC_GB param 추가, erica flag 추가
- v1.1.6 - NETFUNNEL 대응