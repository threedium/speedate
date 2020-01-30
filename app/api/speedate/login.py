#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function)

import os
import random
from time import (time)
# from api.kyc import (_kyc)
# from api.bank import (_corebank)

from bson.objectid import ObjectId
from pymongo import MongoClient
# client = MongoClient('localhost')
# db = client.speed_date


def speed_index(cli):
    data = {}
    data['data'] = False
    data['error'] = []
    data['source'] = str(os.path.abspath(__file__))
    datas = {"data": True, "error": []}

    try:
        data['index'] = cli['index']
        data['server'] = cli['server']
        data['data'] = True
    except Exception as e:
        source = "Speed-Login Index Top-Level Keys-Values (index) Self Error {}".format(e)
        data['error'].append({"error": source, "source": data['source']})
        print(source)

    if data['data'] and data['index'] == 'cleanup':
        
        _data = db.speed_members.find()
        print('Clean-up Data', _data.count())
        if _data.count():
            try:
                _data = _kyc.kyc_index({
                    "index": "webinfo",
                    "app": cli['app'],
                    "server": data['server']
                    })
                if _data['data']:
                    print('KYC Cleanup', len(_data['kyc']))
                    i = 0
                    for kyc in _data['kyc']:
                        if not db.speed_members.find({"_id": ObjectId(kyc['track'])}).count():
                            print('Cleanup User Track', kyc['track'])
                            dkyc = _kyc.kyc_index({
                                "index": "editor",
                                "editor": kyc['id'],
                                "edit": "delete",
                                "server": data['server']
                                })
                            if dkyc['data']:
                                i += 1
                                print(i, 'Deleted KYC Item', kyc['id'])
                    data['data'] = True
            except Exception as e:
                print('Cleanup Error', e)

    elif data['data'] and data['index'] == 'membership':
        # print('Validate incoming caller membership status')
        data['id'] = False
        data['kyc'] = False
        data['data'] = False
        data['enrol'] = "/api/v2/speedate/speedenrol"
        try:
            data['phone'] = cli['phone']
            data['cdr'] = cli['cdr']
            data['app'] = cli['app']
            _data = db.speed_members.find({"speed_phone": data['phone']})
            data['data'] = True
        except Exception as e:
            source = "Speed-Login Index-Membership Self Error {}".format(e)
            data['error'].append({"error": source, "source": data['source']})
            print(source)

        if data['data']:
            currency = "Shillings"
            xtry = "Kenya"
            if data['phone'][:2] == '256':
                xtry = "Uganda"
            elif data['phone'][:2] == '255':
                xtry = "Tanzania"
            elif data['phone'][:1] == '44':
                currency = "Pounds"
                xtry = "Britain"
            elif data['phone'][0] == '1':
                currency = "Dollars"
                xtry = "United States"

        if data['data'] and _data.count():
            edit = {}
            data['id'] = str(_data[0].get('_id'))
            data['kyc'] = _data[0].get('speed_kyc')
            data['calls'] = _data[0].get('speed_calls')
            if not data['calls'] or data['calls'] is None:
                print('Create Call Tally')
                data['calls'] = 1
                edit['speed_calls'] = data['calls']
            if data['cdr'] != _data[0].get('speed_cdr'):
                edit['speed_cdr'] = data['cdr']
                edit['speed_calls'] = data['calls'] + 1
            if currency != _data[0].get('speed_bill')['currency']:
                edit['speed_bill.currency'] = currency
            if xtry != _data[0].get('speed_locate')['country']:
                edit['speed_locate.country'] = currency
            if len(edit) > 0:
                db.speed_members.update_one(
                    {"speed_phone": data['phone']}, {"$set": edit}
                    )

        if data['data'] and not data['id']:
            _data = db.speed_members.insert_one({
                "speed_phone": data['phone'],
                "speed_pack": False,    # speed-on-keypad (77333)
                "speed_bank": False,    # Bank-Account
                "speed_kyc": False,  # KYC-ID
                "speed_nick": False,  # Runtime Nick-Name
                # enrol, active, token, balance, forgot, flagged
                "speed_status": "token",
                "speed_role": "client",     # client, admin
                "speed_cdr": data['cdr'],   # runtime CDR
                "speed_created": int(time()),
                "speed_bill": {
                    "login": False,
                    "logout": False,
                    "cost": 0.0,
                    "currency": False,
                    "offer": False,  # first-time offer (100 -> 20min)
                    },
                "speed_calls": 1,   # number of calls made
                "speed_premium": {},   # premium access object
                "speed_report": {},  # from speed-apps
                "speed_queue": {},  # from speed-queue
                "speed_match": {},  # from speed-match
                "speed_direct": {},  # from speed-direct
                "speed_locate": {
                    "country": False,  # country of caller
                    "media": False,  # audio of recording
                    "text": False  # transcribed location
                    },
                "speed_index": False,    # runtime index
                "speed_terms": False,    # terms and conditions
                })
            data['id'] = str(_data.inserted_id)

        if data['data'] and not data['kyc']:
            data['data'] = False
            _data = _kyc.kyc_index({
                "index": "create",
                "track": data['id'],
                "app": data['app'],
                "cdr": data['cdr'],
                "baseurl": data['enrol'],
                "server": data['server']
                })
            # print('Create Initial KYC Item', _data)
            if _data['data']:
                data['kyc'] = _data['id']
                db.speed_members.update_one(
                    {"speed_phone": data['phone']},
                    {"$set": {"speed_kyc": data['kyc']}}
                    )
                data['data'] = True

        if data['data'] and data['id'] and data['kyc']:
            _data = db.speed_members.find_one({"_id": ObjectId(data['id'])})
            kyc = _kyc.kyc_index({
                "index": "info",
                "info": data['kyc'],
                "server": data['server']
                })
            if kyc['data']:
                edit = {}
                editkyc = {}
                datas['id'] = data['id']
                datas['phone'] = _data.get('speed_phone')
                datas['cdr'] = _data.get('speed_cdr')
                datas['pack'] = _data.get('speed_pack')
                datas['kyc'] = data['kyc']
                datas['bank'] = _data.get('speed_bank')
                datas['role'] = _data.get('speed_role')
                datas['premium'] = _data.get('speed_premium')
                datas['locate'] = _data.get('speed_locate')
                if datas['locate'] is None:
                    edit['speed_locate.country'] = False
                    edit['speed_locate.media'] = False
                    edit['speed_locate.text'] = False
                    datas['locate'] = {"country": False, "media": False, "text": False}
                # datas['birthday'] = kyc['birthday']['year']
                datas['age'] = kyc['birthday']['age']
                # datas['dobformat'] = kyc['birthday']['format']
                # datas['kycname'] = kyc['names']['first']
                datas['gender'] = kyc['gender']
                datas['orient'] = kyc['orient']
                datas['academia'] = kyc['academia']
                datas['career'] = kyc['career']['type']
                datas['wages'] = kyc['career']['wages']
                datas['marital'] = kyc['marital']
                datas['religion'] = kyc['religion']
                datas['residence'] = kyc['residence']['type']
                datas['national'] = kyc['identity']['national']
                datas['passport'] = kyc['identity']['passport']
                datas['driving'] = kyc['identity']['driving']
                datas['baseurl'] = kyc['baseurl']
                if not datas['baseurl'] or datas['baseurl'] != data['enrol']:
                    editkyc['kyc_baseurl'] = data['enrol']
                if kyc['runtime']['cdr'] != data['cdr']:
                    editkyc['kyc_runtime.cdr'] = data['cdr']
                datas['cdr'] = _data.get('speed_cdr')
                datas['calls'] = _data.get('speed_calls')
                datas['bill'] = _data.get('speed_bill')
                if 'offer' not in datas['bill']:
                    # print('Create First-Time Offer')
                    datas['bill']['offer'] = False
                    edit['speed_bill.offer'] = False
                datas['nick'] = _data.get('speed_nick')
                if datas['nick'] is None:
                    datas['nick'] = False
                    edit['speed_nick'] = False
                # Runtime Status -> token, enrol, flagged, balance
                datas['status'] = _data.get('speed_status')
                # Runtime Report Obj -> Dict (Redundant?)
                datas['report'] = _data.get('speed_report')
                if datas['report'] is None:
                    datas['report'] = edit['speed_report'] = {}
                # Runtime Queue Obj -> Dict
                datas['queue'] = _data.get('speed_queue')
                if datas['queue'] is None:
                    datas['queue'] = edit['speed_queue'] = {}
                # Runtime Hotlist Obj -> Dict
                datas['match'] = _data.get('speed_match')
                if datas['match'] is None:
                    datas['match'] = edit['speed_match'] = {}
                # Direct Messaging Obj -> Dict
                datas['direct'] = _data.get('speed_direct')
                if datas['direct'] is None:
                    datas['direct'] = edit['speed_direct'] = {}
                # Runtime Index (studio,menu) Str
                datas['index'] = _data.get('speed_index')
                if datas['index'] is None:
                    datas['index'] = edit['speed_index'] = False
                # Login Terms & Conditions Queue Obj -> Dict
                datas['terms'] = _data.get('speed_terms')
                if datas['terms'] is None:
                    datas['terms'] = edit['speed_terms'] = False
                datas['created'] = _data.get('speed_created')
                if len(edit) > 0:
                    db.speed_members.update_one(
                        {"_id": _data.get('_id')}, {"$set": edit}
                        )
                if len(editkyc) > 0:
                    kyc = _kyc.kyc_index({
                        "index": "editor",
                        "editor": _data.get('speed_kyc'),
                        "edit": editkyc,
                        "server": data['server']
                        })
                data = datas

    elif data['data'] and data['index'] == 'billing':
        # print('Speed-Date Index Billing')
        try:
            edit = {}
            data['phone'] = cli['phone']
            data['cdr'] = cli['cdr']
            data['index'] = cli['bill']
            _data = db.speed_members.find({"speed_phone": data['phone']})
            if _data.count():
                if data['index'] == 'balance':
                    print('Billing Application Below 2 Min Warn')
                    edit['speed_status'] = "balance"
                elif data['index'] == 'login':
                    print('Login Billing Runtime')
                    datas['bill'] = _data[0].get('speed_bill')
                    edit['speed_bill.login'] = int(time())
                    edit['speed_bill.cost'] = 0.0
                elif 'cost' in cli:
                    print('Logout Billing Runtime', cli['cost'])
                    edit['speed_bill.logout'] = int(time())
                    edit['speed_bill.cost'] = cli['cost']

                if len(edit) > 0:
                    db.speed_members.update_one(
                        {"_id": _data[0].get('_id')}, {"$set": edit}
                        )
                data = datas
        except Exception as e:
            source = "Speed-Login Index-Billing Self Error {}".format(e)
            data['error'].append({"error": source, "source": data['source']})
            print(source)

    elif data['data'] and data['index'] == 'enrol':
        data['data'] = False
        edit = {}
        try:
            data['index'] = cli['speed']
            data['phone'] = cli['phone']
            data['app'] = cli['app']
            data['enrol'] = cli['enrol']
            _data = db.speed_members.find({"speed_phone": data['phone']})
            if _data.count():
                data['data'] = True
        except Exception as e:
            source = "Speed-Login Index-Enrol Keys-Values Self Error {}".format(e)
            data['error'].append({"error": source, "source": data['source']})
            print(source)

        if data['data'] and data['index'] == 'forgot':
            print('Forgot Password')
            edit['speed_status'] = "forgot"

        elif data['data'] and data['index'] == 'auth':
            # print('Update Bank-Account Details')
            data['data'] = False
            data['balance'] = 0
            if not _data[0].get('speed_bank'):
                # print('search bank test')
                _data = _corebank.bank_index({
                    "index": "voicebank",
                    "voicebank": "search",
                    "search": "phone",
                    "phone": data['phone'],
                    "app": data['app'],
                    "server": data['server'],
                })
                if _data['data']:
                    edit['speed_bank'] = _data['id']
                    data['data'] = True
            else:
                # print('get bank test')
                bank = _corebank.bank_index({
                    "index": "info",
                    "info": _data[0].get('speed_bank'),
                    "server": data['server']
                    })
                if bank['data']:
                    data['balance'] = bank['balance']
                    data['data'] = True

            if data['data'] and len(edit) > 0:
                print('update bank test')
                db.speed_members.update_one(
                    {"speed_phone": data['phone']}, {"$set": edit}
                    )

        elif data['data'] and data['index'] == 'activate':
            print('Active Account')
            edit['speed_status'] = "active"
            db.speed_members.update_one(
                {"speed_phone": data['phone']}, {"$set": edit}
                )

    elif data['data'] and data['index'] == 'editor':
        data['data'] = False
        try:
            if cli['editor'] == 'deleteall':
                db.speed_members.remove()
                data = datas
            else:
                print('Speed-Login Index-Editor', cli['edit'])
                _data = db.speed_members.find({"_id": ObjectId(cli['editor'])})
                if _data.count():
                    if type(cli['edit']) == dict:
                        db.speed_members.update_one(
                            {"_id": ObjectId(cli['editor'])},
                            {"$set": cli['edit']}
                            )
                        data = datas
                    elif cli['edit'] == 'delete':
                        db.speed_members.remove({"_id": ObjectId(cli['editor'])})
                        data = datas
        except Exception as e:
            source = "Speed-NickNames Index-Editor Self Error {}".format(e)
            data['error'].append({"error": source, "source": data['source']})
            print(source)

    elif data['data'] and data['index'] == 'token':
        data['data'] = False
        try:
            data['phone'] = cli['phone']
            data['token'] = cli['token']
            data['role'] = cli['role']
            _data = db.speed_members.find({"speed_phone": data['phone']})
            if _data.count():
                print('Create Token, and Update Bank', data['token'])
                edit = {}
                edit['speed_pack'] = data['token']
                edit['speed_status'] = "enrol"
                edit['speed_role'] = data['role']
                db.speed_members.update_one(
                    {"speed_phone": data['phone']}, {"$set": edit}
                    )
                data = datas
        except Exception as e:
            source = "Speed-Login Index-Token Self Error {}".format(e)
            data['error'].append({"error": source, "source": data['source']})
            print(source)

    elif data['data'] and data['index'] == 'stats':
        print('Speed-Login Stats', type(cli['speed']))
        # index=stats&speed=73285&app=dashboard
        data['clients'] = 0
        data['online'] = 0
        data['calls'] = 0
        try:
            data['clients'] = db.speed_members.find({"speed_pack": cli['speed']}).count()
            data['online'] = db.speed_members.find({"speed_pack": cli['speed'], "speed_online": "online"}).count()

            _data = db.speed_members.find({"speed_pack": cli['speed']})
            if data['clients']:
                _data = db.speed_members.find({"speed_pack": cli['speed']})
                for k in _data:
                    data['calls'] += k.get('speed_calls')
            # print('Calls Count', data['calls'])
            data['calls'] = random.randint(213, 321) # data['calls']
            datas['clients'] = random.randint(21, 32) # data['clients']
            datas['online'] = random.randint(10, 16) # data['online']
            data = datas
        except Exception as e:
            source = "Speed-Login Index-Stats Self Error {}".format(e)
            data['error'].append({"error": source, "source": data['source']})
            print(source)

    return data
