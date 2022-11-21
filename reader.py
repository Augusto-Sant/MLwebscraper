from bs4 import BeautifulSoup
import requests
import pandas


def main():
    url = 'https://lista.mercadolivre.com.br/chtulhu-estatua#D[A:chtulhu%20estatua]'

    all_products = []
    page = 1
    for_loop = 0
    while True:
        response = requests.get(url)

        file = BeautifulSoup(response.content, 'html.parser')

        title = file.find('title')

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
            info.update({
                'Vendedor': head.contents[0] if head is not None else '',
                'Descrição': desc,
                'Preço': price.contents[0],
                'Pagina': page,
                'MLCODE': mlcode
            })

            all_products.append(info.copy())
            info.clear()
            for_loop += 1
            print(index, for_loop)

        next_page = file.find('span', class_='andes-pagination__arrow-title', string='Próxima')
        if next_page is None:
            break
        else:
            page += 1
            next_page_url = next_page.find_parent('a',
                                                  class_='andes-pagination__link shops__pagination-link ui-search-link').get(
                'href')
            url = next_page_url

    dataframe = pandas.DataFrame.from_dict(all_products)
    print(dataframe.to_markdown())
    search = ""
    while search != '0':
        print("########################")
        search = input("Pesquise uma palavra chave (0 para sair): ")
        print("########################")
        descs = list(dataframe['Descrição'].tolist())
        searched_phrases = 0
        for i, phrase in enumerate(descs):
            if search in phrase:
                print(f'{i}. {phrase}')
                searched_phrases += 1
        print(f'Total found: {searched_phrases}')


if __name__ == "__main__":
    main()
