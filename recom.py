import mysql.connector
import numpy as np
from numpy.linalg import norm
import math

#pocet kategorii
category_nmb = 144
#hodnota, ktora vahuje casovu zavislost nakupov
time_const = 0.8
#zoznam kategorii, pouzitie pri transformacii na id
products_categories_dictionary = ["artif. sweetener",
"baby cosmetics"	,
"bags"	,
"baking powder"	,
"bathroom cleaner"	,
"beef"	,
"berries"	,
"beverages"	,
"bottled beer"	,
"bottled water"	,
"brandy"	,
"brown bread"	,
"butter"	,
"butter milk"	,
"candy"	,
"canned beer"	,
"canned fish"	,
"canned fruit"	,
"canned vegetables"	,
"cat food"	,
"channa"	,
"cheese"	,
"chewing gum"	,
"chicken"	,
"chocolate"	,
"chocolate marshmallow"	,
"chowmien"	,
"citrus fruit"	,
"cleaner"	,
"cling film/bags"	,
"coffee"	,
"condensed milk"	,
"cookware"	,
"cream cheese "	,
"curd"	,
"curd cheese"	,
"Dal"	,
"decalcifier"	,
"dental care"	,
"detergent"	,
"dish cleaner"	,
"dog food"	,
"domestic eggs"	,
"female sanitary products"	,
"finished products"	,
"fish"	,
"flour"	,
"frankfurter"	,
"frozen chicken"	,
"frozen fish"	,
"frozen fruits"	,
"frozen meals"	,
"frozen potato products"	,
"frozen Veg"	,
"frozen vegetables"	,
"fruit"	,
"fruit/vegetable juice"	,
"grapes"	,
"hair spray"	,
"ham"	,
"hamburger meat"	,
"hard cheese"	,
"herbs"	,
"house keeping products"	,
"hygiene articles"	,
"ice cream"	,
"instant coffee"	,
"Instant food products"	,
"kitchen towels"	,
"light bulbs"	,
"liquor"	,
"liquor (appetizer)"	,
"liver loaf"	,
"long life bakery product"	,
"maggie"	,
"margarine"	,
"mayonnaise"	,
"meat"	,
"milk"	,
"misc. beverages"	,
"mustard"	,
"napkins"	,
"newspapers"	,
"nuts/prunes"	,
"oil"	,
"onions"	,
"organic sausage"	,
"other vegetables"	,
"packaged fruit/vegetables"	,
"pasta"	,
"pastry"	,
"pet care"	,
"photo/film"	,
"pickled vegetables"	,
"pip fruit"	,
"popcorn"	,
"pork"	,
"pot plants"	,
"potato products"	,
"processed cheese"	,
"prosecco"	,
"red/blush wine"	,
"rice"	,
"roll products "	,
"rolls/buns"	,
"root vegetables"	,
"rum"	,
"salt"	,
"salty snack"	,
"sanitary pads"	,
"sauces"	,
"sausage"	,
"semi-finished bread"	,
"shopping bags"	,
"sliced cheese"	,
"snack products"	,
"soap"	,
"soda"	,
"soft cheese"	,
"soups"	,
"sparkling wine"	,
"specialty bar"	,
"specialty cheese"	,
"specialty chocolate"	,
"specialty fat"	,
"spices"	,
"spread cheese"	,
"sugar"	,
"sweet spreads"	,
"tropical fruit"	,
"turkey"	,
"UHT-milk"	,
"Veg"	,
"vegetables"	,
"vegetables juice"	,
"vinegar"	,
"waffles"	,
"water"	,
"whipped/sour cream"	,
"white bread"	,
"white wine"	,
"whole milk"	,
"yogurt"	,
"zwieback"
]

#pripojenie k lokalnej databaze
def connect_db():
  myDb = mysql.connector.connect(
    host = "localhost",
    user = "shop",
    password = "123",
    database = "shoping_history"
    )
  return myDb

class Basket:
  def __init__(self, basket, products):
    self.basketId = basket
    self.products = products

