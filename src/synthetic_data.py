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


def generate_enrollment_status():
    """
    Generate a sysnthetic data for 50% students enrolled and 50% students not enrolled
    """
    enrolment_options = ["enrolled", "not_enrolled"]
    enrolment_weights = [0.5, 0.5]  

    return (weighted_choice(enrolment_options, weights=enrolment_weights))

for i in range(10):
    enrolment_results = generate_enrollment_status()
    print(enrolment_results)

def generate_full_time():
    """
    Generate synthetic full time status; 50 % true and 50% false
    """
    fulltime_options = [True, False]
    fulltime_weights = [0.5, 0.5]

    return(weighted_choice(fulltime_options, weights=fulltime_weights))

for i in range(10):
    full_time_results = generate_full_time()
    print(full_time_results)






