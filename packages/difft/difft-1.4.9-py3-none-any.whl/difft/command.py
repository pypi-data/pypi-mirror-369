import argparse
import configparser, os
from difft.client import DifftClient
from difft.message import MessageRequestBuilder
from difft.attachment import AttachmentBuilder

def send_message(args):
    appid, secret, botid, host = _parse_config(args)

    difftclient = DifftClient(appid, secret, host)

    if args.user and args.group:
        raise Exception('can not send to both user and group')

    attachment = {}
    if args.att:
        with open(args.att, "rb") as f:
            att = f.read()
        uploaded_img = difftclient.upload_attachment(botid, [args.group] if args.group else [], \
                                                        args.user.split(',') if args.user else [], att) 

        attachment = AttachmentBuilder()\
                        .authorize_id(uploaded_img.get("authorizeId"))   \
                        .key(uploaded_img.get("key"))                    \
                        .file_size(uploaded_img.get("fileSize"))         \
                        .file_name(os.path.basename(args.att))           \
                        .content_type(args.att_type)                     \
                        .digest(uploaded_img.get("cipherHash"))          \
                        .build()
    
    if args.group:
        message = MessageRequestBuilder()                     \
                .sender(botid)                                \
                .to_group(args.group)                         \
                .message(args.msg)                            \
                .at_user(args.atuser.split(','))              \
                .attachment(attachment)                       \
                .build()
    elif args.user:
        message = MessageRequestBuilder()                     \
            .sender(botid)                                    \
            .to_user(args.user.split(','))                    \
            .message(args.msg)                                \
            .attachment(attachment)                           \
            .build()
    else:
        raise Exception('please specify user or group')

    errs = difftclient.send_message(message)
    if errs:
        print(errs)

def send_card(args):
    appid, secret, botid, host = _parse_config(args)
    difftclient = DifftClient(appid, secret, host)
    if args.group:
        message = MessageRequestBuilder()                                   \
                .sender(botid)                                              \
                .to_group(args.group)                                       \
                .card(appid, args.id,args.content, False,  args.creator, args.ts, refresh=args.refresh)  \
                .build()
    elif args.user:
        message = MessageRequestBuilder()                                   \
            .sender(botid)                                                  \
            .to_user(args.user.split(','))                                  \
            .card(appid, args.id,  args.content, False, args.creator, args.ts, refresh=args.refresh)      \
            .build()
    else:
        raise Exception('please specify user or group')
    errs = difftclient.send_message(message)
    if errs:
        print(errs)


def get_account(args):
    appid, secret, botid, host = _parse_config(args)
    if not args.email and not args.wuid:
        raise Exception('both email and wuid are empty')
    if args.email and args.wuid:
        raise Exception('got both email and wuid, can only set one')

    difftclient = DifftClient(appid, secret, host)

    if args.email:
        accounts = difftclient.get_account_by_email(args.email)
    elif args.wuid:
        accounts = difftclient.get_account_by_wuid(args.wuid)
    print(accounts)

def get_group(args):
    appid, secret, botid, host = _parse_config(args)
    difftclient = DifftClient(appid, secret, host)
    if args.bot:
        groups = difftclient.get_group_by_botid(args.bot)
    else:
        groups = difftclient.get_group_by_botid(botid)

    print(groups)

def _parse_config(args):
    config = configparser.ConfigParser()
    if os.path.exists('.difft.cfg'):
        config.read_file(open('.difft.cfg'))
    elif os.path.exists(os.path.expanduser('~/.difft.cfg')):
        config.read_file(open(os.path.expanduser('~/.difft.cfg')))
    
    if args.appid:
        appid = args.appid
    elif config.has_section('base') and config.has_option('base', 'appid'):
        appid = config.get('base', 'appid')
    else:
        raise Exception('appid can not be empty')
    
    if args.secret:
        secret = args.secret
    elif config.has_section('base') and config.has_option('base', 'secret'):
        secret = config.get('base', 'secret')
    else:
        raise Exception('secret can not be empty')
    
    if args.botid:
        botid = args.botid
    elif config.has_section('base') and config.has_option('base', 'botid'):
        botid = config.get('base', 'botid')
    else:
        raise Exception('botid can not be empty')
    
    if args.host:
        host = args.host
    elif config.has_section('base') and config.has_option('base', 'host'):
        host = config.get('base', 'host')
    else:
        raise Exception('host can not be empty')

    return appid, secret, botid, host


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--appid', dest='appid', default=None, help='appid')
    parser.add_argument('--secret', '-s', dest='secret', default=None, help='secret')
    parser.add_argument('--botid', dest='botid', default=None, help='bot id')
    parser.add_argument('--host', dest='host', default=None, help='openapi server host')

    subparsers = parser.add_subparsers()

    parser_msg = subparsers.add_parser('sendmsg', help="send message")
    parser_msg.add_argument('-user', type=str, dest='user', default='')
    parser_msg.add_argument('-group', type=str, dest='group', default='')
    parser_msg.add_argument('-at', type=str, dest='atuser', default='')
    parser_msg.add_argument('-msg', type=str, dest='msg', default='')
    parser_msg.add_argument('-att', type=str, dest='att', default='', help='path to attachment, e.g: /path/to/att.txt')
    parser_msg.add_argument('-att-type', type=str, dest='att_type', default='text/html', help='attachment type, e.g: text/html, image/jpeg, image/png')
    parser_msg.set_defaults(func=send_message)

    parser_account = subparsers.add_parser('account', help="query account info")
    parser_account.add_argument('-email', type=str, dest='email', default='')
    parser_account.add_argument('-wuid', type=str, dest='wuid', default='')
    parser_account.set_defaults(func=get_account)

    parser_group = subparsers.add_parser('group', help="query group info by botid")
    parser_group.add_argument('-bot', type=str, dest='bot', default='', help='bot id, e.g: +60000')
    parser_group.set_defaults(func=get_group)

    parser_card = subparsers.add_parser('sendcard', help="send card message")
    parser_card.add_argument('-user', type=str, dest='user', default='')
    parser_card.add_argument('-group', type=str, dest='group', default='')
    parser_card.add_argument('-id', type=str, dest='id', default='', required=True)
    parser_card.add_argument('-content', type=str, dest='content', default='', required=True)
    parser_card.add_argument('-creator', type=str, dest='creator', default=None)
#    parser_card.add_argument('-fixedWidth', type=bool, dest='fixedWidth', default=False, required=False, action=argparse.BooleanOptionalAction)
    parser_card.add_argument('-ts', type=int, dest='ts', default=None)
    parser_card.add_argument('-refresh', action='store_true', dest='refresh', default=False)
    parser_card.set_defaults(func=send_card)

    try:
        args = parser.parse_args()
        args.func(args)
    except Exception as e:
        print('ERROR:', str(e))
        parser.print_help()
    
    
