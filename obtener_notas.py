from bs4 import BeautifulSoup
import requests
import time
import json
import threading
 

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "text/html",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com/"
}

class Peliculas:
    """
    Clase que obtiene las notas de las películas/series en diferentes plataformas, diferenciando entre críticas y valoraciones de usuarios.
    Obtiene las notas de IMDB, FilmAffinity, Metacritic y Rotten Tomatoes.
    Se puede asignar el título y el tipo de la película/serie (m para película, tv para serie) en el constructor.
    """
    def __init__(self, titulo):
        self.titulo = titulo
        self.val_criticas = {}
        self.val_audiencia = {}

    def get_nota_imdb(self):
        try:
            url = f'https://v3.sg.media-imdb.com/suggestion/titles/x/{self.titulo}.json'
            r= requests.get(url, headers=headers)
            # print(r.status_code)
            
            for i in r.json()['d']:
                enlace = i['id']
                time.sleep(1)
                soup = BeautifulSoup(requests.get('https://www.imdb.com/title/' + enlace, headers=headers).text, 'html.parser')
                val = soup.find('span', class_='sc-d541859f-1 imUuxf')
                if val:
                    rating = float(val.text)
                    self.val_audiencia['Imdb'] = rating
                    # print(rating)
                    return rating
        except Exception as e:
            self.val_audiencia['Imdb'] = 'No se ha podido obtener'
            # print(e)
            # print('Error al obtener la nota de IMDB')
            return None
    def get_nota_filmaffinity(self):
        try:
            url = f'https://www.filmaffinity.com/en/search.php?stext={self.titulo}'
            r= requests.get(url, headers=headers)
            #print(r.status_code)
            soup = BeautifulSoup(r.text, 'html.parser')
            rating = float(soup.find('div', class_='avg mx-0').text.replace(',', '.'))
            self.val_audiencia['Filmaffinity'] = rating
            #print(rating)
            return rating
        except:
            try:
                rating = float(soup.find('div', id='movie-rat-avg').text.strip().replace(',', '.'))
                self.val_audiencia['Filmaffinity'] = rating
                # print(rating)
                return rating
            except Exception as e:
                self.val_audiencia['Filmaffinity'] = 'No se ha podido obtener'
                # print(e)
                # print('Error al obtener la nota de FilmAffinity')
                return None
    def get_nota_metacritic(self):
        try:
            ratings = {}
            r = requests.get(f'https://backend.metacritic.com/finder/metacritic/autosuggest/{self.titulo}')
            #print(r.status_code)
            r = r.json()
            for i in r['data']['items']:
                if i['type'] == 'movie' or i['type'] == 'show':
                    tipo = i['type']
                    slug = i['slug']
                    break
            time.sleep(1)
            if tipo == 'movie':
                soup = BeautifulSoup(requests.get(f'https://www.metacritic.com/movie/{slug}', headers=headers).text, 'html.parser')
            else:
                soup = BeautifulSoup(requests.get(f'https://www.metacritic.com/tv/{slug}', headers=headers).text, 'html.parser')
            ratings['critics'] = (int(soup.find('div', class_='c-siteReviewScore u-flexbox-column u-flexbox-alignCenter u-flexbox-justifyCenter g-text-bold c-siteReviewScore_green g-color-gray90 c-siteReviewScore_medium').text)/10)
            ratings['user'] = float(soup.find('div', class_='c-siteReviewScore u-flexbox-column u-flexbox-alignCenter u-flexbox-justifyCenter g-text-bold c-siteReviewScore_green c-siteReviewScore_user g-color-gray90 c-siteReviewScore_medium').text)
            self.val_criticas['Metacritic_critic'] = ratings['critics']
            self.val_audiencia['Metacritic'] = ratings['user']
            #print(ratings['critics'], ratings['user'])
            return ratings
        except Exception as e:
            self.val_audiencia['Metacritic_critic'] = 'No se ha podido obtener'
            self.val_audiencia['Metacritic'] = 'No se ha podido obtener'
            #print(e)
            #print('Error al obtener la nota de Metacritic')
            return None
    def get_nota_rottentomatoes(self):
        try:
            url = "https://79frdp12pn-3.algolianet.com/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.24.0)%3B%20Browser%20(lite)&x-algolia-api-key=175588f6e5f8319b27702e4cc4013561&x-algolia-application-id=79FRDP12PN"
            payload = json.dumps({
            "requests": [
                {
                "indexName": "content_rt",
                "params": "analyticsTags=%5B%22header_search%22%5D&clickAnalytics=true&filters=isEmsSearchable%20%3D%201&hitsPerPage=5",
                "query": f'{self.titulo}'
                }
            ]
            })
            r = requests.post(url, headers=headers, data=payload)
            #print(r.status_code)
            r = r.json()
            print(len(r['results'][0]['hits']))
            for i in r['results'][0]['hits']:
                try:
                    self.val_criticas['Rottentomatoes_critic'] = i['rottenTomatoes']['criticsScore']/10
                    self.val_audiencia['Rottentomatoes'] = i['rottenTomatoes']['audienceScore']/10
                    break
                except:
                    pass              
            #print(self.val_criticas['rottentomatoes_critic'], self.val_audiencia['rottentomatoes'])
            return self.val_criticas['Rottentomatoes_critic'], self.val_audiencia['Rottentomatoes']
        except Exception as e:
            self.val_audiencia['Rottentomatoes_critic'] = 'No se ha podido obtener'
            self.val_audiencia['Rottentomatoes'] = 'No se ha podido obtener'
            # print(e)
            # print('Error al obtener la nota de Rotten Tomatoes')
            return None
    
    def get_nota_todas(self):
        self.get_nota_imdb()
        self.get_nota_filmaffinity()
        self.get_nota_metacritic()
        self.get_nota_rottentomatoes()
        return {
            'criticas': self.val_criticas,
            'audiencia': self.val_audiencia
        }