class User:
  def __init__(self, products, basketsDb, id):
    previousBasket = basketsDb[0]
    basketTmp = []
    i = 0
    baskets = []
    #naplnenie zoznamu nakupmy
    for basket in basketsDb:
      if previousBasket != basket:
        basketPush = Basket(previousbasket, basketTmp.copy())
        baskets.append(basketPush)
        basketTmp.clear()
         
      basketTmp.append(products[i])
      previousbasket = basket
      i += 1
    #ulozenie posledneho nakupu
    basketPush = Basket(previousbasket, basketTmp.copy())
    baskets.append(basketPush)
    basketTmp.clear()
    
    self.baskets = baskets
    self.userId = id
    self.similarity = 0
  
  def set_similarity(self, value):
    self.similarity = value


#nacitanie z databaze, kde max je hodnota ID uzivatela, po ktoreho sa maju nacitat udaje
def get_all_baskets_at_once(max, myDb):
  cursor = myDb.cursor()
  comm = "SELECT userId, productItem, dateInt FROM data WHERE userId < " + str(max) + " ORDER BY userId, dateInt"
  cursor.execute(comm)

  #produkty v nakupe
  products = []
  #pouzite pre specialne pripady prveho prechodu
  first = True
  #zoznam class odkazujucich na vsetky kosiky
  baskets = []
  #zoznam vsetkych kosikov
  baskets_array = []
  #vektor jedneho nakupu
  vector = [0]*category_nmb
  #vektor uzivatela, jeho produktov, ktore zakupil
  cust_vector = np.array([0.0]*category_nmb)
  #zoznam vsetkych uzivatelov
  custom_vectors = []
  i = 0
  previous_user = 0
  #slovnik nacitanych uzivatelov
  user_ids = []
  
  basket_counter = 0
  
  #spracovanie dat
  for x in cursor:
    push = False
    if first:
      previousBasket = x[2]
      previous_user = x[0]
      first = False
    #zmena kosika, ulozenie predchdzajucich hodnot a vynulovat potrebnych premennych
    if previousBasket != x[2]:
      #casova zavyslost
      cust_vector *= time_const
      basket = Basket(previous_user*1000000+basket_counter, products.copy())
      baskets.append(basket)
      baskets_array.append(vector)
      vector = [0]*category_nmb
      basket_counter += 1
      
      products.clear()
      previousBasket = x[2]
      #zmena uzivatela
      if previous_user != x[0]:
        basket_counter = 0
        push = True
    #zmena uzivatela, ulozenie predchdzajucich hodnot a vynulovat potrebnych premennych
    if push:
      user_ids.append(previous_user)
      previous_user = x[0]
      custom_vectors.append(cust_vector)
      cust_vector = np.array([0.0]*category_nmb)
    #ulozenie hodnot zo vstupu
    products.append(products_categories_dictionary.index(x[1]))
    cust_vector[products_categories_dictionary.index(x[1])] += 1
    vector[products_categories_dictionary.index(x[1])] += 1
    i += 1
  
  return baskets, baskets_array, np.array(custom_vectors), user_ids

#vypocet podobnosti na zaklade vzdialenosti
def my_similarity (x, y):
  #kosinova vzdialenost
  return np.dot(x,y)/(norm(x)*norm(y))
  #euklidovska vzdialenost
  #return np.linalg.norm(x - y)

