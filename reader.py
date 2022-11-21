from bs4 import BeautifulSoup
import requests
import pandas


class Scraper:
    def __init__(self, url):
        self.all_products = []
        self.title = ""
        self.pages_scraped = 1
        self.initial_url = url
        self.url = url

    def scrape(self):

        for_loop = 0
        while True:
            response = requests.get(self.url)

            file = BeautifulSoup(response.content, 'html.parser')

            self.title = file.find('title')

            div = file.find_all('div',
                                class_="andes-card andes-card--flat andes-card--default ui-search-result "
                                       + "shops__cardStyles ui-search-result--core andes-card--"
                                       + "padding-default andes-card--animated")

            for index, product in enumerate(div):
                info = {}
                head = product.find('span', string=True,
                                    class_='ui-search-item__brand-discoverability ui-search-item__group__element shops__items-group-details')
                desc = product.find('h2', string=True,
                                    class_="ui-search-item__title ui-search-item__group__element shops__items-group-details shops__item-title").contents[
                    0]
                price = product.find('span', string=True, class_="price-tag-fraction")
                try:
                    mlcode = product.find('a')['href'].split('/p/')[1].split('?')[0]
                except:
                    mlcode = product.find('a')['href'].split('MLB-')[1].split('-')[0]
                    mlcode = f"MLB{mlcode}"

                preco = self.corrigir_numeros1000(price.contents[0])
                info.update({
                    'Vendedor': head.contents[0] if head is not None else '',
                    'Descrição': desc,
                    'Preço': preco,
                    'Pagina': self.pages_scraped,
                    'MLCODE': mlcode
                })

                self.all_products.append(info.copy())
                info.clear()
                for_loop += 1
                print(index, for_loop)

            next_page = file.find('span', class_='andes-pagination__arrow-title', string='Próxima')
            if next_page is None:
                break
            else:
                self.pages_scraped += 1
                next_page_url = next_page.find_parent('a',
                                                      class_='andes-pagination__link shops__pagination-'
                                                             + 'link ui-search-link').get('href')
                self.url = next_page_url

    def create_dataframe(self):
        return pandas.DataFrame.from_dict(self.all_products)

    def corrigir_numeros1000(self, preco) -> float:
        """
        Corrige numeração 1.000 para 1000
        :return:
        """
        preco = preco.replace(".", "").replace(",", ".")
        return float(preco)


class CalculaPreco:
    def calcular_media_precos(self, data) -> float:
        """
        Calcula media dos Preços
        :return:
        """
        return data['Preço'].mean()

    def calcular_max_precos(self, data):
        """
        Calcula preço maximo
        :return:
        """
        return data['Preço'].max()

    def calcular_min_precos(self, data):
        """
        Calcula preço minimo
        :return:
        """
        return data['Preço'].min()

    def calcular_mediana_precos(self, data) -> float:
        """
        Calcula mediana dos Preços
        :return:
        """
        return data['Preço'].median()

    def calcular_faixa_precos(self, data):
        """
        Calcula diferença entre o maior e o menor preço
        :return:
        """
        return data['Preço'].max() - data['Preço'].min()


def search(dataframe, calcula_preco):
    while True:
        search_name = input("Pesquise uma palavra chave (0 para sair): ")
        if search_name == '0':
            break

        print("-" * 20)
        descs = list(dataframe['Descrição'].tolist())
        searched_phrases = 0
        products_found = []
        for i, phrase in enumerate(descs):
            if search_name in phrase:
                products_found.append(i)
                searched_phrases += 1
        new_dataframe = dataframe.iloc[products_found]
        print(new_dataframe.to_markdown())
        print("")
        print("INFORMAÇÕES SOBRE OS PREÇOS ---------------------------")
        print(f"| MEDIA: {calcula_preco.calcular_media_precos(new_dataframe):.3f}", end="| ")
        print(f"MEDIANA: {calcula_preco.calcular_mediana_precos(new_dataframe):.3f}", end="| ")
        print(f"MAXIMO: {calcula_preco.calcular_max_precos(new_dataframe):.3f}", end="| ")
        print(f"MINIMO: {calcula_preco.calcular_min_precos(new_dataframe):.3f}", end="| ")
        print(f"FAIXA: {calcula_preco.calcular_faixa_precos(new_dataframe):.3f}", end="|\n")
        print("-------------------------------------------------------")
        print(f'Total encontrado: {searched_phrases}')


def check_html_file():
    html_file = open('data.html', 'w')
    html_file.close()

def main():
    ##
    #OBSERVAÇÃO EXISTEM DOIS TIPOS DE LISTAGEM no MERCADO LIVRE ESSA é PARA BUSCA DENTRO DE CATEGORIA E NÃO GERAL
    ##
    url = input("URL: ")

    check_html_file()

    scraper = Scraper(url)
    scraper.scrape()
    calcula_preco = CalculaPreco()
    dataframe = scraper.create_dataframe()
    print(dataframe.to_markdown())
    dataframe.to_html(buf="data.html")
    print("")
    print("INFORMAÇÕES SOBRE OS PREÇOS ---------------------------")
    print(f"| MEDIA: {calcula_preco.calcular_media_precos(dataframe):.3f}", end="| ")
    print(f"MEDIANA: {calcula_preco.calcular_mediana_precos(dataframe):.3f}", end="| ")
    print(f"MAXIMO: {calcula_preco.calcular_max_precos(dataframe):.3f}", end="| ")
    print(f"MINIMO: {calcula_preco.calcular_min_precos(dataframe):.3f}", end="| ")
    print(f"FAIXA: {calcula_preco.calcular_faixa_precos(dataframe):.3f}", end="|\n")
    print("-------------------------------------------------------")
    print("")
    search(dataframe, calcula_preco)


if __name__ == "__main__":
    main()
