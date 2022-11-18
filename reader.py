from bs4 import BeautifulSoup
import requests
import pandas


def main():
    url = input("URL DO PRODUTO MERCADO LIVRE: ")

    all_products = []
    page = 1
    while True:
        response = requests.get(url)

        file = BeautifulSoup(response.content,'html.parser')

        title = file.find('title')

        div = file.find_all('div',class_="ui-search-result__content-wrapper shops__result-content-wrapper")
        
        for product in div:
            info = {}
            head = product.find('span',string=True,class_='ui-search-item__brand-discoverability ui-search-item__group__element shops__items-group-details')
            desc = product.find('h2',string=True,class_="ui-search-item__title ui-search-item__group__element shops__items-group-details shops__item-title")
            price = product.find('span',string=True,class_="price-tag-fraction")
            info.update({
                'Vendedor':head.contents[0] if head!=None else '',
                'Descrição':desc.contents[0],
                'Preço':price.contents[0],
                'Pagina':page
            })
            
            all_products.append(info.copy())
            info.clear()

        next_page = file.find('span',class_='andes-pagination__arrow-title',string='Próxima')
        if next_page == None:
            break
        else:
            page += 1
            next_page_url = next_page.find_parent('a',class_='andes-pagination__link shops__pagination-link ui-search-link').get('href')
            url = next_page_url

    dataframe = pandas.DataFrame.from_dict(all_products)
    print(dataframe)
    search = ""
    while search != '0':
        print("########################")
        search = input("Pesquise uma palavra chave (0 para sair): ")
        print("########################")
        descs = list(dataframe['Descrição'].tolist())
        for phrase in descs:
            if search in phrase:
                print(phrase)


if __name__ == "__main__":
    main()