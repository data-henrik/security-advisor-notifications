# (C) 2020 IBM Corporation
#
# IBM Cloud Functions / OpenWhisk action for webhook. It receives
# a notification from IBM Cloud Security Advisor as JWT object and
# decodes its content. The decoded object is passed on.

import json,sys,os,requests
import jwt

def main(args):
    if args["sa_public_key"]:
        return {"args": args, "decoded": jwt.decode(args["data"], args["sa_public_key"])}
    else:
        return {"args": args, "decoded": jwt.decode(args["data"], verify=False)}

if __name__ == "__main__":
    main(json.loads(sys.argv[1]))