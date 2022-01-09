import logging
import requests
from bs4 import BeautifulSoup
from processor.utils import get_product_name_from_url
from service.const import *


def send_web_request(url: str):
    """
    Sends a web request to Scrapingbee to fetch the page
    at the given url.
    :param url: the url to scrape.
    :return: the scraped page
    """
    try:
        response = requests.get(
            url=SCRAPINGBEE_URL,
            params={
                'api_key': SCRAPINGBEE_KEY,
                'url': url,
            },
        )
    except Exception as e:
        logging.error("Cannot scrape webpage: " + str(e))
        return None

    status_code = response.status_code
    if status_code < 200 or status_code >= 300:
        logging.error("Invalid status code")
        return None
    return response.content.decode("utf-8")


def get_product_meta(page: str) -> dict:
    """
    Given an Amazon product web page,
    extracts and returns product MetaData
    :param page: the web page to parse
    :return: a MetaData dictionary
    """
    soup = BeautifulSoup(page, 'html.parser')

    # Find title
    try:
        title = soup.find("span", attrs={"id": 'productTitle'})
        title_value = title.string
        title_string = title_value.strip()
    except Exception as e:
        title_string = ""

    # Find global rating
    try:
        glb_rating = soup.find("span", attrs={"class": 'reviewCountTextLinkedHistogram noUnderline'}, title=True)
        glb_rating = glb_rating['title'].strip()
        glb_rating_value = float(glb_rating.split()[0].strip())
    except Exception as e:
        glb_rating_value = 0

    # Find num ratings
    try:
        num_rating = soup.find("span", attrs={"id": 'acrCustomerReviewText'}).text
        num_rating = num_rating.strip().split()[0].strip()
        glb_num_rating = num_rating
    except Exception as e:
        glb_num_rating = ""

    # Find price
    try:
        price = soup.find("span", attrs={'id': 'newBuyBoxPrice'}).string.strip()
    except Exception as e:
        price = ""

    if not price:
        # Try something else
        try:
            price = soup.find("span", attrs={'class': 'a-offscreen'}).string.strip()
        except Exception as e:
            price = ""

    # Find image
    try:
        image_wrapper = soup.find("div", attrs={'class': "imgTagWrapper"})
        tag_wrapper = image_wrapper.find("img", src=True)
        image = tag_wrapper['src']
    except Exception as e:
        image = ""

    if not image:
        # Try something else
        try:
            image_wrapper = soup.find("div", attrs={'id': "mainImageContainer"})
            tag_wrapper = image_wrapper.find("img", src=True)
            image = tag_wrapper['src']
        except Exception as e:
            image = ""

    meta = dict()
    meta['title'] = title_string
    meta['price'] = price
    meta['image'] = image
    meta['glb_rating'] = glb_rating_value
    meta['glb_num_ratings'] = glb_num_rating
    return meta


def get_review_url_link_list(page: str):
    """
    Given an Amazon product page, returns the urls pointing
    to the review pages.
    :param page: an Amazon product page
    :return: the list of urls pointing at the reviews.
    Note: usually it's only 1 url.
    """
    soup = BeautifulSoup(page, 'html.parser')
    rev_url_list = soup.find_all('a', attrs={'class': 'a-link-emphasis a-text-bold'}, href=True)

    review_link_set = set()
    for rev_url in rev_url_list:
        url = rev_url['href'].strip()
        if rev_url.text == 'See all reviews':
            review_link_set.add(url)
    return list(review_link_set)


def get_review_list_from_url(url: str):
    """
    Scrape the page containing reviews.
    :param url: the url of the review page to scrape.
    :return: a pair (list of reviews, scraped page)
    """
    # Scrape the page
    page = send_web_request(url)

    # file_path = 'data/page_review.html'
    # save_page_to_file(page, file_path)
    # page = load_page_from_file(file_path)
    soup = BeautifulSoup(page, 'html.parser')
    all_reviews_list = soup.find_all("div", class_='a-section review aok-relative')

    review_list = list()
    for review_card in all_reviews_list:
        review_map = dict()

        # Find title
        try:
            title_div = review_card.find("div", class_='a-row')
            title_div = review_card.find(
                "a", class_='a-size-base a-link-normal review-title a-color-base review-title-content a-text-bold')
            title_text = title_div.find("span").text
        except:
            title_text = ""

        title_text = title_text.strip()
        review_map['title'] = title_text

        # Find rating
        try:
            rating = review_card.find("span", attrs={'class': 'a-icon-alt'}).string.strip()
        except:
            rating = ""

        rating = rating.strip()
        review_map['rating'] = rating

        # Find review text
        try:
            review_span = review_card.find("span", attrs={'class': 'a-size-base review-text review-text-content'})
            review_text = review_span.find("span").text
        except:
            review_text = ""

        review_text = review_text.replace('\n', ' ')
        review_text = review_text.replace('  ', ' ')
        review_text = review_text.strip()
        review_map['review'] = review_text.strip()

        # Add review to the list
        review_list.append(review_map)

    return review_list, page


def get_next_review_url_from_page(page: str):
    """
    Given an Amazon review page, extracts the url
    of the following review page.
    :param page: an Amazon review page.
    :return: the url of the next review page
    """
    soup = BeautifulSoup(page, 'html.parser')
    review_links = soup.find_all("a", href=True)
    for review_link in review_links:
        href_link = review_link['href']
        if "reviewerType=all_reviews" in href_link and "pageNumber" in href_link:
            return review_link['href']
    return ""


def spider_scrape_review_page(review_url, num_review_pages: int = 0, base_amz_url: str = AMAZON_BASE_URL):
    """
    Scrapes an Amazon review page to extracts reviews for a given product.
    Note that this is done recursively since each review page points to
    the next one.
    :param review_url: the url containing reviews.
    :param num_review_pages: number of review pages to scrape.
    Note: each page points to the next one.
    :param base_amz_url: base Amazon url.
    :return: a list of scraped reviews
    """
    full_review_url = base_amz_url + review_url
    review_list, page = get_review_list_from_url(full_review_url)
    if num_review_pages > 0:
        # Recursively fetch reviews
        next_review_url = get_next_review_url_from_page(page)
        num_review_pages -= 1
        if next_review_url:
            review_list += spider_scrape_review_page(next_review_url, num_review_pages, base_amz_url)
    return review_list


def spider_scrape(url: str, num_review_pages: int = 1, base_amz_url: str = AMAZON_BASE_URL) -> dict:
    """
    Scrapes an Amazon product given its url.
    :param url: the url of the product on Amazon.
    :param num_review_pages: number of review pages to scrape.
    :param base_amz_url: base Amazon url
    :return: a map of MetaData from the scraped product
    """
    # Get product name
    product_name = get_product_name_from_url(url)

    # Get the page of the item in order to get the link to the reviews
    page = send_web_request(url)

    # file_path = 'data/page_sneakers.html'
    # save_page_to_file(page, file_path)
    # page = load_page_from_file(file_path)

    # Get the image url
    product_meta = get_product_meta(page)

    # Get the review links
    num_review_pages -= 1
    review_url_list = get_review_url_link_list(page)

    # For each review link, get the reviews
    reviews_list = list()
    if review_url_list:
        reviews_list = spider_scrape_review_page(review_url_list[0], num_review_pages, base_amz_url)

    product_map = dict()
    product_map['meta'] = product_meta
    product_map['reviews'] = reviews_list

    return product_map
