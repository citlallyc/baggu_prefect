#!/usr/bin/env python
# coding: utf-8

# In[2]:


import requests
import re
from bs4 import BeautifulSoup
from prefect import flow, task
from prefect.tasks import task_input_hash
from datetime import timedelta
from prefect_slack import SlackWebhook
from prefect_slack.messages import send_incoming_webhook_message
# In[3]:


@task(retries = 3)
def find_baggu_price(url):
    k = requests.get(url).text
    soup = BeautifulSoup(k, 'html.parser')
    price_string = soup.find('div', {"class":"product-price"}).text
    price_string = price_string.replace(' ', '')
    price = int(re.search('[0-9]+', price_string).group(0))
    return price

@task #(cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
def compare_price(price, budget):
    if price <= budget:
        return True
       # print(f"Buy the bag, good deal!")
    else:
        return False
        #print(f"Not worth, not worth")

@flow #Using flow decorator       
def baggu_flow(url: str = "https://www.baggu.com/products/medium-nylon-crescent-bag-black", budget: int= 40):
    price = find_baggu_price(url)
    if compare_price(price, budget) == True:
        slack_webhook = SlackWebhook.load("bag")
        send_incoming_webhook_message(
            slack_webhook=slack_webhook,
            text=f"Buy the bag",
    )
    
# url = "https://www.baggu.com/products/medium-nylon-crescent-bag-black"
# budget = 75 
# baggu_flow(url, budget)

if __name__ == "__main__":
    baggu_flow.serve(name="second_deployment", cron="0 0 * * *")
