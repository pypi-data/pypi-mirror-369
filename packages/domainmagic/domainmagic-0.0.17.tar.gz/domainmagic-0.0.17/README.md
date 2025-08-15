domainmagic
===========

domainmagic is a library which combines a bunch of domain/dns lookup tools and stuff often used in related applications

Overview
________

Generic features
________________

- parallel processing (threadpool, parallel dns lookups, ...)
- automatic file updates (geoip database, iana tld list, ...)


Domain/DNS/...
______________

- validator functions (ip adresses, hostnames, email addresses)
- uri and email address extraction
- tld/2tld/3tld handling
- rbl lookups
- geoIP 


Installation
____________

Supported version of Python:
- python 3.6 and newer, python 3.9 and newer recommended

Depencendies:
- geoip2
- dnspython

```
python setup.py install
```