#nacitanie jedneho uzivatela, funkcnost rovnaka ako get_all_baskets_at_once
def get_user(nmb, myDb):  
  cursor = myDb.cursor()
  comm = "SELECT dateInt, productItem FROM data WHERE userId = " + str(nmb) + " ORDER BY dateInt"
  cursor.execute(comm)

  products = []
  first = True
  baskets = []
  baskets_array = []
  vector = [0]*category_nmb
  cust_vector = np.array([0.0]*category_nmb)
  i = 0
  for x in cursor:
    if first:
      previousBasket = x[0]
      first = False
    if previousBasket != x[0]:
      cust_vector *= time_const
      basket = Basket(previousBasket, products.copy())
      baskets.append(basket)
      baskets_array.append(vector)
      vector = [0]*category_nmb
      
      products.clear()
      previousBasket = x[0]
    products.append(products_categories_dictionary.index(x[1]))
    cust_vector[products_categories_dictionary.index(x[1])] += 1
    vector[products_categories_dictionary.index(x[1])] += 1
    i += 1
  i = 0
  for item in vector:
    cust_vector[i] -= item
    i += 1
  return baskets, baskets_array, np.array(cust_vector)

#vyhladavanie najpodobnejsich uzivatelov k uzivatelovy na vstupe
def find_similar_customers_cust2cust (new_cust, customers, nmb_of_customers, user_ids):
  best = [[0, -1] for _ in range(nmb_of_customers)]

  i = 0
  for cust in customers:
    tmp = my_similarity(new_cust, cust)
    #ulozenie najlepsich hodnot
    if tmp > best[0][0]:
      best[0][1] = user_ids[i]
      best[0][0] = tmp
      best = sorted(best,key=lambda l:l[0])
      
    i += 1
  
  return best

#funkcia vrati nakupy uzivatela
def recommend_from_user(user_id, baskets):
  user_basket = []
  for basket in baskets:
    if basket.basketId//1000000 == user_id:
      user_basket.append(basket.products)
  return user_basket

#vrati cetnost zakupenia kategorii uzivatelov v nmb_of_baskets poslednych nakupov
def get_categories_from_baskets(nmb_of_baskets, baskets):
  category = [0]*category_nmb
  for i in range(nmb_of_baskets):
    for item in baskets[-i-1]:
      category[item] += 1
  return category

#vrati najviac zakupene kategorie zo zoznamu
def most_bought_categories(categories, nmb_of_categories):
  max_array =[]
  for i in range(nmb_of_categories):  
    max_value = max(categories)
    max_index = categories.index(max_value)
    max_array.append(max_index)
    categories[max_index] = 0
  return max_array

#vrati najviac zakupene produkty zo zoznamu pre uzivatela na vstupe
def get_user_most_bought_items(user_id, categories, myDb):
  cursor = myDb.cursor()
  items = [0]*176271
  for cat in categories:  
    comm = "SELECT productId FROM data WHERE userId = " + str(user_id) + " AND productItem = \"" + str(products_categories_dictionary[cat]) + "\""
    cursor.execute(comm)
    for x in cursor:
      items[x[0]] +=1
  return items

#vrati najviac zakupene produkty zo zoznamu pre najpodobnejsich uzivatelov
def get_user_most_bought_items_from_other(user_ids, categories, myDb):
  cursor = myDb.cursor()
  items = [0]*176271
  for user_id in user_ids:
    for cat in categories:  
      comm = "SELECT productId FROM data WHERE userId = " + str(user_id) + " AND productItem = \"" + str(products_categories_dictionary[cat]) + "\""
      cursor.execute(comm)
      for x in cursor:
        items[x[0]] +=1
  return items
  
#kontrola presnosti predpovede
def category_hit_rate(categories, nmb_of_last_baskets, baskets):
  counter = 0
  size = 0
  for i in range(nmb_of_last_baskets):  
    for x in baskets[-i-1]:
      if x != 0:
        size += 1
    for j in categories:
      if baskets[-i-1][j] != 0:
        counter += 1
  return counter, size

#kontrola presnosti predpovede
def item_hit_rate(items, nmb_of_last_items, myDb, user_id):
  cursor = myDb.cursor()
  comm = "SELECT productId FROM data WHERE userId = " + str(user_id) + " ORDER BY dateInt"
  cursor.execute(comm)
  
  items_all = []
  
  for x in cursor:
    items_all.append(x[0])

  
  counter = 0
  for i in range(nmb_of_last_items):  
    for j in items:
      if items_all[-i-1] == j:
        counter += 1
  return counter


