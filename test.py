num_list = {"1": True, "2": False, "3": True}
num_str = ""
for k, v in num_list.items():
    num_str += k if v else ""

print(num_str)
