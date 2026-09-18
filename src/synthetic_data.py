# we are writing a function that will generate synthetic data/ fake students for training purposes. 
import random
from datetime import date, timedelta
from rules_engine import parse_iso_date

def weighted_choice(options, weights):
     """
     pick one from a list,  respecting given weights.
     """
     result = random.choices(options, weights=weights, k=1)
     return result[0]  


# write a function that generates synthetic data based on days until end of OPT
def days_until_end_of_opt():
    """
    Generate synthetic data for days until end of OPT.
    """
    bucket_options = ["expired", "within_grace_period", "safe"]
    bucket_weights = [0.45, 0.35, 0.2] # because we want the model to learn how to identify expired and within grace period students more than safe students

    chosen_bucket = weighted_choice(bucket_options, bucket_weights)

    if chosen_bucket == "expired":
        result =  random.randint(-30, -1)
    elif chosen_bucket == "within_grace_period":
        result = random.randint(0, 60)
    else:
        result = random.randint(61,90)

    return {"chosen_bucket": chosen_bucket, "days": result}


for i in range(15):
    final_result = days_until_end_of_opt()
    # print(f"{final_result['chosen_bucket']} : {final_result['days']} days until end of OPT")


#  write a fuction that generates the opt date as a date based on the days until end of OPT
def generate_opt_end_date(today_str):
    """
    Generate synthetic data for OPT end date based on days until end of OPT.
    """
    today_date = parse_iso_date(today_str, "today")
    offset_info = days_until_end_of_opt() # generate a dictionary -> {"chosen_bucket": chosen_bucket, "days": result}
    offset = timedelta(days=offset_info['days']) 
    new_date = today_date + offset
    return {"chosen_bucket": offset_info['chosen_bucket'], 
            "days": offset_info['days'],
            "opt_end_date": new_date.isoformat()}

for i in range(10):
    combined_results = generate_opt_end_date("2026-08-25")
    print(combined_results)







    