# factorytesting

Basic santy-checking tools for Brickstor hardware.

Intent here is to be able to run these on appliance and not need anything further.

To run __healthcheck.py__ script, we can just `curl` it and pass to python interpreter on stdin:
```
# curl -ks https://raw.githubusercontent.com/racktopsystems/factorytesting/master/healthcheck.py | python
```
