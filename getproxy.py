import json
import datetime
import requests
import re
import time
from requests.exceptions import ConnectionError, HTTPError, RequestException

class DownloadProxies:
    def __init__(self) -> None:
        self.api = {
            'socks4': [
                'https://raw.githubusercontent.com/ObcbO/getproxy/master/file/socks4.txt',
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
                'https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks4/socks4.txt',
                'https://raw.githubusercontent.com/ProxyScraper/ProxyScraper/main/socks4.txt',
                'https://raw.githubusercontent.com/TuanMinPay/live-proxy/master/socks4.txt',
                'https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks4.txt'
            ],
            'socks5': [
                'https://raw.githubusercontent.com/ObcbO/getproxy/master/file/socks5.txt',
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
                'https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt',
                'https://raw.githubusercontent.com/TuanMinPay/live-proxy/master/socks5.txt',
                'https://raw.githubusercontent.com/ProxyScraper/ProxyScraper/main/socks5.txt',
                'https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks5.txt'
            ],
            'http': [
                'https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/https/https.txt',
                'https://raw.githubusercontent.com/ObcbO/getproxy/master/file/http.txt',
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
                'https://github.com/ObcbO/getproxy/blob/master/file/https.txt',
                'https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/http.txt',
                'https://raw.githubusercontent.com/TuanMinPay/live-proxy/master/http.txt',
                'https://raw.githubusercontent.com/ProxyScraper/ProxyScraper/main/http.txt',
                'https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt',
                'https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/https.txt'
            ]
        }
        self.proxy_dict = {'socks4': [], 'socks5': [], 'http': []}

    def get_special1(self):
        proxy_list = []
        try:
            r = requests.get("https://www.socks-proxy.net/", timeout=5)
            part = str(r.text).split("<tbody>")[1].split("</tbody>")[0].split("<tr><td>")
            proxies = ""
            for proxy in part:
                proxy = proxy.split("</td><td>")
                try:
                    if proxies != '':
                        proxies += proxy[0] + ":" + proxy[1] + "\n"
                        if proxies != '':
                            proxy_list += proxies.split('\n')
                except:
                    pass
            return proxy_list
        except:
            return []

    def get_special2(self):
        try:
            summary = json.loads(requests.get('https://proxylist.geonode.com/api/proxy-summary').text)
            for i in range(summary["summary"]['proxiesOnline'] // 100):
                proxies = json.loads(requests.get(
                    'https://proxylist.geonode.com/api/proxy-list?limit=100&page={}&sort_by=lastChecked&sort_type=desc'.format(i)).text)
                for p in proxies['data']:
                    protocol = 'http' if p['protocols'][0] == 'https' else p['protocols'][0]
                    self.proxy_dict[protocol].append('{}:{}'.format(p['ip'], p['port']))
        except:
            pass

    def get(self):
        self.proxy_dict['socks4'] += self.get_special1()
        self.get_extra()

        for type in ['socks4', 'socks5', 'http']:
            for api in self.api[type]:
                self.proxy_list = []
                try_count = 0
                while try_count < 2:
                    try:
                        self.r = requests.get(api, timeout=5)
                        if self.r.status_code == requests.codes.ok:
                            self.proxy_list += re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}', self.r.text)
                            self.proxy_dict[type] += list(set(self.proxy_list))
                            print('> Get {} {} ips from {}'.format(len(self.proxy_list), type, api))
                            break  # Sortie de la boucle après une tentative réussie
                    except (ConnectionError, HTTPError) as e:
                        try_count += 1
                        print(f"Tentative {try_count} échouée pour {api}: {e}")
                        if try_count < 2:
                            time.sleep(5)
                        else:
                            print(f"Passage à l'URL suivante après {try_count} tentatives échouées pour {api}.")
                print('> Get {} proxies done'.format(type))

    def get_extra(self):
        retries = 5
        for q in range(20):
            self.count = {'http': 0, 'socks5': 0}
            self.day = datetime.date.today() + datetime.timedelta(-q)
            url = 'https://checkerproxy.net/api/archive/{}-{}-{}'.format(self.day.year, self.day.month, self.day.day)
            try_count = 0
            while try_count < retries:  # Limite les tentatives de récupération à 5
                try:
                    # Vérifier la disponibilité de l'API
                    response = requests.head(url, timeout=10)
                    if response.status_code != 200:
                        raise RequestException(f"API non disponible, statut: {response.status_code}")

                    # Faire la requête principale si l'API est disponible
                    self.r = requests.get(url, timeout=30)  # Augmenter le timeout à 30 secondes
                    self.r.raise_for_status()
                    self.json_result = json.loads(self.r.text)
                    for i in self.json_result:
                        if re.match(r'172\.\d{1,3}\.0\.1', i['ip']):
                            if i['type'] in [1, 2] and i['addr'] in self.proxy_dict['http']:
                                self.proxy_dict['http'].remove(i['addr'])
                            if i['type'] == 4 and i['addr'] in self.proxy_dict['socks5']:
                                self.proxy_dict['socks5'].remove(i['addr'])
                        else:
                            if i['type'] in [1, 2]:
                                self.count['http'] += 1
                                self.proxy_dict['http'].append(i['addr'])
                            if i['type'] == 4:
                                self.count['socks5'] += 1
                                self.proxy_dict['socks5'].append(i['addr'])
                    print('> Get {} http proxy ips from {}'.format(self.count['http'], self.r.url))
                    print('> Get {} socks5 proxy ips from {}'.format(self.count['socks5'], self.r.url))
                    break
                except (ConnectionError, HTTPError) as e:
                    try_count += 1
                    print(f"Tentative {try_count} échouée pour {url}: {e}")
                    if try_count < retries:
                        time.sleep(5)  # Attendre avant de réessayer
                    else:
                        print(f"Passage à la date suivante après {try_count} tentatives échouées pour {url}.")
                except RequestException as e:
                    print(f"Erreur lors de la vérification de l'API: {e}")
                    break

        self.proxy_dict['socks4'] = list(set(self.proxy_dict['socks4']))
        self.proxy_dict['socks5'] = list(set(self.proxy_dict['socks5']))
        self.proxy_dict['http'] = list(set(self.proxy_dict['http']))

        print('> Get extra proxies done')

    def save(self):
        for type in ['socks4', 'socks5', 'http']:
            self.proxy_dict[type] = list(set(self.proxy_dict[type]))
            self.out_file = 'proxies/{}.txt'.format(type)
            with open(self.out_file, 'w') as f:
                for i in self.proxy_dict[type]:
                    if '#' not in i and i != '\n':
                        f.write(i + '\n')
            print("> Have already saved {} proxies list as ".format(len(self.proxy_dict[type])) + self.out_file)

    def save_all(self):
        with open('proxies/all.txt', 'w') as all_file:
            for proxy_type in self.proxy_dict:
                for proxy in self.proxy_dict[proxy_type]:
                    all_file.write(proxy + '\n')
        print("> Have already saved all proxies list as proxies/all.txt")


if __name__ == '__main__':
    d = DownloadProxies()
    d.get()
    d.save()
    d.save_all()
