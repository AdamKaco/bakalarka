import recom
import numpy as np
from numpy.linalg import norm

db = recom.connect_db()

basket_class, baskets_array, customers, user_ids = recom.get_all_baskets_at_once(9000, db)
print(len(baskets_array))



#clusters = recom2.custom_basket_clusters_gpt(baskets_array)
#print(len(clusters))

#tmp1 = recom2.Clusters(baskets)

#tmp1.test()
counter1 = 0
counter2 = 0
counter3 = 0
counter4 = 0
counter5 = 0
counter6 = 0
counter7 = 0

last_baskets_nmb = 1

for k in range(9002,9902):
    #print(k)
    new_tmp, new_baskets, new_customer = recom.get_user(k, db)
    if len(new_tmp) < 10:
        continue

    best_find = recom.find_similar_customers_cust2cust(new_customer, customers, 3, user_ids)
    #print("most similar customers to input: " + str(best_find))

    recomended_user = recom.recommend_from_user(best_find[2][1], basket_class)

    try :
        last_x_baskets = recom.get_categories_from_baskets(5, recomended_user)
    except IndexError:
        continue
    #print("most bought categories vector: " + str(last_x_baskets))

    size_of_basket = 0
    for item in last_x_baskets:
        if item > 0:
            size_of_basket += 1
    size_of_basket = int(size_of_basket/3)
    #print(size_of_basket)
    
    recomended_categories = recom.most_bought_categories(last_x_baskets, size_of_basket)
    #print("most bought categories int: " + str(recomended_categories))

    bought_items = recom.get_user_most_bought_items(k , recomended_categories, db)
    
    other_users = []
    for i in range(3):
        other_users.append(best_find[i][1])
    bought_items_other = recom.get_user_most_bought_items_from_other(other_users , recomended_categories, db)
    
    recomended_items = recom.most_bought_categories(bought_items, size_of_basket)
    recomended_items_other = recom.most_bought_categories(bought_items_other, size_of_basket)
    #print("most bought items int: " + str(recomended_items))

    most_cat = [21, 24, 30, 65]
    counter_cat, all_counter = recom.category_hit_rate(recomended_categories, last_baskets_nmb, new_baskets)
    counter_cat_random, all_counter_random = recom.category_hit_rate(most_cat, last_baskets_nmb, new_baskets)
    
    most_item = [296, 593, 356, 318]
    counter_item = recom.item_hit_rate(recomended_items, size_of_basket, db, k)
    counter_item_other = recom.item_hit_rate(recomended_items_other, size_of_basket, db, k)
    counter_item_random = recom.item_hit_rate(most_item, size_of_basket, db, k)
    
    
    #print("number of hits category: " + str(counter_cat))
    #print("number of hits item: " + str(counter_item))
    #print("number of all: " + str(all_counter))
    counter1 += counter_cat
    counter2 += all_counter
    counter3 += counter_cat_random
    counter4 += all_counter_random
    counter5 += counter_item
    counter6 += counter_item_random
    counter7 += counter_item_other

    #print(counter_item)
print("number of hits category: " + str(counter1))
print("number of hits item: " + str(counter5))
print("number of hits item other: " + str(counter7))
print("number of all: " + str(counter2))

print("number of hits random cat: " + str(counter3))
print("number of hits random item: " + str(counter6))
print("number of all random: " + str(counter4))