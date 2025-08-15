def hyy.print_lol(the_list,level=0):

    for each_item in the_list:
        if isinstance(the_list,list):
            hyy.print_lol(each_item,level+1)
        else:
            for num in range(level):
                print("\t,end=""")
            print(each_item)