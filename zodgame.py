import requests, logging, traceback, re, time, sys, random
from bs4 import BeautifulSoup
from push import push_message

cookie = sys.argv[1]
token  = sys.argv[2]
uids   = sys.argv[3]

def chrome_cookie_string2dictionary(cookie):
    coo = {}
    for k_v in  cookie.split(':'):
        k,v = k_v.split('=', 1)
        coo[k.strip()] = v.replace('"','')
    return coo

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
}

def zodgame_task(session, tasks):
    logging.info("tasks: {}".format(tasks))
    for i in tasks:
        logging.debug("url: {}".format(i))
        session.get("https://zodgame.xyz/" + i)
        time.sleep(15 + random.randint(0,5))
        i = i.replace("do=click", "do=update")
        logging.debug("url: {}".format(i))
        session.get("https://zodgame.xyz/" + i)
    pass

def zodgame_get_user_info(session):
    page = zodgame_log_user_info(session)
    body = BeautifulSoup(page, 'html.parser')
    info = body.find("input", attrs = {"name":"formhash"})
    hash = info.get("value")
    logging.info("hash: {}".format(hash))
    tasks = re.findall(r'window.open\("(.*?)".*?"newwindow".*?\)', page, re.M|re.I)
    logging.info("tasks: {}".format(tasks))
    return hash, tasks

def zodgame_log_user_info(session):
    rsp = session.get("https://zodgame.xyz/plugin.php?id=jnbux")
    page = rsp.text.encode(rsp.encoding).decode(rsp.apparent_encoding)
    body = BeautifulSoup(page, 'html.parser')
    info = body.find_all("ul", class_ = "xl xl2 cl")
    for i in info:
        logging.info(i.get_text())
    return page

def zodgame_sign_user(session, formhash):
    url = 'https://zodgame.xyz/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1&inajax=1'
    payload = {
        'formhash': formhash,
        'qdxq': 'kx',
    }
    rsp = session.post(url, data = payload)
    page = rsp.text.encode(rsp.encoding).decode(rsp.apparent_encoding)
    logging.debug("page: {}".format(page))
    assert ("恭喜" in page) or ('已经签到' in page), "sign failed, page: {}".format(page)
    pass

def zodgame_sign():
    try:
        with requests.session() as s:
            s.headers.update(header)
            s.cookies.update(chrome_cookie_string2dictionary(cookie))
            formhash, tasks = zodgame_get_user_info(s)
            zodgame_sign_user(s, formhash)
            zodgame_task(s, tasks)
            zodgame_log_user_info(s)
    except Exception as e:
        logging.error("Exception: %s", traceback.format_exc())
        if token:
            push_message("zodgame sign failed.", str(e), token, [uids])
    pass

def main():
    logging.basicConfig(level=logging.INFO)
    time.sleep(30 + random.randint(0,30))
    zodgame_sign()
    pass

if __name__ == "__main__":
    main()